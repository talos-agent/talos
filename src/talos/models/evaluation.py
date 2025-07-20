from typing import Any, Dict

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    score: int = Field(..., ge=0, le=100, description="The evaluation score, from 0 to 100.")
    additional_data: Dict[str, Any] = Field({}, description="A dictionary of additional data from the evaluation.")
