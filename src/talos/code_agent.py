from abc import ABC, abstractmethod


class CodeAgent(ABC):
    """
    An abstract base class for a code agent.
    """

    @abstractmethod
    def work_on_task(self, repository: str, task: str) -> None:
        """
        Works on a task in a repository.
        """
        pass

    @abstractmethod
    def commit(self, message: str) -> None:
        """
        Commits the current changes.
        """
        pass

    @abstractmethod
    def ask_question(self, question: str) -> str:
        """
        Asks the user a question.
        """
        pass

    @abstractmethod
    def do_research(self, topic: str) -> str:
        """
        Does research on a topic.
        """
        pass
