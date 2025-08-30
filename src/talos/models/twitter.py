from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TwitterPublicMetrics(BaseModel):
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int
    like_count: int
    media_count: int = Field(default=0)


class TwitterUser(BaseModel):
    id: int
    username: str
    name: str
    created_at: datetime
    profile_image_url: str
    public_metrics: TwitterPublicMetrics
    description: str | None = None
    url: str | None = None
    verified: bool = False


class ReferencedTweet(BaseModel):
    type: str
    id: int


class Tweet(BaseModel):
    id: int
    text: str
    author_id: str
    created_at: Optional[str] = None
    conversation_id: Optional[str] = None
    public_metrics: dict = Field(default_factory=dict)
    referenced_tweets: Optional[list[ReferencedTweet]] = None
    in_reply_to_user_id: Optional[str] = None
    edit_history_tweet_ids: Optional[list[str]] = None

    def is_reply_to(self, tweet_id: str) -> bool:
        """Check if this tweet is a reply to the specified tweet ID."""
        if not self.referenced_tweets:
            return False
        return any(ref.type == "replied_to" and ref.id == tweet_id for ref in self.referenced_tweets)

    def get_replied_to_id(self) -> Optional[int]:
        """Get the ID of the tweet this is replying to, if any."""
        if not self.referenced_tweets:
            return None
        for ref in self.referenced_tweets:
            if ref.type == "replied_to":
                return ref.id
        return None
