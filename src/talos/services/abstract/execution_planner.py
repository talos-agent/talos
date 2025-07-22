from __future__ import annotations

from abc import abstractmethod

from talos.services.abstract.service import Service
from talos.models.proposals.models import Plan, Question


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
