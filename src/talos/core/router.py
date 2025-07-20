from talos.services.base import Service


class Router:
    """
    A simple router that uses keywords to decide which service to use.
    """

    def __init__(self, services: "list[Service]"):
        self.services = {service.name: service for service in services}
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
                return self.services.get(service_name)
        return None
