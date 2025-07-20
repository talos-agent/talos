from unittest.mock import MagicMock, patch

import pytest

from talos.data.dataset_manager import DatasetManager


@pytest.fixture
def dataset_manager():
    with patch("openai.OpenAI"), patch("openai.AsyncOpenAI"):
        manager = DatasetManager()
        return manager


def test_add_dataset(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS") as mock_faiss:
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        assert "test_dataset" in dataset_manager.datasets
        mock_faiss.from_texts.assert_called_once()


def test_add_duplicate_dataset(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS"):
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        with pytest.raises(ValueError):
            dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])


def test_remove_dataset(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS"):
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        dataset_manager.remove_dataset("test_dataset")
        assert "test_dataset" not in dataset_manager.datasets


def test_remove_nonexistent_dataset(dataset_manager):
    with pytest.raises(ValueError):
        dataset_manager.remove_dataset("nonexistent_dataset")


def test_get_dataset(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS"):
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        dataset = dataset_manager.get_dataset("test_dataset")
        assert dataset == ["doc1", "doc2"]


def test_get_nonexistent_dataset(dataset_manager):
    with pytest.raises(ValueError):
        dataset_manager.get_dataset("nonexistent_dataset")


def test_get_all_datasets(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS"):
        dataset_manager.add_dataset("dataset1", ["doc1", "doc2"])
        dataset_manager.add_dataset("dataset2", ["doc3", "doc4"])
        datasets = dataset_manager.get_all_datasets()
        assert len(datasets) == 2
        assert "dataset1" in datasets
        assert "dataset2" in datasets


def test_search(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS") as mock_faiss:
        mock_vector_store = MagicMock()
        mock_vector_store.similarity_search.return_value = [MagicMock(page_content="doc1")]
        mock_faiss.from_texts.return_value = mock_vector_store
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        results = dataset_manager.search("fruit")
        assert isinstance(results, list)
        assert results == ["doc1"]


def test_add_empty_dataset(dataset_manager):
    mock_embeddings = MagicMock()
    mock_embeddings.embed_documents.return_value = []
    dataset_manager.embeddings = mock_embeddings
    dataset_manager.add_dataset("empty_dataset", [])
    assert "empty_dataset" in dataset_manager.datasets
    assert dataset_manager.vector_store is None


def test_search_with_empty_query(dataset_manager):
    with patch("talos.data.dataset_manager.FAISS"):
        dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        results = dataset_manager.search("")
        assert results == []


def test_search_on_empty_dataset(dataset_manager):
    results = dataset_manager.search("query")
    assert results == []
