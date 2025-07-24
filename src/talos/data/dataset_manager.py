from __future__ import annotations

import re
from io import BytesIO
from typing import Any

import requests
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

    def add_dataset(self, name: str, data: list[str]) -> None:
        """
        Adds a dataset to the DatasetManager.
        """
        if name in self.datasets and self.datasets.get(name):
            raise ValueError(f"Dataset with name '{name}' already exists.")
        self.datasets[name] = data
        if not data:
            return
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(data, self.embeddings)
        else:
            self.vector_store.add_texts(data)

    def remove_dataset(self, name: str) -> None:
        """
        Removes a dataset from the DatasetManager.
        """
        if name not in self.datasets:
            raise ValueError(f"Dataset with name '{name}' not found.")
        # This is a bit tricky with FAISS. For now, we'll just clear the vector store
        # and rebuild it without the removed dataset.
        del self.datasets[name]
        self.vector_store = None
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
        if name not in self.datasets:
            raise ValueError(f"Dataset with name '{name}' not found.")
        return self.datasets[name]

    def get_all_datasets(self) -> dict[str, Any]:
        """
        Gets all registered datasets.
        """
        return self.datasets

    def search(self, query: str, k: int = 5) -> list[str]:
        """
        Searches the vector store for similar documents.
        """
        if self.vector_store is None:
            return []
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def add_document_from_ipfs(self, name: str, ipfs_hash: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """
        Loads a document from IPFS hash and adds it to the dataset with intelligent chunking.
        
        Args:
            name: Name for the dataset
            ipfs_hash: IPFS hash of the document
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
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
        content = self._fetch_content_from_url(url)
        chunks = self._process_and_chunk_content(content, chunk_size, chunk_overlap)
        self.add_dataset(name, chunks)
    
    def _fetch_content_from_url(self, url: str) -> str:
        """Fetch content from URL, handling different content types."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type:
            pdf_reader = PdfReader(BytesIO(response.content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            if 'text/html' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
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
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def _find_sentence_boundary(self, text: str, start: int, end: int) -> int:
        """Find the best sentence boundary within the given range."""
        sentence_pattern = r'[.!?]\s+'
        
        for match in re.finditer(sentence_pattern, text[start:end]):
            boundary = start + match.end()
            if boundary > start:
                return boundary
        
        return end
