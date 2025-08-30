from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, PrivateAttr

from talos.data.dataset_manager import DatasetManager
from talos.tools.base import SupervisedTool


class DocumentLoaderArgs(BaseModel):
    name: str = Field(..., description="Name for the dataset")
    source: str = Field(..., description="IPFS hash or URL of the document")
    chunk_size: int = Field(1000, description="Maximum size of each text chunk")
    chunk_overlap: int = Field(200, description="Number of characters to overlap between chunks")


class DocumentLoaderTool(SupervisedTool):
    """Tool for loading documents from IPFS or URLs into the DatasetManager."""

    name: str = "document_loader"
    description: str = "Loads documents from IPFS hashes or URLs and adds them to the dataset manager with intelligent chunking for RAG"
    args_schema: type[BaseModel] = DocumentLoaderArgs
    _dataset_manager: DatasetManager = PrivateAttr()

    def __init__(self, dataset_manager: DatasetManager, **kwargs):
        super().__init__(**kwargs)
        self._dataset_manager = dataset_manager

    def _run_unsupervised(
        self, name: str, source: str, chunk_size: int = 1000, chunk_overlap: int = 200, **kwargs: Any
    ) -> str:
        """Load document from IPFS hash or URL."""
        try:
            all_datasets = self._dataset_manager.get_all_datasets()
            if name in all_datasets:
                return f"Dataset '{name}' already exists. Use dataset_search to query existing content."
            
            if self._is_ipfs_hash(source):
                self._dataset_manager.add_document_from_ipfs(name, source, chunk_size, chunk_overlap)
                return f"Successfully loaded document from IPFS hash {source} into dataset '{name}'"
            else:
                self._dataset_manager.add_document_from_url(name, source, chunk_size, chunk_overlap)
                return f"Successfully loaded document from URL {source} into dataset '{name}'"
        except Exception as e:
            return f"Failed to load document: {str(e)}"

    def _is_ipfs_hash(self, source: str) -> bool:
        """Check if source is an IPFS hash."""
        if source.startswith("Qm") and len(source) == 46:
            return True
        if source.startswith("b") and len(source) > 46:
            return True
        if source.startswith("ipfs://"):
            return True
        return False


class DatasetSearchArgs(BaseModel):
    query: str = Field(..., description="Search query")
    k: int = Field(5, description="Number of results to return")


class DatasetSearchTool(SupervisedTool):
    """Tool for searching datasets in the DatasetManager."""

    name: str = "dataset_search"
    description: str = "Search for similar content in loaded datasets"
    args_schema: type[BaseModel] = DatasetSearchArgs
    _dataset_manager: DatasetManager = PrivateAttr()

    def __init__(self, dataset_manager: DatasetManager, **kwargs):
        super().__init__(**kwargs)
        self._dataset_manager = dataset_manager

    def _run_unsupervised(self, query: str, k: int = 5, **kwargs: Any) -> list[str]:
        """Search for similar content in the datasets."""
        try:
            results = self._dataset_manager.search(query, k)
            if not results:
                return ["No relevant documents found in datasets"]
            return results
        except Exception as e:
            return [f"Search failed: {str(e)}"]
