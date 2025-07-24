from datetime import datetime
from pydantic import BaseModel


class TwitterPublicMetrics(BaseModel):
    followers_count: int
    following_count: int
    tweet_count: int
    listed_count: int
    like_count: int


class TwitterUser(BaseModel):
    id: str
    username: str
    name: str
    created_at: datetime
    profile_image_url: str
    public_metrics: TwitterPublicMetrics
