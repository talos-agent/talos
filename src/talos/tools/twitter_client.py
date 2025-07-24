from abc import ABC, abstractmethod
from typing import Any, Optional

import tweepy
from pydantic import Field, PrivateAttr, SecretStr
from pydantic_settings import BaseSettings
from textblob import TextBlob


class TwitterClient(ABC):
    @abstractmethod
    def get_user(self, username: str) -> Any:
        pass

    @abstractmethod
    def search_tweets(self, query: str) -> Any:
        pass

    @abstractmethod
    def get_user_timeline(self, username: str) -> list[Any]:
        pass

    @abstractmethod
    def get_user_mentions(self, username: str) -> list[Any]:
        pass

    @abstractmethod
    def get_tweet(self, tweet_id: str) -> Any:
        pass

    @abstractmethod
    def get_sentiment(self, search_query: str = "talos") -> float:
        pass

    @abstractmethod
    def post_tweet(self, tweet: str) -> Any:
        pass

    @abstractmethod
    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        pass


class TweepyClient(BaseSettings, TwitterClient):
    TWITTER_BEARER_TOKEN: Optional[SecretStr] = Field(None, env="TWITTER_BEARER_TOKEN")

    _client: tweepy.Client = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        if not self.TWITTER_BEARER_TOKEN:
            raise ValueError("TWITTER_BEARER_TOKEN is not set")
        self._client = tweepy.Client(bearer_token=self.TWITTER_BEARER_TOKEN.get_secret_value())

    def get_user(self, username: str) -> Any:
        return self._client.get_user(username=username).data

    def search_tweets(self, query: str) -> Any:
        return self._client.search_recent_tweets(
            query=query,
            tweet_fields=["public_metrics"],
            expansions=["author_id"],
            user_fields=["public_metrics"],
        )

    def get_user_timeline(self, username: str) -> list[Any]:
        user = self.get_user(username)
        if not user:
            return []
        return self._client.get_users_tweets(id=user.id).data

    def get_user_mentions(self, username: str) -> list[Any]:
        user = self.get_user(username)
        if not user:
            return []
        return self._client.get_users_mentions(id=user.id).data

    def get_tweet(self, tweet_id: str) -> Any:
        return self._client.get_tweet(tweet_id).data

    def get_sentiment(self, search_query: str = "talos") -> float:
        """
        Gets the sentiment of tweets that match a search query.
        """
        tweets = self.search_tweets(search_query)
        sentiment = 0
        if tweets:
            for tweet in tweets:
                analysis = TextBlob(tweet.text)
                sentiment += analysis.sentiment.polarity
            return sentiment / len(tweets)
        return 0

    def post_tweet(self, tweet: str) -> Any:
        return self._client.create_tweet(text=tweet)

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        return self._client.create_tweet(text=tweet, in_reply_to_tweet_id=tweet_id)
