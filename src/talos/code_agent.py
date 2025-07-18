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
    def ask_question(self, question: str) -> str:
        """
        Asks the user a question.
        """
        pass

    @abstractmethod
    def interrupt(self, message: str) -> None:
        """
        Interrupts the agent with a message.
        """
        pass

    @abstractmethod
    def halt(self) -> None:
        """
        Halts the agent.
        """
        pass

    @abstractmethod
    def resume(self) -> None:
        """
        Resumes the agent.
        """
        pass

    @abstractmethod
    def get_current_task(self) -> str | None:
        """
        Returns the current task.
        """
        pass
