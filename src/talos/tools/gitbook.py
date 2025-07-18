import requests

def get_api(api_key: str) -> requests.Session:
    """
    Returns a requests session with the GitBook API key.
    """
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {api_key}"})
    return session


def read_page(session: requests.Session, page_url: str) -> str:
    """
    Reads a GitBook page.
    """
    response = session.get(page_url)
    response.raise_for_status()
    return response.text


def update_page(session: requests.Session, page_url: str, content: str) -> None:
    """
    Updates a GitBook page.
    """
    response = session.put(page_url, json={"content": content})
    response.raise_for_status()
