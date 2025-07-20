
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models import BaseLanguageModel

from talos.services.base import Service
from talos.services.proposals.models import QueryResponse
class CoreAgent(Service):
    """
    A LangChain-based agent for managing conversational memory.
    """

    def __init__(
        self,
        model: BaseLanguageModel,
    ):
        self.llm = model
        self.conversation = ConversationChain(
            llm=self.llm,
            verbose=True,
            memory=ConversationBufferMemory(),
        )

    def run(self, **kwargs) -> QueryResponse:
        """
        Sends a message to the LangChain agent and returns the response.
        """
        if "query" not in kwargs:
            raise ValueError("Missing required argument: query")
        response = self.conversation.predict(input=kwargs["query"])
        return QueryResponse(answers=[response])

    @property
    def name(self) -> str:
        return "core"

    def add_dataset(self, dataset_path: str) -> None:
        """
        This method is not applicable to the conversational agent.
        """
        raise NotImplementedError(
            "The conversational agent does not support adding datasets directly."
        )
