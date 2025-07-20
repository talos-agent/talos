from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TicketStatus(str, Enum):
    """
    The status of a ticket.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TicketCreationRequest(BaseModel):
    """
    A request to create a ticket.
    """

    tool: str
    tool_args: dict[str, Any]


class Ticket(BaseModel):
    """
    A ticket for a long-running process.
    """

    ticket_id: str = Field(..., description="The ID of the ticket.")
    status: TicketStatus = Field(..., description="The status of the ticket.")
    created_at: str = Field(..., description="The timestamp when the ticket was created.")
    updated_at: str = Field(..., description="The timestamp when the ticket was last updated.")
    request: TicketCreationRequest = Field(..., description="The request that created the ticket.")


class TicketResult(BaseModel):
    """
    The result of a ticket.
    """

    ticket_id: str = Field(..., description="The ID of the ticket.")
    status: TicketStatus = Field(..., description="The status of the ticket.")
    result: Any | None = Field(None, description="The result of the ticket.")
    error: str | None = Field(None, description="The error message if the ticket failed.")
