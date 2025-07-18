import argparse

from talos.disciplines.crypto_sentiment import analyze_sentiment, post_question


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("post-question")
    subparsers.add_parser("analyze-sentiment")

    args = parser.parse_args()

    if args.command == "post-question":
        post_question()
    elif args.command == "analyze-sentiment":
        analyze_sentiment()
    else:
        parser.print_help()
