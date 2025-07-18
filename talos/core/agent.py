from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI

from talos.disciplines.base import Discipline
from talos.disciplines.proposals.models import AddDatasetParams, QueryResponse, RunParams


class CoreAgent(Discipline):
    """
    A LangChain-based agent for managing conversational memory.
    """

    def __init__(
        self,
        model: OpenAI,
    ):
        self.llm = model
        self.conversation = ConversationChain(
            llm=self.llm,
            verbose=True,
            memory=ConversationBufferMemory(),
        )

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Sends a message to the LangChain agent and returns the response.
        """
        response = self.conversation.predict(input=query)
        return QueryResponse(answers=[{"answer": response, "score": 1.0}])

    @property
    def name(self) -> str:
        return "core"

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        This method is not applicable to the conversational agent.
        """
        raise NotImplementedError(
            "The conversational agent does not support adding datasets directly."
        )
