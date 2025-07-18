import tweepy
from talos.tools.basetool import Tool


class TweepyTool(Tool):
    """
    A tool for interacting with Twitter using Tweepy.
    """

    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    @property
    def name(self) -> str:
        return "tweepy"

    def run(self, **kwargs) -> str:
        """
        Runs the tool.
        """
        command = kwargs.get("command")
        if not command:
            return "No command specified. Available commands are: read_posts, post_tweet, reply_to_tweet, create_poll, get_poll_results, get_all_replies, get_follower_count, get_following_count, get_tweet_engagement"
        if command == "read_posts":
            return self.read_posts(kwargs.get("query"))
        elif command == "post_tweet":
            self.post_tweet(kwargs.get("tweet"))
            return "Tweet posted successfully."
        elif command == "reply_to_tweet":
            self.reply_to_tweet(kwargs.get("tweet_id"), kwargs.get("reply"))
            return "Replied to tweet successfully."
        elif command == "create_poll":
            self.create_poll(kwargs.get("question"), kwargs.get("options"))
            return "Poll created successfully."
        elif command == "get_poll_results":
            return self.get_poll_results(kwargs.get("poll_id"))
        elif command == "get_all_replies":
            return self.get_all_replies(kwargs.get("tweet_id"))
        elif command == "get_follower_count":
            return self.get_follower_count(kwargs.get("username"))
        elif command == "get_following_count":
            return self.get_following_count(kwargs.get("username"))
        elif command == "get_tweet_engagement":
            return self.get_tweet_engagement(kwargs.get("tweet_id"))
        else:
            return "Invalid command."


    def read_posts(self, query: str) -> str:
        """
        Reads posts on Twitter that match a query.
        """
        posts = self.api.search_tweets(q=query)
        return "\n".join([post.text for post in posts])

    def post_tweet(self, tweet: str) -> None:
        """
        Posts a tweet.
        """
        self.api.update_status(status=tweet)

    def reply_to_tweet(self, tweet_id: str, reply: str) -> None:
        """
        Replies to a tweet.
        """
        self.api.update_status(status=reply, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)

    def create_poll(self, question: str, options: list[str]) -> None:
        """
        Creates a poll on Twitter.
        """
        # Tweepy does not support creating polls directly.
        # This would need to be implemented using the Twitter API directly.
        raise NotImplementedError("Creating polls is not supported by this discipline.")

    def get_poll_results(self, poll_id: str) -> dict:
        """
        Gets the results of a poll.
        """
        # Tweepy does not support getting poll results directly.
        # This would need to be implemented using the Twitter API directly.
        raise NotImplementedError("Getting poll results is not supported by this discipline.")

    def get_all_replies(self, tweet_id: str) -> list[str]:
        """
        Gets all replies to a tweet.
        """
        # This is a simplified implementation. A real implementation would need to handle pagination.
        replies = self.api.search_tweets(q=f"to:{self.api.verify_credentials().screen_name}", since_id=tweet_id)
        return [reply.text for reply in replies]

    def get_follower_count(self, username: str) -> int:
        """
        Gets the follower count of a user.
        """
        user = self.api.get_user(screen_name=username)
        return user.followers_count

    def get_following_count(self, username: str) -> int:
        """
        Gets the following count of a user.
        """
        user = self.api.get_user(screen_name=username)
        return user.friends_count

    def get_tweet_engagement(self, tweet_id: str) -> dict:
        """
        Gets the engagement of a tweet.
        """
        tweet = self.api.get_status(id=tweet_id)
        return {"likes": tweet.favorite_count, "retweets": tweet.retweet_count}
