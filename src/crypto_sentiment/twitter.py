import tweepy

def get_all_replies(api: tweepy.API, tweet_id: str) -> list[tweepy.Tweet]:
    """
    Gets all replies to a tweet.
    """
    # This is a simplified implementation. A real implementation would need to handle pagination.
    replies = tweepy.Cursor(api.search_tweets, q=f"to:{api.verify_credentials().screen_name}", since_id=tweet_id, tweet_mode='extended').items()
    return [reply for reply in replies if reply.in_reply_to_status_id == int(tweet_id)]
