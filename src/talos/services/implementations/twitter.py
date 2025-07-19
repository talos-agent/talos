from talos.services.abstract.twitter import Twitter


class TwitterService(Twitter):
    """
    A service for interacting with Twitter.
    """

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "twitter"
