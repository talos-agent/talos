import threading
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from talos.services.models import (
    Ticket,
    TicketCreationRequest,
    TicketResult,
    TicketStatus,
)


class Service(ABC):
    """
    An abstract base class for a service.
    Services are a way to organize and manage the agent's actions.
    They are LLM driven actions, which means that they are powered by a
    language model. This allows them to be more flexible and powerful
    than traditional tools.
    """

    def __init__(self) -> None:
        self.tickets: Dict[str, Ticket] = {}
        self.results: Dict[str, TicketResult] = {}
        self.threads: Dict[str, threading.Thread] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass

    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """
        Runs the service.
        """
        pass

    def create_ticket_tool(self):
        def create_ticket(**kwargs: Any) -> Ticket:
            """
            Creates a ticket for a long-running process.
            This should be non-blocking.
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
            self.tickets[ticket_id] = ticket
            thread = threading.Thread(
                target=self._run_in_background, args=(ticket_id, request.tool_args)
            )
            self.threads[ticket_id] = thread
            thread.start()
            return ticket

        create_ticket.__name__ = f"create_{self.name}_ticket"
        create_ticket.__doc__ = f"""
        Creates a ticket for the {self.name} service.

        Args:
            **kwargs: The arguments to pass to the {self.name} service.

        Returns:
            The ticket object.
        """

        return create_ticket

    def _run_in_background(self, ticket_id: str, tool_args: Dict[str, Any]) -> None:
        """
        Runs the service in the background.
        """
        self.tickets[ticket_id].status = TicketStatus.RUNNING
        self.tickets[ticket_id].updated_at = str(time.time())
        try:
            result = self.run(**tool_args)
            self.results[ticket_id] = TicketResult(
                ticket_id=ticket_id,
                status=TicketStatus.COMPLETED,
                result=result,
                error=None,
            )
            self.tickets[ticket_id].status = TicketStatus.COMPLETED
        except Exception as e:
            self.results[ticket_id] = TicketResult(
                ticket_id=ticket_id,
                status=TicketStatus.FAILED,
                result=None,
                error=str(e),
            )
            self.tickets[ticket_id].status = TicketStatus.FAILED
        finally:
            self.tickets[ticket_id].updated_at = str(time.time())

    def get_ticket_status(self, ticket_id: str) -> Optional[Ticket]:
        """
        Checks on the status of a ticket number with the service.
        """
        return self.tickets.get(ticket_id)

    def cancel_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Cancels the execution of a ticket number.
        """
        if ticket_id in self.threads:
            # Note: This is a simplistic way to "cancel" a thread.
            # It doesn't actually stop the thread, but it does prevent
            # the result from being stored.
            self.threads[ticket_id].join(timeout=0.1)
            if self.threads[ticket_id].is_alive():
                # If the thread is still alive, we can't do much more
                # to stop it without more complex mechanisms.
                pass
            del self.threads[ticket_id]
            self.tickets[ticket_id].status = TicketStatus.CANCELLED
            self.tickets[ticket_id].updated_at = str(time.time())
            return self.tickets[ticket_id]
        return None

    def get_ticket_result(self, ticket_id: str) -> Optional[TicketResult]:
        """
        If it is finalized, to get the result of the execution.
        """
        return self.results.get(ticket_id)

    def get_all_tickets(self) -> list[Ticket]:
        """
        Returns all tickets for this service.
        """
        return list(self.tickets.values())
