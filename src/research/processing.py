import requests
from bs4 import BeautifulSoup
from haystack.nodes import PreProcessor
from haystack.schema import Document
from pypdf import PdfReader


def process_pdf(file_path: str) -> list[Document]:
    """
    Processes a PDF file and returns a list of Haystack Documents.

    :param file_path: The path to the PDF file.
    :return: A list of Haystack Documents.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="word",
        split_length=200,
        split_respect_sentence_boundary=True,
    )
    docs = preprocessor.process([Document(content=text, meta={"source": file_path})])
    return docs


def process_website(url: str) -> list[Document]:
    """
    Processes a website and returns a list of Haystack Documents.

    :param url: The URL of the website.
    :return: A list of Haystack Documents.
    """
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()

    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=True,
        split_by="word",
        split_length=200,
        split_respect_sentence_boundary=True,
    )
    docs = preprocessor.process([Document(content=text, meta={"source": url})])
    return docs
