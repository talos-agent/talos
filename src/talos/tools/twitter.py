import os
import tweepy
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class TwitterToolName(str, Enum):
    POST_TWEET = "post_tweet"
    GET_ALL_REPLIES = "get_all_replies"
    REPLY_TO_TWEET = "reply_to_tweet"
    GET_FOLLOWER_COUNT = "get_follower_count"
    GET_FOLLOWING_COUNT = "get_following_count"
    GET_TWEET_ENGAGEMENT = "get_tweet_engagement"

class TwitterToolArgs(BaseModel):
    tool_name: TwitterToolName = Field(..., description="The name of the tool to run")
    tweet: str | None = Field(None, description="The content of the tweet")
    tweet_id: str | None = Field(None, description="The ID of the tweet")
    username: str | None = Field(None, description="The username of the user")

class TwitterTool(BaseTool):
    name = "twitter_tool"
    description = "Provides tools for interacting with the Twitter API."
    args_schema: type[BaseModel] = TwitterToolArgs

    def __init__(self):
        super().__init__()
        auth = tweepy.OAuthHandler(os.environ["TWITTER_API_KEY"], os.environ["TWITTER_API_SECRET"])
        auth.set_access_token(os.environ["TWITTER_ACCESS_TOKEN"], os.environ["TWITTER_ACCESS_TOKEN_SECRET"])
        self.api = tweepy.API(auth)

    def post_tweet(self, tweet: str) -> str:
        """Posts a tweet."""
        self.api.update_status(tweet)
        return "Tweet posted successfully."

    def get_all_replies(self, tweet_id: str) -> List[tweepy.Tweet]:
        """Gets all replies to a tweet."""
        # This is a simplified implementation. A real implementation would need to handle pagination.
        replies = tweepy.Cursor(self.api.search_tweets, q=f"to:{tweet_id}", tweet_mode='extended').items()
        return [reply for reply in replies]

    def reply_to_tweet(self, tweet_id: str, tweet: str) -> str:
        """Replies to a tweet."""
        self.api.update_status(tweet, in_reply_to_status_id=tweet_id)
        return "Replied to tweet successfully."

    def get_follower_count(self, username: str) -> int:
        """Gets the follower count for a user."""
        user = self.api.get_user(screen_name=username)
        return user.followers_count

    def get_following_count(self, username: str) -> int:
        """Gets the following count for a user."""
        user = self.api.get_user(screen_name=username)
        return user.friends_count

    def get_tweet_engagement(self, tweet_id: str) -> dict:
        """Gets the engagement for a tweet."""
        tweet = self.api.get_status(tweet_id)
        return {
            "likes": tweet.favorite_count,
            "retweets": tweet.retweet_count,
        }

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
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

