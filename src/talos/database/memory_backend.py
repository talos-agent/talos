import warnings
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

from .models import User, ConversationHistory, Message, Memory as MemoryModel
from .session import get_session
from ..core.memory import MemoryRecord

warnings.warn(
    "DatabaseMemoryBackend is deprecated. Use Memory class with use_database=True for SQLite via LangMem.",
    DeprecationWarning,
    stacklevel=2
)


class DatabaseMemoryBackend:
    """Database-backed memory implementation using SQLAlchemy."""
    
    def __init__(
        self,
        user_id: str,
        embeddings_model: Embeddings,
        session_id: Optional[str] = None,
        auto_save: bool = True,
        verbose: bool = False,
        similarity_threshold: float = 0.85,
    ):
        self.user_id = user_id
        self.embeddings_model = embeddings_model
        self.session_id = session_id or str(uuid.uuid4())
        self.auto_save = auto_save
        self.verbose = verbose
        self.similarity_threshold = similarity_threshold
        self._ensure_user_exists()
        self._ensure_conversation_exists()
    
    def _ensure_user_exists(self) -> User:
        """Ensure user exists in database, create if not."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if not user:
                is_temp = len(self.user_id) == 36 and self.user_id.count('-') == 4
                user = User(user_id=self.user_id, is_temporary=is_temp)
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                user.last_active = datetime.now()
                session.commit()
            return user
    
    def _ensure_conversation_exists(self) -> ConversationHistory:
        """Ensure conversation exists in database, create if not."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
                
            conversation = session.query(ConversationHistory).filter(
                ConversationHistory.user_id == user.id,
                ConversationHistory.session_id == self.session_id
            ).first()
            
            if not conversation:
                conversation = ConversationHistory(
                    user_id=user.id,
                    session_id=self.session_id
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
            return conversation
    
    def add_memory(self, description: str, metadata: Optional[dict] = None) -> None:
        """Add a memory to the database."""
        embedding = self.embeddings_model.embed_query(description)
        
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
            
            similar_memory = self._find_similar_memory(session, user.id, embedding, description)
            if similar_memory:
                self._merge_memories(session, similar_memory, description, metadata or {})
                return
                
            memory = MemoryModel(
                user_id=user.id,
                description=description,
                memory_metadata=metadata or {},
                embedding=embedding,
                timestamp=datetime.now()
            )
            session.add(memory)
            session.commit()
            if self.verbose:
                print(f"\033[32m✓ Memory saved: {description}\033[0m")
    
    def search_memories(self, query: str, k: int = 5) -> List[MemoryRecord]:
        """Search memories using semantic similarity."""
        query_embedding = self.embeddings_model.embed_query(query)
        
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
                
            memories = session.query(MemoryModel).filter(MemoryModel.user_id == user.id).all()
            
            if not memories:
                return []
            
            similarities = []
            for memory in memories:
                if memory.embedding:
                    similarity = sum(a * b for a, b in zip(query_embedding, memory.embedding))
                    similarities.append((similarity, memory))
            
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_memories = similarities[:k]
            
            results = [
                MemoryRecord(
                    timestamp=memory.timestamp.timestamp(),
                    description=memory.description,
                    metadata=memory.memory_metadata or {},
                    embedding=memory.embedding
                )
                for _, memory in top_memories
            ]
            if self.verbose and results:
                print(f"\033[34m🔍 Memory search: found {len(results)} relevant memories\033[0m")
            return results
    
    def load_history(self) -> List[BaseMessage]:
        """Load conversation history from database."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
                
            conversation = session.query(ConversationHistory).filter(
                ConversationHistory.user_id == user.id,
                ConversationHistory.session_id == self.session_id
            ).first()
            
            if not conversation:
                return []
            
            messages = session.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.timestamp).all()
            
            result: List[BaseMessage] = []
            for msg in messages:
                if msg.role == "human":
                    result.append(HumanMessage(content=msg.content))
                elif msg.role == "ai":
                    result.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    result.append(SystemMessage(content=msg.content))
            
            return result
    
    def save_history(self, messages: List[BaseMessage]) -> None:
        """Save conversation history to database."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
                
            conversation = session.query(ConversationHistory).filter(
                ConversationHistory.user_id == user.id,
                ConversationHistory.session_id == self.session_id
            ).first()
            
            if not conversation:
                conversation = ConversationHistory(
                    user_id=user.id,
                    session_id=self.session_id
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
            
            session.query(Message).filter(Message.conversation_id == conversation.id).delete()
            
            for msg in messages:
                role = "human" if isinstance(msg, HumanMessage) else \
                       "ai" if isinstance(msg, AIMessage) else \
                       "system" if isinstance(msg, SystemMessage) else "unknown"
                
                db_message = Message(
                    user_id=user.id,
                    conversation_id=conversation.id,
                    role=role,
                    content=msg.content,
                    message_metadata={},
                    timestamp=datetime.now()
                )
                session.add(db_message)
            
            session.commit()
    
    def get_user_conversation_history(self, limit: int = 10) -> List[ConversationHistory]:
        """Get recent conversation history for the user."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                return []
            
            conversations = session.query(ConversationHistory).filter(
                ConversationHistory.user_id == user.id
            ).order_by(ConversationHistory.updated_at.desc()).limit(limit).all()
            
            return conversations
    
    def list_all_memories(self, filter_user_id: Optional[str] = None) -> List[MemoryRecord]:
        """List all memories for the user, optionally filtered by a different user."""
        with get_session() as session:
            if filter_user_id:
                user = session.query(User).filter(User.user_id == filter_user_id).first()
            else:
                user = session.query(User).filter(User.user_id == self.user_id).first()
                
            if user is None:
                return []
                
            memories = session.query(MemoryModel).filter(MemoryModel.user_id == user.id).order_by(MemoryModel.timestamp.desc()).all()
            
            results = [
                MemoryRecord(
                    timestamp=memory.timestamp.timestamp(),
                    description=memory.description,
                    metadata=memory.memory_metadata or {},
                    embedding=memory.embedding
                )
                for memory in memories
            ]
            if self.verbose and results:
                print(f"\033[34m📋 Listed {len(results)} memories\033[0m")
            return results

    def cleanup_temporary_users(self, older_than_hours: int = 24) -> int:
        """Clean up temporary users and their data older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        
        with get_session() as session:
            temp_users = session.query(User).filter(
                User.is_temporary,
                User.last_active < cutoff_time
            ).all()
            
            count = len(temp_users)
            for user in temp_users:
                session.delete(user)  # Cascade will delete related data
            
            session.commit()
            return count

    def _find_similar_memory(self, session, user_id: int, embedding: List[float], description: str) -> Optional[MemoryModel]:
        """Find a similar memory based on embedding similarity and description."""
        memories = session.query(MemoryModel).filter(MemoryModel.user_id == user_id).all()
        
        if not memories:
            return None
        
        best_similarity = 0.0
        best_memory = None
        
        for memory in memories:
            if memory.embedding:
                if memory.description.strip().lower() == description.strip().lower():
                    return memory
                
                similarity = sum(a * b for a, b in zip(embedding, memory.embedding))
                
                embedding_norm = sum(x * x for x in embedding) ** 0.5
                memory_norm = sum(x * x for x in memory.embedding) ** 0.5
                if embedding_norm > 0 and memory_norm > 0:
                    similarity = similarity / (embedding_norm * memory_norm)
                
                if similarity >= self.similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_memory = memory
        
        return best_memory
    
    def _merge_memories(self, session, existing_memory: MemoryModel, new_description: str, new_metadata: dict):
        """Merge a new memory with an existing similar memory."""
        if existing_memory.description.strip().lower() == new_description.strip().lower():
            if existing_memory.memory_metadata is None:
                existing_memory.memory_metadata = {}
            existing_memory.memory_metadata.update(new_metadata)
            existing_memory.timestamp = datetime.now()
            if self.verbose:
                print(f"\033[33m⚡ Memory updated (duplicate): {new_description}\033[0m")
        else:
            from ..utils.memory_combiner import MemoryCombiner
            combiner = MemoryCombiner(verbose=self.verbose)
            combined_description = combiner.combine_memories(existing_memory.description, new_description)
            existing_memory.description = combined_description
            if existing_memory.memory_metadata is None:
                existing_memory.memory_metadata = {}
            existing_memory.memory_metadata.update(new_metadata)
            existing_memory.timestamp = datetime.now()
            if self.verbose:
                print(f"\033[33m⚡ Memory merged (LLM): {combined_description}\033[0m")
        
        session.commit()

    @staticmethod
    def flush_all_memories() -> int:
        """Delete all memories from the database. Returns count of deleted memories."""
        with get_session() as session:
            count = session.query(MemoryModel).count()
            session.query(MemoryModel).delete()
            session.commit()
            return count

    @staticmethod
    def flush_user_memories(user_id: str) -> int:
        """Delete all memories for a specific user from the database. Returns count of deleted memories."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is None:
                return 0
            
            count = session.query(MemoryModel).filter(MemoryModel.user_id == user.id).count()
            session.query(MemoryModel).filter(MemoryModel.user_id == user.id).delete()
            session.commit()
            return count
