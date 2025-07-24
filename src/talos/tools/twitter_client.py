from abc import ABC, abstractmethod
from typing import Any, Optional

import tweepy
from pydantic import model_validator
from pydantic_settings import BaseSettings
from textblob import TextBlob

from talos.models.twitter import TwitterUser, Tweet, ReferencedTweet


class PaginatedTwitterResponse:
    """
    Response object for paginated Twitter API calls.

    Aggregates data from multiple Twitter API responses into a single response-like object
    that maintains compatibility with the expected interface while providing pagination metadata.
    """

    def __init__(self, tweets: list[Any], users: list[Any], total_requests: int = 1):
        self.data = tweets
        self.includes = {"users": users}
        self.meta = {"result_count": len(tweets), "paginated": total_requests > 1, "total_requests": total_requests}
        self.errors: list[Any] = []


class TwitterConfig(BaseSettings):
    TWITTER_BEARER_TOKEN: Optional[str] = None

    @model_validator(mode="after")
    def validate_bearer_token(self):
        if not self.TWITTER_BEARER_TOKEN:
            raise ValueError("TWITTER_BEARER_TOKEN environment variable is required but not set")
        return self


class TwitterClient(ABC):
    @abstractmethod
    def get_user(self, username: str) -> TwitterUser:
        pass

    @abstractmethod
    def search_tweets(
        self, query: str, start_time: Optional[str] = None, max_tweets: int = 500
    ) -> PaginatedTwitterResponse:
        pass

    @abstractmethod
    def get_user_timeline(self, username: str) -> list[Tweet]:
        pass

    @abstractmethod
    def get_user_mentions(self, username: str) -> list[Tweet]:
        pass

    @abstractmethod
    def get_tweet(self, tweet_id: int) -> Tweet:
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

    def get_user(self, username: str) -> TwitterUser:
        response = self.client.get_user(
            username=username,
            user_fields=[
                "created_at",
                "public_metrics",
                "profile_image_url",
                "verified",
                "description",
                "location",
                "url",
            ],
        )
        from talos.models.twitter import TwitterPublicMetrics
        user_data = response.data
        return TwitterUser(
            id=int(user_data.id),
            username=user_data.username,
            name=user_data.name,
            created_at=user_data.created_at,
            profile_image_url=user_data.profile_image_url or "",
            public_metrics=TwitterPublicMetrics(**user_data.public_metrics),
            description=user_data.description,
            url=user_data.url,
            verified=getattr(user_data, 'verified', False)
        )

    def search_tweets(
        self, query: str, start_time: Optional[str] = None, max_tweets: int = 500
    ) -> PaginatedTwitterResponse:
        all_tweets: list[Any] = []
        all_users: list[Any] = []
        next_token = None
        request_count = 0

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
            request_count += 1

            if not response or not response.data:
                break

            all_tweets.extend(response.data)
            if response.includes and response.includes.get("users"):
                all_users.extend(response.includes["users"])

            if hasattr(response, "meta") and response.meta and response.meta.get("next_token"):
                next_token = response.meta["next_token"]
            else:
                break

        return PaginatedTwitterResponse(all_tweets, all_users, request_count)

    def get_user_timeline(self, username: str) -> list[Tweet]:
        user = self.get_user(username)
        if not user:
            return []
        response = self.client.get_users_tweets(
            id=user.id,
            tweet_fields=["author_id", "in_reply_to_user_id", "public_metrics", "referenced_tweets", "conversation_id", "created_at", "edit_history_tweet_ids"],
            user_fields=[
                "created_at",
                "public_metrics",
                "profile_image_url",
                "verified",
                "description",
                "location",
                "url",
            ],
        )
        return [self._convert_to_tweet_model(tweet) for tweet in (response.data or [])]

    def get_user_mentions(self, username: str) -> list[Tweet]:
        user = self.get_user(username)
        if not user:
            return []
        response = self.client.get_users_mentions(
            id=user.id,
            tweet_fields=["author_id", "in_reply_to_user_id", "public_metrics", "referenced_tweets", "conversation_id", "created_at", "edit_history_tweet_ids"],
            user_fields=[
                "created_at",
                "public_metrics",
                "profile_image_url",
                "verified",
                "description",
                "location",
                "url",
            ],
        )
        return [self._convert_to_tweet_model(tweet) for tweet in (response.data or [])]

    def get_tweet(self, tweet_id: int) -> Tweet:
        response = self.client.get_tweet(
            str(tweet_id),
            tweet_fields=["author_id", "in_reply_to_user_id", "public_metrics", "referenced_tweets", "conversation_id", "created_at", "edit_history_tweet_ids"]
        )
        return self._convert_to_tweet_model(response.data)

    def get_sentiment(self, search_query: str = "talos") -> float:
        """
        Gets the sentiment of tweets that match a search query.
        """
        response = self.search_tweets(search_query)
        sentiment = 0
        if response.data:
            for tweet in response.data:
                analysis = TextBlob(tweet.text)
                sentiment += analysis.sentiment.polarity
            return sentiment / len(response.data)
        return 0

    def post_tweet(self, tweet: str) -> Any:
        return self.client.create_tweet(text=tweet)

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> Any:
        return self.client.create_tweet(text=tweet, in_reply_to_tweet_id=tweet_id)

    def _convert_to_tweet_model(self, tweet_data: Any) -> Tweet:
        """Convert raw tweepy tweet data to Tweet BaseModel"""
        referenced_tweets = []
        if hasattr(tweet_data, 'referenced_tweets') and tweet_data.referenced_tweets:
            for ref in tweet_data.referenced_tweets:
                if isinstance(ref, dict):
                    referenced_tweets.append(ReferencedTweet(
                        type=ref.get('type', ''),
                        id=ref.get('id', 0)
                    ))
                else:
                    referenced_tweets.append(ReferencedTweet(
                        type=getattr(ref, 'type', ''),
                        id=getattr(ref, 'id', 0)
                    ))
        
        return Tweet(
            id=int(tweet_data.id),
            text=tweet_data.text,
            author_id=str(tweet_data.author_id),
            created_at=str(tweet_data.created_at) if hasattr(tweet_data, 'created_at') and tweet_data.created_at else None,
            conversation_id=str(tweet_data.conversation_id) if hasattr(tweet_data, 'conversation_id') and tweet_data.conversation_id else None,
            public_metrics=dict(tweet_data.public_metrics) if hasattr(tweet_data, 'public_metrics') and tweet_data.public_metrics else {},
            referenced_tweets=referenced_tweets if referenced_tweets else None,
            in_reply_to_user_id=str(tweet_data.in_reply_to_user_id) if hasattr(tweet_data, 'in_reply_to_user_id') and tweet_data.in_reply_to_user_id else None,
            edit_history_tweet_ids=[str(id) for id in tweet_data.edit_history_tweet_ids] if hasattr(tweet_data, 'edit_history_tweet_ids') and tweet_data.edit_history_tweet_ids else None
        )
