
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from research.abc import Agent
from research.models import AddDatasetParams, QueryResponse, RunParams


class LangChainAgent(Agent):
    """
    A LangChain-based agent for question answering.
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
        self.vector_store = None

    def run(self, query: str, params: RunParams) -> QueryResponse:
        """
        Runs the agent with a given query and optional parameters.
        """
        if self.vector_store is None:
            raise ValueError("No dataset has been added. Please add a dataset first.")

        prompt = PromptTemplate(
            template="""Answer the question based only on the following context:

{context}

Question: {input}""",
            input_variables=["context", "input"],
        )
        document_chain = create_stuff_documents_chain(self.llm, prompt)
        retriever = self.vector_store.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        response = retrieval_chain.invoke({"input": query})
        return QueryResponse(answers=[{"answer": response["answer"], "score": 1.0}])

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        """
        Adds a dataset to the agent's knowledge base.
        """
        if dataset_path.startswith("http"):
            loader = WebBaseLoader(dataset_path)
        elif dataset_path.endswith(".pdf"):
            loader = PyPDFLoader(dataset_path)
        else:
            raise NotImplementedError("Only PDF and website sources are supported at this time.")

        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings(openai_api_key=self.llm.openai_api_key)
        self.vector_store = FAISS.from_documents(texts, embeddings)
