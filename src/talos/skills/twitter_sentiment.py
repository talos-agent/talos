from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from talos.models.proposals import QueryResponse
from talos.prompts.prompt_manager import PromptManager
from talos.skills.base import Skill
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterSentimentSkill(Skill):
    """
    A skill for interacting with Twitter.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: PromptManager = Field(default_factory=PromptManager)
    llm: Any = Field(default_factory=ChatOpenAI)

    @property
    def name(self) -> str:
        return "twitter_sentiment_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        query = kwargs.get("query")
        start_time = kwargs.get("start_time")
        if not query:
            raise ValueError("Query must be provided.")
        response = self.twitter_client.search_tweets(query, start_time=start_time)
        if not response or not response.data:
            return QueryResponse(answers=[f"Could not find any tweets for query {query}"])

        users = {user["id"]: user for user in response.includes.get("users", [])}

        tweet_text = ""
        for tweet in response.data:
            author_id = tweet.author_id
            author = users.get(author_id)
            if author:
                tweet_text += f"- Tweet by @{author.username} (Followers: {author.public_metrics['followers_count']}): '{tweet.text}'\n"
                tweet_text += f"  - Retweets: {tweet.public_metrics['retweet_count']}\n"
                tweet_text += f"  - Likes: {tweet.public_metrics['like_count']}\n"
                tweet_text += f"  - Replies: {tweet.public_metrics['reply_count']}\n"
                tweet_text += f"  - Quotes: {tweet.public_metrics['quote_count']}\n"
            else:
                tweet_text += f"- Tweet: '{tweet.text}'\n"
                tweet_text += f"  - Retweets: {tweet.public_metrics['retweet_count']}\n"
                tweet_text += f"  - Likes: {tweet.public_metrics['like_count']}\n"
                tweet_text += f"  - Replies: {tweet.public_metrics['reply_count']}\n"
                tweet_text += f"  - Quotes: {tweet.public_metrics['quote_count']}\n"

        prompt = self.prompt_manager.get_prompt("talos_sentiment_summary_prompt")
        if not prompt:
            raise ValueError("Could not find prompt 'talos_sentiment_summary_prompt'")
        formatted_prompt = prompt.format(tweets=tweet_text)

        response = self.llm.invoke(formatted_prompt)

        return QueryResponse(answers=[response.content])
