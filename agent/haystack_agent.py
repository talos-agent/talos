from typing import Any, Dict, List, Optional

from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from agent.abc import Agent


from agent.web_search import crawl, search


class HaystackAgent(Agent):
    """
    A Haystack-based agent for question answering.
    """

    def __init__(self, model_name_or_path: str = "deepset/roberta-base-squad2"):
        self.document_store = InMemoryDocumentStore()
        self.retriever = BM25Retriever(document_store=self.document_store)
        self.reader = FARMReader(model_name_or_path=model_name_or_path, use_gpu=False)
        self.pipeline = ExtractiveQAPipeline(self.reader, self.retriever)

from agent.models import AddDatasetParams, QueryResponse, RunParams


    def run(self, query: str, params: RunParams) -> QueryResponse:
        if params.web_search:
            search_results = search(query)
            documents = []
            for result in search_results:
                documents.extend(crawl(result["url"]))
            self.document_store.write_documents(documents)

        prediction = self.pipeline.run(query=query, params=params.extra_params)
        return QueryResponse(**prediction)

    def add_dataset(self, dataset_path: str, params: AddDatasetParams) -> None:
        from agent.processing import process_pdf, process_website
        if dataset_path.startswith("http"):
            documents = process_website(dataset_path)
        elif dataset_path.endswith(".pdf"):
            documents = process_pdf(dataset_path)
        else:
            raise NotImplementedError("Only PDF and website sources are supported at this time.")

        self.document_store.write_documents(documents)
