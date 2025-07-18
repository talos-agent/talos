import os
import tweepy
from .twitter import get_all_replies

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

from src.talos.agent import Agent

def analyze_sentiment(tweets: list[str]) -> str:
    """
    Analyzes the sentiment of a list of tweets and returns a summary.
    """
    agent = Agent(model="gpt-4", prompt="{messages}")
    # TODO: The prompt is super basic and needs to be improved.
    # We also need to define a schema for the output.
    response = agent.run(f"Analyze the sentiment of these tweets and provide a summary:\n{tweets}")
    return response.content


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
