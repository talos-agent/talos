from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


class RunParams(BaseModel):
    """
    Parameters for the `run` method.
    """

    web_search: bool = Field(False, description="Whether to perform a web search.")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="Extra parameters for the agent.")


class AddDatasetParams(BaseModel):
    """
    Parameters for the `add_dataset` method.
    """

    extra_params: Optional[Dict[str, Any]] = Field(None, description="Extra parameters for adding the dataset.")


class QueryResult(BaseModel):
    """
    A single query result.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    answer: str
    context: Optional[str]
    score: float
    document_id: Optional[str]
    meta: Optional[Dict[str, Any]]


class Feedback(BaseModel):
    """
    Feedback on a proposal from a delegate.
    """

    delegate: str
    feedback: str


class Proposal(BaseModel):
    """
    A proposal to be evaluated by the agent.
    """

    prompt: str
    proposal_text: str
    feedback: List[Feedback]


class QueryResponse(BaseModel):
    """
    The response from a query.
    """

    answers: List[QueryResult]
