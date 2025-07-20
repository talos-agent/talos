from enum import Enum
from typing import Optional

import tweepy
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from textblob import TextBlob

from ..models.evaluation import EvaluationResult
from .twitter_client import TweepyClient, TwitterClient
from .twitter_evaluator import DefaultTwitterAccountEvaluator, TwitterAccountEvaluator


class TwitterToolName(str, Enum):
    POST_TWEET = "post_tweet"
    GET_ALL_REPLIES = "get_all_replies"
    REPLY_TO_TWEET = "reply_to_tweet"
    GET_FOLLOWER_COUNT = "get_follower_count"
    GET_FOLLOWING_COUNT = "get_following_count"
    GET_TWEET_ENGAGEMENT = "get_tweet_engagement"
    EVALUATE_ACCOUNT = "evaluate_account"
    GET_TWEET_SENTIMENT = "get_tweet_sentiment"


class TwitterToolArgs(BaseModel):
    tool_name: TwitterToolName = Field(..., description="The name of the tool to run")
    tweet: str | None = Field(None, description="The content of the tweet")
    tweet_id: str | None = Field(None, description="The ID of the tweet")
    username: str | None = Field(None, description="The username of the user")
    search_query: str | None = Field(None, description="The search query to use")


class TwitterTool(BaseTool):
    name: str = "twitter_tool"
    description: str = "Provides tools for interacting with the Twitter API."
    args_schema: type[BaseModel] = TwitterToolArgs
    twitter_client: Optional[TwitterClient] = None
    account_evaluator: Optional[TwitterAccountEvaluator] = None

    def __init__(
        self,
        twitter_client: Optional[TwitterClient] = None,
        account_evaluator: Optional[TwitterAccountEvaluator] = None,
    ):
        super().__init__()
        self.twitter_client = twitter_client or TweepyClient()
        self.account_evaluator = account_evaluator or DefaultTwitterAccountEvaluator()

    def post_tweet(self, tweet: str) -> str:
        """Posts a tweet."""
        # This functionality is not yet migrated to the new TwitterClient
        raise NotImplementedError

    def get_all_replies(self, tweet_id: str) -> list[tweepy.Tweet]:
        """Gets all replies to a tweet."""
        # This functionality is not yet migrated to the new TwitterClient
        raise NotImplementedError

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> str:
        """Replies to a tweet."""
        # This functionality is not yet migrated to the new TwitterClient
        raise NotImplementedError

    def get_follower_count(self, username: str) -> int:
        """Gets the follower count for a user."""
        assert self.twitter_client is not None
        user = self.twitter_client.get_user(username)
        return user.followers_count

    def get_following_count(self, username: str) -> int:
        """Gets the following count for a user."""
        assert self.twitter_client is not None
        user = self.twitter_client.get_user(username)
        return user.friends_count

    def get_tweet_engagement(self, tweet_id: str) -> dict:
        """Gets the engagement for a tweet."""
        # This functionality is not yet migrated to the new TwitterClient
        raise NotImplementedError

    def evaluate_account(self, username: str) -> EvaluationResult:
        """Evaluates a Twitter account and returns a score."""
        assert self.twitter_client is not None
        assert self.account_evaluator is not None
        user = self.twitter_client.get_user(username)
        return self.account_evaluator.evaluate(user)

    def get_tweet_sentiment(self, search_query: str) -> dict:
        """Gets the sentiment of tweets that match a search query."""
        assert self.twitter_client is not None
        tweets = self.twitter_client.search_tweets(search_query)
        sentiment = {"positive": 0, "negative": 0, "neutral": 0}
        for tweet in tweets:
            analysis = TextBlob(tweet.text)
            if analysis.sentiment.polarity > 0:
                sentiment["positive"] += 1
            elif analysis.sentiment.polarity < 0:
                sentiment["negative"] += 1
            else:
                sentiment["neutral"] += 1
        return sentiment

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "post_tweet":
            return self.post_tweet(**kwargs)
        elif tool_name == "get_all_replies":
            return self.get_all_replies(**kwargs)
        elif tool_name == "reply_to_tweet":
            return self.reply_to_tweet(**kwargs)
        elif tool_name == "get_follower_count":
            return self.get_follower_count(**kwargs)
        elif tool_name == "get_following_count":
            return self.get_following_count(**kwargs)
        elif tool_name == "get_tweet_engagement":
            return self.get_tweet_engagement(**kwargs)
        elif tool_name == "evaluate_account":
            return self.evaluate_account(**kwargs)
        elif tool_name == "get_tweet_sentiment":
            return self.get_tweet_sentiment(**kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
