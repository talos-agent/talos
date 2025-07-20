from typing import Optional

from pydantic import BaseModel


class Issue(BaseModel):
    number: int
    title: str
    url: str


class Comment(BaseModel):
    user: str
    comment: str
    reply_to: Optional[str] = None


class PullRequestFile(BaseModel):
    filename: str
