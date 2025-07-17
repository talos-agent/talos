from talos.disciplines.abstract.gitbook import GitBook


class GitBookDiscipline(GitBook):
    """
    A discipline for interacting with GitBook.
    """

    def read_page(self, page_url: str) -> str:
        """
        Reads a GitBook page.
        """
        return f"Reading page: {page_url}"

    def update_page(self, page_url: str, content: str) -> None:
        """
        Updates a GitBook page.
        """
        print(f"Updating page {page_url} with content: {content}")
