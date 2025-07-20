from talos.services.abstract.twitter import Twitter
from talos.services.models import (
    Ticket,
    TicketCreationRequest,
    TicketResult,
)


class TwitterService(Twitter):
    """
    A service for interacting with Twitter.
    """

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "twitter"

    def create_ticket(self, request: "TicketCreationRequest") -> "Ticket":
        raise NotImplementedError

    def get_ticket_status(self, ticket_id: str) -> "Ticket":
        raise NotImplementedError

    def cancel_ticket(self, ticket_id: str) -> "Ticket":
        raise NotImplementedError

    def get_ticket_result(self, ticket_id: str) -> "TicketResult":
        raise NotImplementedError
