from __future__ import annotations

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    delegate: str
    feedback: str


class Proposal(BaseModel):
    proposal_text: str
    feedback: list[Feedback]


class QueryResponse(BaseModel):
    answers: list[str]
    score: float | None = Field(None, description="The score of the response.")


class Question(BaseModel):
    text: str
    feedback: list[Feedback]


class Plan(BaseModel):
    plan: str


class RunParams(BaseModel):
    tool: str | None = None
    tool_args: dict | None = None
    prompt: str | None = None
    prompt_args: dict | None = None
    discipline: str | None = None
