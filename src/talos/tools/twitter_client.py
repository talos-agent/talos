from abc import ABC, abstractmethod
from typing import Any, Optional

import tweepy
from pydantic import model_validator
from pydantic_settings import BaseSettings
from textblob import TextBlob


class TwitterConfig(BaseSettings):
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_bearer_token(self):
        if not self.TWITTER_BEARER_TOKEN:
            raise ValueError("TWITTER_BEARER_TOKEN environment variable is required but not set")
        return self


class TwitterClient(ABC):
    @abstractmethod
    def get_user(self, username: str) -> Any:
        pass

    @abstractmethod
    def search_tweets(self, query: str, start_time: Optional[str] = None) -> Any:
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
    client: tweepy.Client
    
    def __init__(self):
        config = TwitterConfig()
        self.client = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)

    def get_user(self, username: str) -> Any:
        return self.client.get_user(username=username).data

    def search_tweets(self, query: str, start_time: Optional[str] = None) -> Any:
        all_tweets: list[Any] = []
        all_users: list[Any] = []
        next_token = None
        max_tweets = 500
        
        while len(all_tweets) < max_tweets:
            params = {
                "query": query,
                "tweet_fields": ["public_metrics", "created_at"],
                "expansions": ["author_id"],
                "user_fields": ["public_metrics"],
                "max_results": min(100, max_tweets - len(all_tweets)),
            }
            if start_time:
                params["start_time"] = start_time
            if next_token:
                params["next_token"] = next_token
                
            response = self.client.search_recent_tweets(**params)
            
            if not response or not response.data:
                break
                
            all_tweets.extend(response.data)
            if response.includes and response.includes.get("users"):
                all_users.extend(response.includes["users"])
                
            if hasattr(response, 'meta') and response.meta and response.meta.get('next_token'):
                next_token = response.meta['next_token']
            else:
                break
        
        class MockResponse:
            def __init__(self, data, includes):
                self.data = data
                self.includes = includes
        
        return MockResponse(all_tweets, {"users": all_users})

    def get_user_timeline(self, username: str) -> list[Any]:
        user = self.get_user(username)
        if not user:
            return []
        return self.client.get_users_tweets(id=user.id).data

    def get_user_mentions(self, username: str) -> list[Any]:
        user = self.get_user(username)
        if not user:
            return []
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
