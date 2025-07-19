import tweepy

def get_all_replies(api: tweepy.API, tweet_id: str) -> list[dict]:
    """
    Gets all replies to a tweet and returns a list of dictionaries, where each dictionary contains the tweet text and the follower count of the author.
    """
    # This is a simplified implementation. A real implementation would need to handle pagination.
    replies = tweepy.Cursor(api.search_tweets, q=f"conversation_id:{tweet_id}", tweet_mode='extended').items()
    return [{"text": reply.full_text, "followers": reply.user.followers_count} for reply in replies]
