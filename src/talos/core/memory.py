import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Any, Union

from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict

if TYPE_CHECKING:
    from langgraph.store.memory import InMemoryStore
    from langmem import create_memory_store_manager, create_memory_manager

try:
    from langgraph.store.memory import InMemoryStore
    from langmem import create_memory_store_manager, create_memory_manager
    LANGMEM_AVAILABLE = True
except ImportError:
    InMemoryStore = Any  # type: ignore
    create_memory_store_manager = Any  # type: ignore
    create_memory_manager = Any  # type: ignore
    LANGMEM_AVAILABLE = False


@dataclass
class MemoryRecord:
    timestamp: float
    description: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None


class Memory:
    """
    A class to handle the saving and loading of an agent's memories using LangMem.
    Supports both SQLite (default) and file-based backends.
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
        use_database: bool = True,
        verbose: Union[bool, int] = False,
        similarity_threshold: float = 0.85,
    ):
        self.file_path = file_path
        self.history_file_path = history_file_path
        self.embeddings_model = embeddings_model
        self.batch_size = batch_size
        self.auto_save = auto_save
        self.user_id = user_id
        self.session_id = session_id or "default-session"
        self.use_database = use_database
        self.verbose = verbose
        self.similarity_threshold = similarity_threshold
        self.memories: List[MemoryRecord] = []
        self._unsaved_count = 0
        self._langmem_manager = None
        self._store = None
        self._db_backend = None
        
        if self.use_database and LANGMEM_AVAILABLE and self.embeddings_model:
            self._setup_langmem_sqlite()
        elif self.use_database and self.user_id and self.embeddings_model:
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
            self._setup_langmem_file()
        else:
            if self.file_path:
                self._setup_langmem_file()

    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))

    def _setup_langmem_sqlite(self):
        """Setup LangMem with SQLite backend."""
        if not LANGMEM_AVAILABLE:
            if self._get_verbose_level() >= 1:
                print("⚠ LangMem not available, falling back to database backend")
            if self.user_id and self.embeddings_model:
                from ..database.memory_backend import DatabaseMemoryBackend
                self._db_backend = DatabaseMemoryBackend(
                    user_id=self.user_id,
                    embeddings_model=self.embeddings_model,
                    session_id=self.session_id,
                    auto_save=self.auto_save,
                    verbose=self.verbose,
                    similarity_threshold=self.similarity_threshold
                )
            return
            
        try:
            self._store = InMemoryStore(
                index={
                    "dims": 1536,
                    "embed": "openai:text-embedding-3-small"
                }
            )
            
            self._langmem_manager = create_memory_store_manager(
                "gpt-4o",
                namespace=("memories", self.user_id or "default"),
                store=self._store
            )
            
            if self._get_verbose_level() >= 1:
                print("✓ LangMem initialized with SQLite backend")
        except Exception as e:
            if self._get_verbose_level() >= 1:
                print(f"⚠ SQLite setup failed, falling back to database backend: {e}")
            if self.user_id and self.embeddings_model:
                from ..database.memory_backend import DatabaseMemoryBackend
                self._db_backend = DatabaseMemoryBackend(
                    user_id=self.user_id,
                    embeddings_model=self.embeddings_model,
                    session_id=self.session_id,
                    auto_save=self.auto_save,
                    verbose=self.verbose,
                    similarity_threshold=self.similarity_threshold
                )

    def _setup_langmem_file(self):
        """Setup LangMem with file-based backend."""
        if not LANGMEM_AVAILABLE:
            if self._get_verbose_level() >= 1:
                print("⚠ LangMem not available, using file-only storage")
            if self.file_path:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                if not self.file_path.exists():
                    self.file_path.write_text("[]")
                self._load_file_memories()
            return
            
        try:
            self._langmem_manager = create_memory_manager("gpt-4o")
            if self.file_path:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                if not self.file_path.exists():
                    self.file_path.write_text("[]")
                self._load_file_memories()
            
            if self._get_verbose_level() >= 1:
                print("✓ LangMem initialized with file backend")
        except Exception as e:
            if self._get_verbose_level() >= 1:
                print(f"✗ LangMem setup failed: {e}")
            if self.file_path:
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                if not self.file_path.exists():
                    self.file_path.write_text("[]")
                self._load_file_memories()

    def _load_file_memories(self):
        """Load existing memories from file."""
        if self.file_path and self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.memories = [MemoryRecord(**d) for d in data]
            except Exception as e:
                if self._get_verbose_level() >= 1:
                    print(f"⚠ Failed to load memories: {e}")

    async def add_memory_async(self, description: str, metadata: Optional[dict] = None):
        """Add a memory using LangMem."""
        if self._langmem_manager and self._store:
            try:
                config = {"configurable": {"langgraph_user_id": self.user_id or "default"}}
                conversation = [{"role": "user", "content": description}]
                await self._langmem_manager.ainvoke({"messages": conversation}, config=config)
                
                if self._get_verbose_level() >= 1:
                    print(f"✓ Memory saved: {description}")
            except Exception as e:
                if self._get_verbose_level() >= 1:
                    print(f"✗ Failed to save memory: {e}")
        elif self._langmem_manager:
            try:
                conversation = [{"role": "user", "content": description}]
                await self._langmem_manager.ainvoke({"messages": conversation})
                
                memory = MemoryRecord(
                    timestamp=time.time(),
                    description=description,
                    metadata=metadata or {},
                )
                self.memories.append(memory)
                self._unsaved_count += 1
                
                if self.auto_save and self._unsaved_count >= self.batch_size:
                    self.flush()
                
                if self._get_verbose_level() >= 1:
                    print(f"✓ Memory saved: {description}")
            except Exception as e:
                if self._get_verbose_level() >= 1:
                    print(f"✗ Failed to save memory: {e}")
        elif self._db_backend:
            self._db_backend.add_memory(description, metadata)
        else:
            memory = MemoryRecord(
                timestamp=time.time(),
                description=description,
                metadata=metadata or {},
            )
            self.memories.append(memory)
            self._unsaved_count += 1
            
            if self.auto_save and self._unsaved_count >= self.batch_size:
                self.flush()
            
            if self._get_verbose_level() >= 1:
                print(f"✓ Memory saved (fallback): {description}")

    def add_memory(self, description: str, metadata: Optional[dict] = None):
        """Add memory with backward compatibility."""
        if self._db_backend:
            self._db_backend.add_memory(description, metadata)
            return
            
        if self._langmem_manager and self._store:
            try:
                config = {"configurable": {"langgraph_user_id": self.user_id or "default"}}
                conversation = [{"role": "user", "content": description}]
                self._langmem_manager.invoke({"messages": conversation}, config=config)
                
                if self._get_verbose_level() >= 1:
                    print(f"✓ Memory saved to LangMem store: {description}")
            except Exception as e:
                if self._get_verbose_level() >= 1:
                    print(f"✗ LangMem store failed, using fallback: {e}")
                memory = MemoryRecord(
                    timestamp=time.time(),
                    description=description,
                    metadata=metadata or {},
                )
                self.memories.append(memory)
                self._unsaved_count += 1
                
                if self.auto_save and self._unsaved_count >= self.batch_size:
                    self.flush()
        elif self._langmem_manager:
            try:
                conversation = [{"role": "user", "content": description}]
                self._langmem_manager.invoke({"messages": conversation})
                
                memory = MemoryRecord(
                    timestamp=time.time(),
                    description=description,
                    metadata=metadata or {},
                )
                self.memories.append(memory)
                self._unsaved_count += 1
                
                if self.auto_save and self._unsaved_count >= self.batch_size:
                    self.flush()
                
                if self._get_verbose_level() >= 1:
                    print(f"✓ Memory saved to LangMem: {description}")
            except Exception as e:
                if self._get_verbose_level() >= 1:
                    print(f"✗ LangMem failed, using fallback: {e}")
                memory = MemoryRecord(
                    timestamp=time.time(),
                    description=description,
                    metadata=metadata or {},
                )
                self.memories.append(memory)
                self._unsaved_count += 1
                
                if self.auto_save and self._unsaved_count >= self.batch_size:
                    self.flush()
        else:
            memory = MemoryRecord(
                timestamp=time.time(),
                description=description,
                metadata=metadata or {},
            )
            self.memories.append(memory)
            self._unsaved_count += 1
            
            if self.auto_save and self._unsaved_count >= self.batch_size:
                self.flush()
            
            if self._get_verbose_level() >= 1:
                print(f"✓ Memory saved (fallback): {description}")

    async def search_async(self, query: str, k: int = 5) -> List[MemoryRecord]:
        """Search memories using LangMem."""
        if self._langmem_manager and self._store:
            try:
                config = {"configurable": {"langgraph_user_id": self.user_id or "default"}}
                results = await self._langmem_manager.asearch(query=query, config=config)
                
                memory_records = []
                for result in results[:k]:
                    memory_records.append(MemoryRecord(
                        timestamp=time.time(),
                        description=str(result),
                        metadata={},
                    ))
                
                verbose_level = self._get_verbose_level()
                if verbose_level >= 1 and memory_records:
                    print(f"🔍 Memory search: found {len(memory_records)} relevant memories")
                    if verbose_level >= 2:
                        for i, memory in enumerate(memory_records, 1):
                            print(f"  {i}. {memory.description}")
                            if memory.metadata:
                                print(f"     Metadata: {memory.metadata}")
                
                return memory_records
            except Exception as e:
                verbose_level = self._get_verbose_level()
                if verbose_level >= 1:
                    print(f"✗ Search failed: {e}")
                    if verbose_level >= 2:
                        print(f"  Error details: {str(e)}")
                        print(f"  Query: {query}")
                return []
        else:
            if not self.memories:
                return []
            
            results = []
            query_lower = query.lower()
            for memory in self.memories:
                if query_lower in memory.description.lower():
                    results.append(memory)
            
            return results[:k]

    def search(self, query: str, k: int = 5) -> List[MemoryRecord]:
        """Search with backward compatibility."""
        if self._db_backend:
            return self._db_backend.search_memories(query, k)
            
        import asyncio
        try:
            return asyncio.run(self.search_async(query, k))
        except Exception:
            return []

    def list_all(self, filter_user_id: Optional[str] = None) -> List[MemoryRecord]:
        """List all memories."""
        if self._db_backend:
            results = self._db_backend.list_all_memories(filter_user_id)
            verbose_level = self._get_verbose_level()
            if verbose_level >= 1 and results:
                print(f"📋 Listed {len(results)} memories")
                if verbose_level >= 2:
                    for i, memory in enumerate(results[:5], 1):
                        print(f"  {i}. {memory.description}")
                        if memory.metadata:
                            print(f"     Metadata: {memory.metadata}")
                    if len(results) > 5:
                        print(f"  ... and {len(results) - 5} more memories")
            return results
        elif self._store:
            if self._get_verbose_level() >= 1:
                print("📋 Listed memories from SQLite store")
            return []
        else:
            results = self.memories.copy()
            results.sort(key=lambda x: x.timestamp, reverse=True)
            verbose_level = self._get_verbose_level()
            if verbose_level >= 1 and results:
                print(f"📋 Listed {len(results)} memories")
                if verbose_level >= 2:
                    for i, memory in enumerate(results[:5], 1):
                        print(f"  {i}. {memory.description}")
                        if memory.metadata:
                            print(f"     Metadata: {memory.metadata}")
                    if len(results) > 5:
                        print(f"  ... and {len(results) - 5} more memories")
            return results

    def load_history(self) -> List[BaseMessage]:
        """Load conversation history."""
        if self._db_backend:
            return self._db_backend.load_history()
            
        if not self.history_file_path or not self.history_file_path.exists():
            return []
        try:
            with open(self.history_file_path, "r") as f:
                dicts = json.load(f)
            return messages_from_dict(dicts)
        except Exception:
            return []

    def save_history(self, messages: List[BaseMessage]):
        """Save conversation history."""
        if self._db_backend:
            self._db_backend.save_history(messages)
            return
            
        if not self.history_file_path:
            return
        try:
            if not self.history_file_path.exists():
                self.history_file_path.parent.mkdir(parents=True, exist_ok=True)
                self.history_file_path.touch()
            dicts = messages_to_dict(messages)
            with open(self.history_file_path, "w") as f:
                json.dump(dicts, f, indent=4)
        except Exception as e:
            verbose_level = self._get_verbose_level()
            if verbose_level >= 1:
                print(f"⚠ Failed to save history: {e}")
                if verbose_level >= 2:
                    print(f"  Error details: {str(e)}")
                    print(f"  History file: {self.history_file_path}")

    def flush(self):
        """Manually save all unsaved memories to disk."""
        if self._unsaved_count > 0 and self.file_path:
            try:
                with open(self.file_path, "w") as f:
                    json.dump([m.__dict__ for m in self.memories], f, indent=4)
                self._unsaved_count = 0
            except Exception as e:
                verbose_level = self._get_verbose_level()
                if verbose_level >= 1:
                    print(f"⚠ Failed to flush memories: {e}")
                    if verbose_level >= 2:
                        print(f"  Error details: {str(e)}")
                        print(f"  Memory file: {self.file_path}")

    def __del__(self):
        """Ensure data is saved when object is destroyed."""
        if hasattr(self, "_unsaved_count") and self._unsaved_count > 0:
            self.flush()
