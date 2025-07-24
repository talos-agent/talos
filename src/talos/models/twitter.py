from datetime import datetime

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
