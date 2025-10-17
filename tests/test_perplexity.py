from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from talos.services.implementations.perplexity import PerplexityService


@pytest.fixture
def perplexity_service() -> PerplexityService:
    return PerplexityService(token="test_token")


@patch("requests.post")
def test_search_success(mock_post: MagicMock, perplexity_service: PerplexityService) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "test_result"}
    mock_post.return_value = mock_response

    response = perplexity_service.search("test_query")

    assert response == {"result": "test_result"}
    mock_post.assert_called_once_with(
        "https://api.perplexity.ai/search",
        headers={
            "Authorization": "Bearer test_token",
            "Content-Type": "application/json",
        },
        json={"query": "test_query"},
    )


@patch("requests.post")
def test_search_failure(mock_post: MagicMock, perplexity_service: PerplexityService) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = Exception("Test error")
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        perplexity_service.search("test_query")