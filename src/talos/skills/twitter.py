from typing import Any

from talos.models.proposals import QueryResponse
from talos.skills.base import Skill


class TwitterSkill(Skill):
    """
    A skill for interacting with Twitter.
    """

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "twitter_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        # Not implemented yet
        return QueryResponse(answers=["The Twitter skill is not implemented yet."])
