from typing import Any, Dict, List, Optional

from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from agent.abc import Agent


from agent.web_search import crawl, search


class HaystackAgent(Agent):
    """
    A Haystack-based agent for question answering.
    """

    def __init__(self, model_name_or_path: str = "deepset/roberta-base-squad2"):
        self.document_store = InMemoryDocumentStore(use_bm25=True)
        self.retriever = BM25Retriever(document_store=self.document_store)
        self.reader = FARMReader(model_name_or_path=model_name_or_path, use_gpu=False)
        self.pipeline = ExtractiveQAPipeline(self.reader, self.retriever)

    def run(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if params and params.get("web_search"):
            search_results = search(query)
            documents = []
            for result in search_results:
                documents.extend(crawl(result["url"]))
            self.document_store.write_documents(documents)

        """
        Runs the agent with a given query and optional parameters.

        :param query: The query to process.
        :param params: Optional parameters for the agent.
        :return: A list of dictionaries representing the results.
        """
        if params is None:
            params = {}
        prediction = self.pipeline.run(query=query, params=params)
        return prediction["answers"]

    def add_dataset(self, dataset_path: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Adds a dataset to the agent's knowledge base.

        :param dataset_path: The path to the dataset.
        :param params: Optional parameters for adding the dataset.
        """
        if params is None:
            params = {}

        if dataset_path == "squad":
            from agent.datasets import add_squad_dataset
            add_squad_dataset(self.document_store, **params)
        else:
            # For now, we only support the SQuAD dataset.
            raise NotImplementedError("Only the SQuAD dataset is supported at this time.")
