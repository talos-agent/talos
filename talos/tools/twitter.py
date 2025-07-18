import tweepy


def get_api(consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str) -> tweepy.API:
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def read_posts(api: tweepy.API, query: str) -> str:
    """
    Reads posts on Twitter that match a query.
    """
    posts = api.search_tweets(q=query)
    return "\n".join([post.text for post in posts])


def post_tweet(api: tweepy.API, tweet: str) -> None:
    """
    Posts a tweet.
    """
    api.update_status(status=tweet)


def reply_to_tweet(api: tweepy.API, tweet_id: str, reply: str) -> None:
    """
    Replies to a tweet.
    """
    api.update_status(status=reply, in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)


def create_poll(api: tweepy.API, question: str, options: list[str]) -> None:
    """
    Creates a poll on Twitter.
    """
    # Tweepy does not support creating polls directly.
    # This would need to be implemented using the Twitter API directly.
    raise NotImplementedError("Creating polls is not supported by this discipline.")


def get_poll_results(api: tweepy.API, poll_id: str) -> dict:
    """
    Gets the results of a poll.
    """
    # Tweepy does not support getting poll results directly.
    # This would need to be implemented using the Twitter API directly.
    raise NotImplementedError("Getting poll results is not supported by this discipline.")


def get_all_replies(api: tweepy.API, tweet_id: str) -> list[str]:
    """
    Gets all replies to a tweet.
    """
    # This is a simplified implementation. A real implementation would need to handle pagination.
    replies = api.search_tweets(q=f"to:{api.verify_credentials().screen_name}", since_id=tweet_id)
    return [reply.text for reply in replies]


def get_follower_count(api: tweepy.API, username: str) -> int:
    """
    Gets the follower count of a user.
    """
    user = api.get_user(screen_name=username)
    return user.followers_count


def get_following_count(api: tweepy.API, username: str) -> int:
    """
    Gets the following count of a user.
    """
    user = api.get_user(screen_name=username)
    return user.friends_count


def get_tweet_engagement(api: tweepy.API, tweet_id: str) -> dict:
    """
    Gets the engagement of a tweet.
    """
    tweet = api.get_status(id=tweet_id)
    return {"likes": tweet.favorite_count, "retweets": tweet.retweet_count}
