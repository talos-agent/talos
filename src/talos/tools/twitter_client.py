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
        auth = tweepy.OAuthHandler(os.environ["TWITTER_API_KEY"], os.environ["TWITTER_API_SECRET"])
        auth.set_access_token(os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"])
        self.api = tweepy.API(auth)

    def get_user(self, username: str) -> Any:
        return self.api.get_user(screen_name=username)

    def search_tweets(self, query: str) -> list[Any]:
        return self.api.search_tweets(q=query, count=100)

    def get_user_timeline(self, username: str) -> list[Any]:
        return self.api.user_timeline(screen_name=username, count=100)

    def get_user_mentions(self, username: str) -> list[Any]:
        return self.api.mentions_timeline(screen_name=username, count=100)

    def get_tweet(self, tweet_id: str) -> Any:
        return self.api.get_status(tweet_id)

    def get_sentiment(self, search_query: str = "talos") -> float:
        """
        Gets the sentiment of tweets that match a search query.
        """
        tweets = self.search_tweets(search_query)
        sentiment = 0
        for tweet in tweets:
            analysis = TextBlob(tweet.text)
            sentiment += analysis.sentiment.polarity
        return sentiment / len(tweets) if tweets else 0

    def post_tweet(self, tweet: str) -> Any:
        return self.api.update_status(tweet)

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        return self.api.update_status(tweet, in_reply_to_status_id=tweet_id)
