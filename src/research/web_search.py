import requests
from bs4 import BeautifulSoup
from haystack.nodes import PreProcessor
from haystack.schema import Document


def search(query: str, top_k: int = 5):
    """
    Performs a web search using DuckDuckGo and returns the top results.

    :param query: The query to search for.
    :param top_k: The number of results to return.
    :return: A list of dictionaries representing the search results.
    """
    response = requests.get("https://duckduckgo.com/html/", params={"q": query})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for link in soup.find_all("a", {"class": "result__a"}):
        results.append({"title": link.text, "url": link["href"]})
        if len(results) == top_k:
            break
    return results


def crawl(url: str):
    """
    Crawls a URL and returns the content as a Haystack Document.

    :param url: The URL to crawl.
    :return: A Haystack Document containing the content of the URL.
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
    docs = preprocessor.process([Document(content=text, meta={"url": url})])
    return docs
