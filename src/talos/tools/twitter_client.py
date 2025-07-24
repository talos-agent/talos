import os
from abc import ABC, abstractmethod
from typing import Any, Optional

import tweepy
from pydantic_settings import BaseSettings
from textblob import TextBlob


class TwitterConfig(BaseSettings):
    TWITTER_BEARER_TOKEN: Optional[str] = None


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


class TweepyClient(TwitterClient):
    def __init__(self):
        config = TwitterConfig()
        if config.TWITTER_BEARER_TOKEN:
            self.client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)
        else:
            self.client = None

    def get_user(self, username: str) -> Any:
        if not self.client:
            return None
        return self.client.get_user(username=username).data

    def search_tweets(self, query: str) -> Any:
        if not self.client:
            return None
        return self.client.search_recent_tweets(
            query=query,
            tweet_fields=["public_metrics"],
            expansions=["author_id"],
            user_fields=["public_metrics"],
        )

    def get_user_timeline(self, username: str) -> list[Any]:
        if not self.client:
            return []
        user = self.get_user(username)
        if not user:
            return []
        return self.client.get_users_tweets(id=user.id).data

    def get_user_mentions(self, username: str) -> list[Any]:
        if not self.client:
            return []
        user = self.get_user(username)
        if not user:
            return []
        return self.client.get_users_mentions(id=user.id).data

    def get_tweet(self, tweet_id: str) -> Any:
        if not self.client:
            return None
        return self.client.get_tweet(tweet_id).data

    def get_sentiment(self, search_query: str = "talos") -> float:
        """
        Gets the sentiment of tweets that match a search query.
        """
        if not self.client:
            return 0.0
        tweets = self.search_tweets(search_query)
        sentiment = 0
        if tweets:
            for tweet in tweets:
                analysis = TextBlob(tweet.text)
                sentiment += analysis.sentiment.polarity
            return sentiment / len(tweets)
        return 0

    def post_tweet(self, tweet: str) -> Any:
        if not self.client:
            return None
        return self.client.create_tweet(text=tweet)

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        if not self.client:
            return None
        return self.client.create_tweet(text=tweet, in_reply_to_tweet_id=tweet_id)
