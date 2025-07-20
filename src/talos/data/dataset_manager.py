from typing import Any, Dict, List

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field


class DatasetManager(BaseModel):
    """
    A class for managing datasets for the Talos agent.
    """

    datasets: Dict[str, Any] = Field(default_factory=dict)
    vector_store: Any = Field(default=None)
    embeddings: Any = Field(default_factory=OpenAIEmbeddings)

    class Config:
        arbitrary_types_allowed = True

    def add_dataset(self, name: str, data: List[str]):
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

    def remove_dataset(self, name: str):
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

    def get_all_datasets(self) -> Dict[str, Any]:
        """
        Gets all registered datasets.
        """
        return self.datasets

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Searches the vector store for similar documents.
        """
        if self.vector_store is None:
            return []
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]
