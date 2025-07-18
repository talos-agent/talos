import tweepy

def get_all_replies(api: tweepy.API, tweet_id: str) -> list[tweepy.Tweet]:
    """
    Gets all replies to a tweet.
    """
    # This is a simplified implementation. A real implementation would need to handle pagination.
    replies = tweepy.Cursor(api.search_tweets, q=f"conversation_id:{tweet_id}", tweet_mode='extended').items()
    return [reply for reply in replies]
