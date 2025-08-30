from __future__ import annotations

import re
from io import BytesIO
from typing import Any, Optional, Union

from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, ConfigDict, Field
from pypdf import PdfReader

from talos.tools.ipfs import IpfsTool


class DatasetManager(BaseModel):
    """
    A class for managing datasets for the Talos agent.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    datasets: dict[str, Any] = Field(default_factory=dict)
    vector_store: Any = Field(default=None)
    embeddings: Any = Field(default_factory=OpenAIEmbeddings)
    verbose: Union[bool, int] = Field(default=False)
    user_id: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    use_database: bool = Field(default=False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db_backend = None
        
        if self.use_database and self.user_id and self.embeddings:
            from ..database.dataset_backend import DatabaseDatasetBackend
            self._db_backend = DatabaseDatasetBackend(
                user_id=self.user_id,
                embeddings_model=self.embeddings,
                session_id=self.session_id,
                verbose=self.verbose
            )

    def add_dataset(self, name: str, data: list[str]) -> None:
        """
        Adds a dataset to the DatasetManager.
        """
        if self._db_backend:
            self._db_backend.add_dataset(name, data)
            return
        
        if name in self.datasets and self.datasets.get(name):
            raise ValueError(f"Dataset with name '{name}' already exists.")
        self.datasets[name] = data
        if not data:
            if self._get_verbose_level() >= 1:
                print(f"\033[33m⚠️ Dataset '{name}' added but is empty\033[0m")
            return
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(data, self.embeddings)
        else:
            self.vector_store.add_texts(data)
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1:
            print(f"\033[32m✓ Dataset '{name}' added with {len(data)} chunks\033[0m")
            if verbose_level >= 2:
                print(f"  Dataset type: {type(self.vector_store).__name__}")
                print(f"  Total datasets: {len(self.datasets)}")

    def remove_dataset(self, name: str) -> None:
        """
        Removes a dataset from the DatasetManager.
        """
        if self._db_backend:
            self._db_backend.remove_dataset(name)
            return
        
        if name not in self.datasets:
            raise ValueError(f"Dataset with name '{name}' not found.")
        del self.datasets[name]
        self.vector_store = None
        self._rebuild_vector_store()
        
    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))
        
    def _rebuild_vector_store(self):
        """Rebuild the vector store from all datasets."""
        for dataset_name, dataset in self.datasets.items():
            if not dataset:
                continue
            if self.vector_store is None:
                self.vector_store = FAISS.from_texts(dataset, self.embeddings)
            else:
                self.vector_store.add_texts(dataset)

    def get_dataset(self, name: str) -> Any:
        """
        Gets a dataset by name.
        """
        if self._db_backend:
            return self._db_backend.get_dataset(name)
        
        if name not in self.datasets:
            raise ValueError(f"Dataset with name '{name}' not found.")
        return self.datasets[name]

    def get_all_datasets(self) -> dict[str, Any]:
        """
        Gets all registered datasets.
        """
        if self._db_backend:
            return self._db_backend.get_all_datasets()
        
        return self.datasets

    def search(self, query: str, k: int = 5, context_search: bool = False) -> list[str]:
        """
        Searches the vector store for similar documents.
        """
        if self._db_backend:
            return self._db_backend.search(query, k, context_search)
        
        if self.vector_store is None:
            if self._get_verbose_level() >= 1 and not context_search:
                print("\033[33m⚠️ Dataset search: no datasets available\033[0m")
            return []
        results = self.vector_store.similarity_search(query, k=k)
        result_texts = [doc.page_content for doc in results]
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1 and result_texts and not context_search:
            print(f"\033[34m🔍 Dataset search: found {len(result_texts)} relevant documents\033[0m")
            if verbose_level >= 2:
                for i, doc_text in enumerate(result_texts[:3], 1):
                    content_preview = doc_text[:100] + "..." if len(doc_text) > 100 else doc_text
                    print(f"  {i}. {content_preview}")
                if len(result_texts) > 3:
                    print(f"  ... and {len(result_texts) - 3} more documents")
        return result_texts

    def add_document_from_ipfs(
        self, name: str, ipfs_hash: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> None:
        """
        Loads a document from IPFS hash and adds it to the dataset with intelligent chunking.

        Args:
            name: Name for the dataset
            ipfs_hash: IPFS hash of the document
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        if self._db_backend:
            self._db_backend.add_document_from_ipfs(name, ipfs_hash, chunk_size, chunk_overlap)
            return
        
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1:
            print(f"\033[36m📦 Fetching content from IPFS: {ipfs_hash}\033[0m")
            if verbose_level >= 2:
                print(f"  IPFS hash: {ipfs_hash}")
        ipfs_tool = IpfsTool()
        content = ipfs_tool.get_content(ipfs_hash)

        chunks = self._process_and_chunk_content(content, chunk_size, chunk_overlap)
        self.add_dataset(name, chunks)

    def add_document_from_url(self, name: str, url: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """
        Loads a document from URL and adds it to the dataset with intelligent chunking.

        Args:
            name: Name for the dataset
            url: URL of the document
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        if self._db_backend:
            self._db_backend.add_document_from_url(name, url, chunk_size, chunk_overlap)
            return
        
        verbose_level = self._get_verbose_level()
        if verbose_level >= 1:
            print(f"\033[36m🌐 Fetching content from URL: {url}\033[0m")
        content = self._fetch_content_from_url(url)
        if verbose_level >= 2:
            print(f"  URL: {url}")
            content_type = "text/html"  # Default content type for verbose output
            print(f"  Content type: {content_type}")
        chunks = self._process_and_chunk_content(content, chunk_size, chunk_overlap)
        self.add_dataset(name, chunks)

    def _fetch_content_from_url(self, url: str) -> str:
        """Fetch content from URL, handling different content types."""
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
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find the best sentence boundary within the given range."""
        sentence_pattern = r"[.!?]\s+"

        for match in re.finditer(sentence_pattern, text[start:end]):
            boundary = start + match.end()
            if boundary > start:
                return boundary

        return end
