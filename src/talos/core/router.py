from __future__ import annotations

from talos.models.services import Ticket
from talos.services.abstract.service import Service
from talos.skills.base import Skill


class Router:
    """
    A simple router that uses keywords to decide which service to use.
    """

    def __init__(self, services: list[Service], skills: list[Skill]):
        self.services = services
        self.skills = skills
        self.service_map = {service.name: service for service in services}
        self.skill_map = {skill.name: skill for skill in skills}
        self.keywords = {
            "github": ["github", "issue", "pull request", "pr", "code"],
            "pr_review_skill": ["pr review", "pull request review", "code review", "review pr"],
            "proposals": ["proposal", "vote", "snapshot"],
            "twitter": ["twitter", "tweet", "x"],
            "twitter_influencer": [
                "crypto influencer",
                "influencer analysis",
                "crypto twitter",
                "influencer evaluation",
            ],
            "twitter_influence_skill": [
                "twitter influence",
                "influence evaluation",
                "account influence",
                "twitter perception",
                "influence analysis",
                "social influence",
                "twitter credibility",
            ],
        }

    def route(self, query: str) -> Service | Skill | None:
        """
        Routes the query to the appropriate service or skill.
        """
        for service_name, keywords in self.keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                if service_name in self.service_map:
                    return self.service_map.get(service_name)
                elif service_name in self.skill_map:
                    return self.skill_map.get(service_name)
        return None

    def get_service(self, service_name: str) -> Service | None:
        """
        Returns a service by name.
        """
        return self.service_map.get(service_name)

    def get_skill(self, skill_name: str) -> Skill | None:
        """
        Returns a skill by name.
        """
        return self.skill_map.get(skill_name)

    def get_all_tickets(self) -> list[Ticket]:
        """
        Returns all tickets from all skills.
        """
        tickets: list[Ticket] = []
        for skill in self.skills:
            tickets.extend(skill.get_all_tickets())
        return tickets
