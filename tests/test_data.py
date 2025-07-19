import unittest
from unittest.mock import patch, MagicMock
from talos.data.dataset_manager import DatasetManager


class TestDatasetManager(unittest.TestCase):
    @patch("talos.data.dataset_manager.OpenAIEmbeddings")
    @patch("talos.data.dataset_manager.FAISS")
    def setUp(self, mock_faiss, mock_embeddings):
        self.mock_embeddings = mock_embeddings.return_value
        self.mock_embeddings.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        self.dataset_manager = DatasetManager()
        self.dataset_manager.embeddings = self.mock_embeddings

    def test_add_dataset(self):
        self.dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        self.assertIn("test_dataset", self.dataset_manager.datasets)

    def test_add_duplicate_dataset(self):
        self.dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        with self.assertRaises(ValueError):
            self.dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])

    def test_remove_dataset(self):
        self.dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        self.dataset_manager.remove_dataset("test_dataset")
        self.assertNotIn("test_dataset", self.dataset_manager.datasets)

    def test_remove_nonexistent_dataset(self):
        with self.assertRaises(ValueError):
            self.dataset_manager.remove_dataset("nonexistent_dataset")

    def test_get_dataset(self):
        self.dataset_manager.add_dataset("test_dataset", ["doc1", "doc2"])
        dataset = self.dataset_manager.get_dataset("test_dataset")
        self.assertEqual(dataset, ["doc1", "doc2"])

    def test_get_nonexistent_dataset(self):
        with self.assertRaises(ValueError):
            self.dataset_manager.get_dataset("nonexistent_dataset")

    def test_get_all_datasets(self):
        self.dataset_manager.add_dataset("dataset1", ["doc1", "doc2"])
        with patch.object(self.dataset_manager.vector_store, "add_texts"):
            self.dataset_manager.add_dataset("dataset2", ["doc3", "doc4"])
            datasets = self.dataset_manager.get_all_datasets()
            self.assertEqual(len(datasets), 2)
            self.assertIn("dataset1", datasets)
            self.assertIn("dataset2", datasets)

    def test_search(self):
        self.dataset_manager.vector_store = MagicMock()
        self.dataset_manager.vector_store.similarity_search.return_value = [MagicMock(page_content="doc1")]
        results = self.dataset_manager.search("fruit")
        self.assertIsInstance(results, list)
        self.assertEqual(results, ["doc1"])


if __name__ == "__main__":
    unittest.main()
