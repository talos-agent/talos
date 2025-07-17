
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI

from research.abc import Agent
from research.models import AddDatasetParams, QueryResponse, RunParams


class LangChainConversationalAgent(Agent):
    """
    A LangChain-based agent for managing conversational memory.
    """

    def __init__(
        self,
        openai_api_key: str,
        model_name: str = "text-davinci-003",
        temperature: float = 0.0,
    ):
        self.llm = OpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=openai_api_key,
        )
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

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        This method is not applicable to the conversational agent.
        """
        raise NotImplementedError(
            "The conversational agent does not support adding datasets directly."
        )
