import os
import tweepy
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from talos.tools.twitter import get_api, post_tweet
from talos.core.agent import CoreAgent

TWEET_ID_FILE = "tweet_id.txt"


def post_question():
    """
    Posts the question about crypto sentiment to Twitter and saves the tweet ID.
    """
    api = get_api(
        consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
        consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )
    tweet = api.update_status(status="What is your current sentiment about crypto markets today and why?")
    with open(TWEET_ID_FILE, "w") as f:
        f.write(str(tweet.id))


def analyze_sentiment():
    """
    Analyzes the sentiment of replies to the last tweet.
    """
    api = get_api(
        consumer_key=os.environ["TWITTER_CONSUMER_KEY"],
        consumer_secret=os.environ["TWITTER_CONSUMER_SECRET"],
        access_token=os.environ["TWITTER_ACCESS_TOKEN"],
        access_token_secret=os.environ["TWITTER_ACCESS_TOKEN_SECRET"],
    )

    # Get the last tweet ID
    with open(TWEET_ID_FILE, "r") as f:
        last_tweet_id = f.read().strip()

    # Get all replies to the tweet
    replies = api.search_tweets(q=f"conversation_id:{last_tweet_id}")

    # Analyze the sentiment of each reply using an LLM
    llm = OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])
    agent = CoreAgent(model=llm)

    sentiment_scores = []
    for reply in replies:
        response = agent.run(
            query=f"Analyze the sentiment of the following tweet reply and return a score from 0 to 100, where 0 is very negative, 50 is neutral, and 100 is very positive. Just return the score, nothing else.\n\nReply: {reply.text}\n\nScore:",
            params={}
        )
        score = response.answers[0]['answer']
        sentiment_scores.append(int(score))

    # Calculate the sentiment score
    if sentiment_scores:
        sentiment_score = int(sum(sentiment_scores) / len(sentiment_scores))
    else:
        sentiment_score = 50

    # Find the most interesting reply
    most_interesting_reply = None
    if replies:
        most_interesting_reply = max(replies, key=lambda r: r.user.followers_count)

    # Create the summary
    summary = f"Crypto Sentiment Score: {sentiment_score}/100\n\n"
    if most_interesting_reply:
        summary += f"Most interesting reply from @{most_interesting_reply.user.screen_name} ({most_interesting_reply.user.followers_count} followers):\n"
        summary += f"{most_interesting_reply.text}\n\n"

    # Post the results to Twitter
    post_tweet(api, summary)
