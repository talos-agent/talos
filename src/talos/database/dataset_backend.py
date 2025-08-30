import uuid
from datetime import datetime
from typing import Optional, Union
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS

from .models import User, Dataset, DatasetChunk
from .session import get_session


class DatabaseDatasetBackend:
    """Database-backed dataset implementation using SQLAlchemy."""
    
    def __init__(
        self,
        user_id: str,
        embeddings_model: Embeddings,
        session_id: Optional[str] = None,
        verbose: Union[bool, int] = False,
    ):
        self.user_id = user_id
        self.embeddings_model = embeddings_model
        self.session_id = session_id or str(uuid.uuid4())
        self.verbose = verbose
        
    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))
    
    
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
    
    def add_dataset(self, name: str, data: list[str]) -> None:
        """Add a dataset to the database."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
            
            existing_dataset = session.query(Dataset).filter(
                Dataset.user_id == user.id,
                Dataset.name == name
            ).first()
            
            if existing_dataset:
                raise ValueError(f"Dataset with name '{name}' already exists.")
            
            if not data:
                dataset = Dataset(
                    user_id=user.id,
                    name=name,
                    dataset_metadata={}
                )
                session.add(dataset)
                session.commit()
                verbose_level = self._get_verbose_level()
                if verbose_level >= 1:
                    print(f"\033[33m⚠️ Dataset '{name}' added but is empty\033[0m")
                return
            
            dataset = Dataset(
                user_id=user.id,
                name=name,
                dataset_metadata={}
            )
            session.add(dataset)
            session.commit()
            session.refresh(dataset)
            
            for idx, text in enumerate(data):
                embedding = self.embeddings_model.embed_query(text)
                chunk = DatasetChunk(
                    dataset_id=dataset.id,
                    content=text,
                    embedding=embedding,
                    chunk_index=idx,
                    chunk_metadata={}
                )
                session.add(chunk)
            
            session.commit()
            verbose_level = self._get_verbose_level()
            if verbose_level >= 1:
                print(f"\033[32m✓ Dataset '{name}' added with {len(data)} chunks\033[0m")
                if verbose_level >= 2:
                    print(f"  Dataset ID: {dataset.id}")
                    print(f"  Document count: {len(data)}")
    
    def remove_dataset(self, name: str) -> None:
        """Remove a dataset from the database."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
            
            dataset = session.query(Dataset).filter(
                Dataset.user_id == user.id,
                Dataset.name == name
            ).first()
            
            if not dataset:
                raise ValueError(f"Dataset with name '{name}' not found.")
            
            session.delete(dataset)
            session.commit()
    
    def get_dataset(self, name: str) -> list[str]:
        """Get a dataset by name."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
            
            dataset = session.query(Dataset).filter(
                Dataset.user_id == user.id,
                Dataset.name == name
            ).first()
            
            if not dataset:
                raise ValueError(f"Dataset with name '{name}' not found.")
            
            chunks = session.query(DatasetChunk).filter(
                DatasetChunk.dataset_id == dataset.id
            ).order_by(DatasetChunk.chunk_index).all()
            
            return [chunk.content for chunk in chunks]
    
    def get_all_datasets(self) -> dict[str, list[str]]:
        """Get all datasets for the user."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                return {}
            
            datasets = session.query(Dataset).filter(Dataset.user_id == user.id).all()
            result = {}
            
            for dataset in datasets:
                chunks = session.query(DatasetChunk).filter(
                    DatasetChunk.dataset_id == dataset.id
                ).order_by(DatasetChunk.chunk_index).all()
                result[dataset.name] = [chunk.content for chunk in chunks]
            
            return result
    
    def search(self, query: str, k: int = 5, context_search: bool = False) -> list[str]:
        """Search datasets using semantic similarity."""
        query_embedding = self.embeddings_model.embed_query(query)
        
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                return []
            
            chunks = session.query(DatasetChunk).join(Dataset).filter(
                Dataset.user_id == user.id,
                DatasetChunk.embedding.isnot(None)
            ).all()
            
            if not chunks:
                if self._get_verbose_level() >= 1 and not context_search:
                    print("\033[33m⚠️ Dataset search: no datasets available\033[0m")
                return []
            
            similarities = []
            for chunk in chunks:
                if chunk.embedding:
                    similarity = sum(a * b for a, b in zip(query_embedding, chunk.embedding))
                    similarities.append((similarity, chunk))
            
            similarities.sort(key=lambda x: x[0], reverse=True)
            top_chunks = similarities[:k]
            
            results = [chunk.content for _, chunk in top_chunks]
            verbose_level = self._get_verbose_level()
            if verbose_level >= 1 and results and not context_search:
                print(f"\033[34m🔍 Dataset search: found {len(results)} relevant documents\033[0m")
                if verbose_level >= 2:
                    for i, result in enumerate(results[:3], 1):
                        content_preview = result[:100] + "..." if len(result) > 100 else result
                        print(f"  {i}. {content_preview}")
                    if len(results) > 3:
                        print(f"  ... and {len(results) - 3} more documents")
            return results
    
    def _build_vector_store(self) -> Optional[FAISS]:
        """Build FAISS vector store from database chunks."""
        with get_session() as session:
            user = session.query(User).filter(User.user_id == self.user_id).first()
            if user is None:
                return None
            
            chunks = session.query(DatasetChunk).join(Dataset).filter(
                Dataset.user_id == user.id,
                DatasetChunk.embedding.isnot(None)
            ).all()
            
            if not chunks:
                return None
            
            texts = []
            embeddings = []
            
            for chunk in chunks:
                if chunk.embedding is not None:
                    texts.append(chunk.content)
                    embeddings.append(chunk.embedding)
            
            if texts and embeddings:
                return FAISS.from_embeddings(
                    text_embeddings=list(zip(texts, embeddings)),
                    embedding=self.embeddings_model
                )
            
            return None
    
    def add_document_from_ipfs(
        self, name: str, ipfs_hash: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> None:
        """Load a document from IPFS hash and add it to the dataset."""
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1:
            print(f"\033[36m📦 Fetching content from IPFS: {ipfs_hash}\033[0m")
            if verbose_level >= 2:
                print(f"  IPFS hash: {ipfs_hash}")
        
        from ..tools.ipfs import IpfsTool
        ipfs_tool = IpfsTool()
        content = ipfs_tool.get_content(ipfs_hash)
        
        chunks = self._process_and_chunk_content(content, chunk_size, chunk_overlap)
        self.add_dataset(name, chunks)
    
    def add_document_from_url(
        self, name: str, url: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> None:
        """Load a document from URL and add it to the dataset."""
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1:
            print(f"\033[36m🌐 Fetching content from URL: {url}\033[0m")
            if verbose_level >= 2:
                print(f"  URL: {url}")
        
        content = self._fetch_content_from_url(url)
        chunks = self._process_and_chunk_content(content, chunk_size, chunk_overlap)
        self.add_dataset(name, chunks)
    
    def _fetch_content_from_url(self, url: str) -> str:
        """Fetch content from URL, handling different content types."""
        from bs4 import BeautifulSoup
        from pypdf import PdfReader
        from io import BytesIO
        
        from talos.utils.http_client import SecureHTTPClient
        http_client = SecureHTTPClient()
        response = http_client.get(url)

        content_type = response.headers.get("content-type", "").lower()

        if "application/pdf" in content_type:
            pdf_reader = PdfReader(BytesIO(response.content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            if "text/html" in content_type:
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text()
            else:
                return response.text
    
    def _process_and_chunk_content(self, content: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        """Process content and split into intelligent chunks."""
        content = self._clean_text(content)

        chunks = []
        start = 0

        while start < len(content):
            end = start + chunk_size

            if end < len(content):
                search_start = max(start + chunk_size - 200, start)
                sentence_end = self._find_sentence_boundary(content, search_start, end)
                if sentence_end > start:
                    end = sentence_end

            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = max(start + chunk_size - chunk_overlap, end)

            if start >= len(content):
                break

        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        import re
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find the best sentence boundary within the given range."""
        import re
        sentence_pattern = r"[.!?]\s+"

        for match in re.finditer(sentence_pattern, text[start:end]):
            boundary = start + match.end()
            if boundary > start:
                return boundary

        return end
