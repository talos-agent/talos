import os
import tweepy
from abc import ABC, abstractmethod
from typing import Any

class TwitterClient(ABC):
    @abstractmethod
    def get_user(self, username: str) -> Any:
        pass

    @abstractmethod
    def search_tweets(self, query: str) -> list[Any]:
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
