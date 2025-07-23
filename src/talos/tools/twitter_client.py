import os
from abc import ABC, abstractmethod
from typing import Any

import tweepy
from textblob import TextBlob


class TwitterClient(ABC):
    @abstractmethod
    def get_user(self, username: str) -> Any:
        pass

    @abstractmethod
    def search_tweets(self, query: str) -> list[Any]:
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
        self.client = tweepy.Client(bearer_token=os.environ["TWITTER_BEARER_TOKEN"])

    def get_user(self, username: str) -> Any:
        return self.client.get_user(username=username).data

    def search_tweets(self, query: str) -> list[Any]:
        return self.client.search_recent_tweets(query=query).data

    def get_user_timeline(self, username: str) -> list[Any]:
        user = self.get_user(username)
        return self.client.get_users_tweets(id=user.id).data

    def get_user_mentions(self, username: str) -> list[Any]:
        user = self.get_user(username)
        return self.client.get_users_mentions(id=user.id).data

    def get_tweet(self, tweet_id: str) -> Any:
        return self.client.get_tweet(tweet_id).data

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
        return self.client.create_tweet(text=tweet)

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        return self.client.create_tweet(text=tweet, in_reply_to_tweet_id=tweet_id)
