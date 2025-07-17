import os
from typing import Any, Dict, List, Optional

from haystack.document_stores import BaseDocumentStore
from haystack.utils import fetch_archive_from_http


def add_squad_dataset(document_store: BaseDocumentStore, squad_version: str = "1.1") -> None:
    """
    Adds the SQuAD dataset to the document store.

    :param document_store: The document store to add the dataset to.
    :param squad_version: The version of the SQuAD dataset to use.
    """
    squad_data_url = f"https://s3.eu-central-1.amazonaws.com/deepset.ai-farm-qa/datasets/squad_v{squad_version}.json.zip"
    squad_data_dir = "data/squad"

    fetch_archive_from_http(url=squad_data_url, output_dir=squad_data_dir)

    document_store.write_documents(
        os.path.join(squad_data_dir, f"squad_v{squad_version}.json"),
        duplicate_documents="overwrite",
    )
