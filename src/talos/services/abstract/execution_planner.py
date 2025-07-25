from __future__ import annotations

from abc import abstractmethod

from talos.models.proposals import Plan, Question
from talos.services.abstract.service import Service


class ExecutionPlanner(Service):
    """
    Abstract base class for a service that generates execution plans.
    """

    @property
    def name(self) -> str:
        return "execution_planner"

    @abstractmethod
    def generate_plan(self, question: Question) -> Plan:
        """
        Generates a plan for execution based on a question and feedback.
        """
        pass
