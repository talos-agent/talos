import unittest
from unittest.mock import Mock, patch

from talos.data.dataset_manager import DatasetManager
from talos.tools.document_loader import DatasetSearchTool, DocumentLoaderTool


class TestDocumentLoader(unittest.TestCase):
    def setUp(self):
        with patch("openai.OpenAI"), patch("openai.AsyncOpenAI"):
            self.dataset_manager = DatasetManager()
        self.document_loader = DocumentLoaderTool(self.dataset_manager)
        self.dataset_search = DatasetSearchTool(self.dataset_manager)

    def test_is_ipfs_hash(self):
        self.assertTrue(self.document_loader._is_ipfs_hash("QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"))
        self.assertTrue(self.document_loader._is_ipfs_hash("ipfs://QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"))
        self.assertFalse(self.document_loader._is_ipfs_hash("https://example.com/document.pdf"))
    
    @patch('talos.utils.http_client.SecureHTTPClient.get')
    def test_fetch_content_from_url_text(self, mock_get):
        mock_response = Mock()
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.text = "This is a test document."
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        content = self.dataset_manager._fetch_content_from_url("https://example.com/test.txt")
        self.assertEqual(content, "This is a test document.")

    def test_clean_text(self):
        dirty_text = "This   is    a\n\n\n\ntest   document."
        clean_text = self.dataset_manager._clean_text(dirty_text)
        self.assertEqual(clean_text, "This is a\n\ntest document.")

    def test_chunk_content(self):
        content = "This is sentence one. This is sentence two. This is sentence three."
        chunks = self.dataset_manager._process_and_chunk_content(content, chunk_size=30, chunk_overlap=10)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(len(chunk) <= 40 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
