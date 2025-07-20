from typing import Any

from talos.services.abstract.twitter import Twitter
from talos.services.proposals.models import QueryResponse


class TwitterService(Twitter):
    """
    A service for interacting with Twitter.
    """

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "twitter"

    def run(self, **kwargs: Any) -> QueryResponse:
        # Not implemented yet
        return QueryResponse(answers=["The Twitter service is not implemented yet."])
