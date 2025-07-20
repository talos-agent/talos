from __future__ import annotations

from talos.services.base import Service
from talos.services.models import Ticket


class Router:
    """
    A simple router that uses keywords to decide which service to use.
    """

    def __init__(self, services: list[Service]):
        self.services = services
        self.service_map = {service.name: service for service in services}
        self.keywords = {
            "github": ["github", "issue", "pull request", "pr", "code"],
            "proposals": ["proposal", "vote", "snapshot"],
            "twitter": ["twitter", "tweet", "x"],
        }

    def route(self, query: str) -> Service | None:
        """
        Routes the query to the appropriate service.
        """
        for service_name, keywords in self.keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                return self.service_map.get(service_name)
        return None

    def get_service(self, service_name: str) -> Service | None:
        """
        Returns a service by name.
        """
        return self.service_map.get(service_name)

    def get_all_tickets(self) -> list[Ticket]:
        """
        Returns all tickets from all services.
        """
        tickets: list[Ticket] = []
        for service in self.services:
            tickets.extend(service.get_all_tickets())
        return tickets
