from abc import ABC, abstractmethod
from talos.services.models import (
    Ticket,
    TicketCreationRequest,
    TicketResult,
)


class Service(ABC):
    """
    An abstract base class for a service.
    Services are a way to organize and manage the agent's actions.
    They are LLM driven actions, which means that they are powered by a
    language model. This allows them to be more flexible and powerful
    than traditional tools.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the service.
        """
        pass

    @abstractmethod
    def create_ticket(self, request: TicketCreationRequest) -> Ticket:
        """
        Creates a ticket for a long-running process.
        This should be non-blocking.
        """
        pass

    @abstractmethod
    def get_ticket_status(self, ticket_id: str) -> Ticket:
        """
        Checks on the status of a ticket number with the service.
        """
        pass

    @abstractmethod
    def cancel_ticket(self, ticket_id: str) -> Ticket:
        """
        Cancels the execution of a ticket number.
        """
        pass

    @abstractmethod
    def get_ticket_result(self, ticket_id: str) -> TicketResult:
        """
        If it is finalized, to get the result of the execution.
        """
        pass
