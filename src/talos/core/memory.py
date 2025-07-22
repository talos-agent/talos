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
    """

    def __init__(
        self,
        file_path: Path,
        embeddings_model: Embeddings,
        history_file_path: Optional[Path] = None,
    ):
        self.file_path = file_path
        self.history_file_path = history_file_path
        self.embeddings_model = embeddings_model
        self.memories: List[MemoryRecord] = []
        self.index: Optional[IndexFlatL2] = None
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
        embedding = self.embeddings_model.embed_query(description)
        memory = MemoryRecord(
            timestamp=time.time(),
            description=description,
            metadata=metadata or {},
            embedding=embedding,
        )
        self.memories.append(memory)
        if self.index is None:
            self.index = IndexFlatL2(len(embedding))
        self.index.add(np.array([embedding], dtype=np.float32))
        self._save()

    def search(self, query: str, k: int = 5) -> List[MemoryRecord]:
        if not self.index or not self.memories:
            return []
        query_embedding = self.embeddings_model.embed_query(query)
        distances, indices = self.index.search(np.array([query_embedding], dtype=np.float32), k)
        return [self.memories[i] for i in indices[0]]

    def load_history(self) -> List[BaseMessage]:
        if not self.history_file_path or not self.history_file_path.exists():
            return []
        with open(self.history_file_path, "r") as f:
            dicts = json.load(f)
        return messages_from_dict(dicts)

    def save_history(self, messages: List[BaseMessage]):
        if not self.history_file_path:
            return
        if not self.history_file_path.exists():
            self.history_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.history_file_path.touch()
        dicts = messages_to_dict(messages)
        with open(self.history_file_path, "w") as f:
            json.dump(dicts, f, indent=4)
