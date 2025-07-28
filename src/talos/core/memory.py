import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np
from faiss import IndexFlatL2, read_index, write_index
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict


@dataclass
class MemoryRecord:
    timestamp: float
    description: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class Memory:
    """
    A class to handle the saving and loading of an agent's memories.
    Supports both file-based and database-based backends.
    """

    def __init__(
        self,
        file_path: Optional[Path] = None,
        embeddings_model: Optional[Embeddings] = None,
        history_file_path: Optional[Path] = None,
        batch_size: int = 10,
        auto_save: bool = True,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        use_database: bool = False,
        verbose: bool = False,
        similarity_threshold: float = 0.85,
    ):
        self.file_path = file_path
        self.history_file_path = history_file_path
        self.embeddings_model = embeddings_model
        self.batch_size = batch_size
        self.auto_save = auto_save
        self.user_id = user_id
        self.session_id = session_id
        self.use_database = use_database
        self.verbose = verbose
        self.similarity_threshold = similarity_threshold
        self.memories: List[MemoryRecord] = []
        self.index: Optional[IndexFlatL2] = None
        self._unsaved_count = 0
        self._db_backend = None
        
        if self.use_database and self.user_id and self.embeddings_model:
            from ..database.memory_backend import DatabaseMemoryBackend
            self._db_backend = DatabaseMemoryBackend(
                user_id=self.user_id,
                embeddings_model=self.embeddings_model,
                session_id=self.session_id,
                auto_save=self.auto_save,
                verbose=self.verbose,
                similarity_threshold=self.similarity_threshold
            )
        elif not self.use_database and self.file_path:
            self._load()

    def _load(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.memories = [MemoryRecord(**d) for d in data]
            index_path = self.file_path.with_suffix(".index")
            if index_path.exists():
                self.index = read_index(str(index_path))
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.touch()
            self.file_path.write_text("[]")

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump([m.__dict__ for m in self.memories], f, indent=4)
        if self.index:
            write_index(self.index, str(self.file_path.with_suffix(".index")))

    def add_memory(self, description: str, metadata: Optional[dict] = None):
        if self._db_backend:
            self._db_backend.add_memory(description, metadata)
            return
        
        if not self.embeddings_model:
            raise ValueError("Embeddings model is required for file-based memory")
            
        embedding = self.embeddings_model.embed_query(description)
        
        similar_memory = self._find_similar_memory(embedding, description)
        if similar_memory:
            self._merge_memories(similar_memory, description, metadata or {})
            return
        
        memory = MemoryRecord(
            timestamp=time.time(),
            description=description,
            metadata=metadata or {},
            embedding=embedding,
        )
        self.memories.append(memory)
        if self.verbose:
            print(f"\033[32m✓ Memory saved: {description}\033[0m")
        if self.index is None:
            self.index = IndexFlatL2(len(embedding))

        assert self.index is not None
        self.index.add(np.array([embedding], dtype=np.float32))
        self._unsaved_count += 1

        if self.auto_save and self._unsaved_count >= self.batch_size:
            self.flush()

    def search(self, query: str, k: int = 5) -> List[MemoryRecord]:
        if self._db_backend:
            results = self._db_backend.search_memories(query, k)
            return results
        
        if not self.index or not self.memories or not self.embeddings_model:
            return []
        query_embedding = self.embeddings_model.embed_query(query)
        distances, indices = self.index.search(np.array([query_embedding], dtype=np.float32), k)
        results = [self.memories[i] for i in indices[0]]
        if self.verbose and results:
            print(f"\033[34m🔍 Memory search: found {len(results)} relevant memories\033[0m")
        return results

    def list_all(self, filter_user_id: Optional[str] = None) -> List[MemoryRecord]:
        """List all memories, optionally filtered by user."""
        if self._db_backend:
            results = self._db_backend.list_all_memories(filter_user_id)
            if self.verbose and results:
                print(f"\033[34m📋 Listed {len(results)} memories\033[0m")
            return results
        
        if filter_user_id and self.verbose:
            print("\033[33m⚠️ User filtering not supported in file-based memory backend\033[0m")
        
        results = self.memories.copy()
        results.sort(key=lambda x: x.timestamp, reverse=True)
        if self.verbose and results:
            print(f"\033[34m📋 Listed {len(results)} memories\033[0m")
        return results

    def load_history(self) -> List[BaseMessage]:
        if self._db_backend:
            return self._db_backend.load_history()
        
        if not self.history_file_path or not self.history_file_path.exists():
            return []
        with open(self.history_file_path, "r") as f:
            dicts = json.load(f)
        return messages_from_dict(dicts)

    def save_history(self, messages: List[BaseMessage]):
        if self._db_backend:
            self._db_backend.save_history(messages)
            return
        
        if not self.history_file_path:
            return
        if not self.history_file_path.exists():
            self.history_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_file_path.touch()
        dicts = messages_to_dict(messages)
        with open(self.history_file_path, "w") as f:
            json.dump(dicts, f, indent=4)

    def _find_similar_memory(self, embedding: List[float], description: str) -> Optional[MemoryRecord]:
        """Find a similar memory based on embedding similarity and description."""
        if not self.memories or not self.index:
            return None
        
        distances, indices = self.index.search(np.array([embedding], dtype=np.float32), k=min(5, len(self.memories)))
        
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.memories):
                candidate = self.memories[idx]
                similarity = 1 / (1 + distance)
                
                if candidate.description.strip().lower() == description.strip().lower():
                    return candidate
                
                if similarity >= self.similarity_threshold:
                    return candidate
        
        return None
    
    def _merge_memories(self, existing_memory: MemoryRecord, new_description: str, new_metadata: dict):
        """Merge a new memory with an existing similar memory."""
        if existing_memory.description.strip().lower() == new_description.strip().lower():
            existing_memory.metadata.update(new_metadata)
            existing_memory.timestamp = time.time()
            if self.verbose:
                print(f"\033[33m⚡ Memory updated (duplicate): {new_description}\033[0m")
        else:
            from ..utils.memory_combiner import MemoryCombiner
            combiner = MemoryCombiner(verbose=self.verbose)
            combined_description = combiner.combine_memories(existing_memory.description, new_description)
            existing_memory.description = combined_description
            existing_memory.metadata.update(new_metadata)
            existing_memory.timestamp = time.time()
            if self.verbose:
                print(f"\033[33m⚡ Memory merged (LLM): {combined_description}\033[0m")
        
        self._unsaved_count += 1
        if self.auto_save and self._unsaved_count >= self.batch_size:
            self.flush()

    def flush(self):
        """Manually save all unsaved memories to disk."""
        if self._unsaved_count > 0:
            self._save()
            self._unsaved_count = 0

    def __del__(self):
        """Ensure data is saved when object is destroyed."""
        if hasattr(self, "_unsaved_count") and self._unsaved_count > 0:
            self.flush()
