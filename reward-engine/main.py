import time


def get_seconds_watched():
    """
    Gets the total seconds watched per user from Hasura.
    This is a placeholder for a real implementation.
    """
    return {"user1": 120, "user2": 240}


def calc_tokens(seconds):
    """
    Calculates the number of tokens to reward based on the number of seconds watched.
    This is a placeholder for a real implementation.
    """
    return seconds / 60


def send_rewards(rewards):
    """
    Sends the rewards to the TimeChain network.
    This is a placeholder for a real implementation.
    """
    print(f"Sending rewards: {rewards}")
    # w3 = Web3(Web3.HTTPProvider(os.environ["CHAIN_RPC"]))
    # ...


def main():
    while True:
        seconds_watched = get_seconds_watched()
        rewards = {user: calc_tokens(seconds) for user, seconds in seconds_watched.items()}
        send_rewards(rewards)
        time.sleep(60)


if __name__ == "__main__":
    main()
