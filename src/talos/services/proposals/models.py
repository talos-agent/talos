from pydantic import BaseModel
from typing import List

class Feedback(BaseModel):
    delegate: str
    feedback: str

class Proposal(BaseModel):
    prompt: str
    proposal_text: str
    feedback: List[Feedback]

