from __future__ import annotations

from pydantic import BaseModel


class Feedback(BaseModel):
    delegate: str
    feedback: str


class Proposal(BaseModel):
    proposal_text: str
    feedback: list[Feedback]


class QueryResponse(BaseModel):
    answers: list[str]


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
