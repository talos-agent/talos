from pydantic import BaseModel
from typing import List

class Feedback(BaseModel):
    delegate: str
    feedback: str

class Proposal(BaseModel):
    prompt: str
    proposal_text: str
    feedback: List[Feedback]

class QueryResponse(BaseModel):
    answers: List[str]

class RunParams(BaseModel):
    tool: str | None = None
    tool_args: dict | None = None
    prompt: str | None = None
    prompt_args: dict | None = None
    discipline: str | None = None
