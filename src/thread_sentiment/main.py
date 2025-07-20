import os

import tweepy
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from talos.core.agent import Agent
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager

from .twitter import get_all_replies

prompt_manager = FilePromptManager("src/talos/prompts")


def post_question():
    """
    Posts a tweet to Twitter asking for crypto market sentiment.
    The tweet ID is saved to a file to be used by the analysis function.
    """
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    tweet = api.update_status("What is your current sentiment about crypto markets today and why?")

    with open("tweet_id.txt", "w") as f:
        f.write(str(tweet.id))


def analyze_sentiment(tweets: list[dict]) -> str:
    """
    Analyzes the sentiment of a list of tweets and returns a summary.
    """
    agent = Agent(model=ChatOpenAI(model="gpt-4"), prompt_manager=prompt_manager, schema=None)
    response = agent.run(message="", history=[], tweets=str(tweets))
    if isinstance(response, AIMessage):
        return str(response.content)
    return str(response)


def analyze_and_post_sentiment():
    """
    Analyzes the replies to the tweet posted by post_question() and posts a sentiment analysis summary.
    """
    consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
    consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    with open("tweet_id.txt", "r") as f:
        tweet_id = f.read()

    tweets = get_all_replies(api, tweet_id)
    sentiment = analyze_sentiment(tweets)

    api.update_status(sentiment)
