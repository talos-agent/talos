from __future__ import annotations

import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict

from langchain_core.tools import tool
from pydantic import BaseModel, PrivateAttr

from talos.models.services import Ticket, TicketCreationRequest, TicketResult, TicketStatus


class Skill(BaseModel, ABC):
    """
    An abstract base class for a skill.
    Skills are a way to organize and manage the agent's actions.
    They are LLM driven actions, which means that they are powered by a
    language model. This allows them to be more flexible and powerful
    than traditional tools.
    """

    _tickets: Dict[str, Ticket] = PrivateAttr(default_factory=dict)
    _results: Dict[str, TicketResult] = PrivateAttr(default_factory=dict)
    _threads: Dict[str, threading.Thread] = PrivateAttr(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the skill.
        """
        pass

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Runs the skill.
        """
        pass

    def create_ticket_tool(self):
        @tool(f"create_{self.name}_ticket")
        def create_ticket(**kwargs: Any) -> Ticket:
            """
            Creates a ticket for the {self.name} skill.

            Args:
                **kwargs: The arguments to pass to the {self.name} skill.

            Returns:
                The ticket object.
            """
            request = TicketCreationRequest(tool=self.name, tool_args=kwargs)
            ticket_id = str(uuid.uuid4())
            ticket = Ticket(
                ticket_id=ticket_id,
                status=TicketStatus.PENDING,
                created_at=str(time.time()),
                updated_at=str(time.time()),
                request=request,
            )
            self._tickets[ticket_id] = ticket
            thread = threading.Thread(target=self._run_in_background, args=(ticket_id, request.tool_args))
            self._threads[ticket_id] = thread
            thread.start()
            return ticket

        return create_ticket

    def _run_in_background(self, ticket_id: str, tool_args: Dict[str, Any]) -> None:
        """
        Runs the skill in the background.
        """
        self._tickets[ticket_id].status = TicketStatus.RUNNING
        self._tickets[ticket_id].updated_at = str(time.time())
        try:
            result = self.run(**tool_args)
            self._results[ticket_id] = TicketResult(
                ticket_id=ticket_id,
                status=TicketStatus.COMPLETED,
                result=result,
                error=None,
            )
            self._tickets[ticket_id].status = TicketStatus.COMPLETED
        except Exception as e:
            self._results[ticket_id] = TicketResult(
                ticket_id=ticket_id,
                status=TicketStatus.FAILED,
                result=None,
                error=str(e),
            )
            self._tickets[ticket_id].status = TicketStatus.FAILED
        finally:
            self._tickets[ticket_id].updated_at = str(time.time())

    def get_ticket_status(self, ticket_id: str) -> Ticket | None:
        """
        Checks on the status of a ticket number with the skill.
        """
        return self._tickets.get(ticket_id)

    def cancel_ticket(self, ticket_id: str) -> Ticket | None:
        """
        Cancels the execution of a ticket number.
        """
        if ticket_id in self._threads:
            # Note: This is a simplistic way to "cancel" a thread.
            # It doesn't actually stop the thread, but it does prevent
            # the result from being stored.
            self._threads[ticket_id].join(timeout=0.1)
            if self._threads[ticket_id].is_alive():
                # If the thread is still alive, we can't do much more
                # to stop it without more complex mechanisms.
                pass
            del self._threads[ticket_id]
            self._tickets[ticket_id].status = TicketStatus.CANCELLED
            self._tickets[ticket_id].updated_at = str(time.time())
            return self._tickets[ticket_id]
        return None

    def get_ticket_result(self, ticket_id: str) -> TicketResult | None:
        """
        If it is finalized, to get the result of the execution.
        """
        return self._results.get(ticket_id)

    def get_all_tickets(self) -> list[Ticket]:
        """
        Returns all tickets for this skill.
        """
        return list(self._tickets.values())
