from disciplines.twitter_abc import Twitter


class TwitterDiscipline(Twitter):
    """
    A discipline for interacting with Twitter.
    """

    def read_posts(self, query: str) -> str:
        """
        Reads posts on Twitter that match a query.
        """
        return f"Reading posts about {query}"

    def post_tweet(self, tweet: str) -> None:
        """
        Posts a tweet.
        """
        print(f"Posting tweet: {tweet}")

    def reply_to_tweet(self, tweet_id: str, reply: str) -> None:
        """
        Replies to a tweet.
        """
        print(f"Replying to tweet {tweet_id} with: {reply}")

    def create_poll(self, question: str, options: list[str]) -> None:
        """
        Creates a poll on Twitter.
        """
        print(f"Creating poll: {question} with options: {options}")
