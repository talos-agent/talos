from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch

from talos.tools.github.tools import GithubTools


class TestGithubTools(unittest.TestCase):
    def setUp(self):
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            self.github_tools = GithubTools()

    @patch("talos.tools.github.tools.Github")
    def test_initialization_with_cache(self, mock_github_class):
        """Test that GithubTools initializes with proper cache configuration."""
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            
            tools = GithubTools(cache_ttl=600, cache_maxsize=10)
            
            # Verify cache is initialized with correct parameters
            self.assertEqual(tools._repo_cache.maxsize, 10)
            self.assertEqual(tools._repo_cache.ttl, 600)
            self.assertEqual(len(tools._repo_cache), 0)

    @patch("talos.tools.github.tools.Github")
    def test_get_cached_repo_cache_miss(self, mock_github_class):
        """Test cache miss scenario - first time accessing a repo."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools()
            
            # First call should be a cache miss
            result = tools._get_cached_repo("testuser", "testrepo")
            
            # Verify API was called
            mock_github_instance.get_repo.assert_called_once_with("testuser/testrepo")
            self.assertEqual(result, mock_repo)
            
            # Verify repo is now cached
            self.assertEqual(len(tools._repo_cache), 1)
            self.assertIn("testuser/testrepo", tools._repo_cache)

    @patch("talos.tools.github.tools.Github")
    def test_get_cached_repo_cache_hit(self, mock_github_class):
        """Test cache hit scenario - repo already in cache."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools()
            
            # First call - cache miss
            result1 = tools._get_cached_repo("testuser", "testrepo")
            
            # Second call - should be cache hit
            result2 = tools._get_cached_repo("testuser", "testrepo")
            
            # Verify API was only called once
            mock_github_instance.get_repo.assert_called_once_with("testuser/testrepo")
            
            # Both results should be the same object
            self.assertEqual(result1, result2)
            self.assertEqual(result1, mock_repo)

    @patch("talos.tools.github.tools.Github")
    def test_cache_ttl_expiration(self, mock_github_class):
        """Test that cache entries expire after TTL."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            # Use very short TTL for testing
            tools = GithubTools(cache_ttl=1)
            
            # First call
            tools._get_cached_repo("testuser", "testrepo")
            self.assertEqual(mock_github_instance.get_repo.call_count, 1)
            
            # Wait for TTL to expire
            time.sleep(1.1)
            
            # Second call after expiration - should hit API again
            tools._get_cached_repo("testuser", "testrepo")
            self.assertEqual(mock_github_instance.get_repo.call_count, 2)

    @patch("talos.tools.github.tools.Github")
    def test_cache_info(self, mock_github_class):
        """Test cache info method returns correct statistics."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools(cache_ttl=300, cache_maxsize=20)
            
            # Initially empty cache
            info = tools.get_cache_info()
            expected = {
                "cache_size": 0,
                "max_size": 20,
                "ttl": 300,
                "cached_repos": []
            }
            self.assertEqual(info, expected)
            
            # Add some repos to cache
            tools._get_cached_repo("user1", "repo1")
            tools._get_cached_repo("user2", "repo2")
            
            info = tools.get_cache_info()
            self.assertEqual(info["cache_size"], 2)
            self.assertEqual(info["max_size"], 20)
            self.assertEqual(info["ttl"], 300)
            self.assertIn("user1/repo1", info["cached_repos"])
            self.assertIn("user2/repo2", info["cached_repos"])

    @patch("talos.tools.github.tools.Github")
    def test_clear_cache(self, mock_github_class):
        """Test that clear_cache empties the cache."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools()
            
            # Add repos to cache
            tools._get_cached_repo("user1", "repo1")
            tools._get_cached_repo("user2", "repo2")
            self.assertEqual(len(tools._repo_cache), 2)
            
            # Clear cache
            tools.clear_cache()
            self.assertEqual(len(tools._repo_cache), 0)
            
            # Verify next access hits API again
            mock_github_instance.get_repo.reset_mock()
            tools._get_cached_repo("user1", "repo1")
            mock_github_instance.get_repo.assert_called_once_with("user1/repo1")

    @patch("talos.tools.github.tools.Github")
    def test_get_open_issues_uses_cache(self, mock_github_class):
        """Test that get_open_issues uses the cached repo."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/test/issues/123"
        mock_repo.get_issues.return_value = [mock_issue]
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools()
            
            # Call get_open_issues twice
            result1 = tools.get_open_issues("testuser", "testrepo")
            result2 = tools.get_open_issues("testuser", "testrepo")
            
            # Verify API was only called once (second call used cache)
            mock_github_instance.get_repo.assert_called_once_with("testuser/testrepo")
            
            # Verify results are correct
            expected = [{"number": 123, "title": "Test Issue", "url": "https://github.com/test/test/issues/123"}]
            self.assertEqual(result1, expected)
            self.assertEqual(result2, expected)

    @patch("talos.tools.github.tools.Github")
    def test_multiple_methods_use_same_cached_repo(self, mock_github_class):
        """Test that multiple methods can use the same cached repository."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        
        # Mock different method responses
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/test/issues/123"
        mock_repo.get_issues.return_value = [mock_issue]
        
        mock_pr = MagicMock()
        mock_pr.number = 456
        mock_pr.title = "Test PR"
        mock_pr.html_url = "https://github.com/test/test/pull/456"
        mock_repo.get_pulls.return_value = [mock_pr]
        
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            tools = GithubTools()
            
            # Call different methods that should use the same cached repo
            tools.get_open_issues("testuser", "testrepo")
            tools.get_all_pull_requests("testuser", "testrepo")
            
            # Verify API was only called once
            mock_github_instance.get_repo.assert_called_once_with("testuser/testrepo")
            
            # Verify both methods were called on the same repo object
            mock_repo.get_issues.assert_called_once()
            mock_repo.get_pulls.assert_called_once()

    @patch("talos.tools.github.tools.Github")
    def test_cache_maxsize_limit(self, mock_github_class):
        """Test that cache respects maxsize limit."""
        mock_github_instance = MagicMock()
        mock_github_class.return_value = mock_github_instance
        mock_repo = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        
        with patch("talos.tools.github.tools.GitHubSettings") as mock_settings:
            mock_settings.return_value.GITHUB_API_TOKEN = "test_token"
            # Set small cache size for testing
            tools = GithubTools(cache_maxsize=2)
            
            # Add repos up to cache limit
            tools._get_cached_repo("user1", "repo1")
            tools._get_cached_repo("user2", "repo2")
            self.assertEqual(len(tools._repo_cache), 2)
            
            # Adding third repo should evict one (LRU behavior)
            tools._get_cached_repo("user3", "repo3")
            self.assertEqual(len(tools._repo_cache), 2)
            self.assertIn("user3/repo3", tools._repo_cache)


if __name__ == "__main__":
    unittest.main()
