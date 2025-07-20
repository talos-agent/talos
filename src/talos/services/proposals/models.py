from pydantic import BaseModel
from typing import Any, List, Optional


class Feedback(BaseModel):
    delegate: str
    feedback: str


class Proposal(BaseModel):
    prompt: str
    proposal_text: str
    feedback: List[Feedback]


class QueryResponse(BaseModel):
    answers: List[dict[str, Any]]


class RunParams(BaseModel):
    tool: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    prompt: Optional[str] = None
    prompt_args: Optional[dict[str, Any]] = None
    discipline: Optional[str] = None


class AddDatasetParams(BaseModel):
    pass
