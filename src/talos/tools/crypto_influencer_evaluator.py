import json
from datetime import datetime, timezone
from typing import Any, List

from langchain_openai import ChatOpenAI

from ..models.evaluation import EvaluationResult
from ..prompts.prompt_managers.file_prompt_manager import FilePromptManager
from .twitter_client import TwitterClient
from .twitter_evaluator import TwitterAccountEvaluator


class CryptoInfluencerEvaluator(TwitterAccountEvaluator):
    """
    Evaluates Twitter accounts specifically for crypto influencer relevance.
    Extends the base TwitterAccountEvaluator with crypto-specific metrics.
    """

    def __init__(self, twitter_client: TwitterClient, llm: Any = None, prompt_manager: FilePromptManager | None = None):
        self.twitter_client = twitter_client
        self.llm = llm or ChatOpenAI()
        if prompt_manager is None:
            import os

            prompts_dir = os.path.join(os.path.dirname(__file__), "..", "prompts")
            self.prompt_manager = FilePromptManager(prompts_dir)
        else:
            self.prompt_manager = prompt_manager
        self.crypto_keywords = [
            "bitcoin",
            "btc",
            "ethereum",
            "eth",
            "crypto",
            "cryptocurrency",
            "blockchain",
            "defi",
            "nft",
            "web3",
            "dao",
            "degen",
            "hodl",
            "altcoin",
            "trading",
            "yield",
            "staking",
            "mining",
            "wallet",
        ]

    def evaluate(self, user: Any) -> EvaluationResult:
        followers_count = user.public_metrics.get("followers_count", 0)
        following_count = user.public_metrics.get("following_count", 0)
        follower_following_ratio = followers_count / following_count if following_count > 0 else followers_count
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days
        is_verified = user.verified
        has_custom_profile_image = bool(user.profile_image_url)

        base_score = 0
        if follower_following_ratio > 1:
            base_score += 25
        if account_age_days > 365:
            base_score += 25
        if is_verified:
            base_score += 25
        if has_custom_profile_image:
            base_score += 25

        base_data = {
            "follower_following_ratio": follower_following_ratio,
            "account_age_days": account_age_days,
            "is_verified": is_verified,
            "has_custom_profile_image": has_custom_profile_image,
        }

        try:
            user_timeline = self.twitter_client.get_user_timeline(user.username)
            crypto_relevance_score = self._calculate_crypto_relevance(user_timeline)
            engagement_score = self._calculate_engagement_score(user, user_timeline)
            authenticity_score = self._calculate_authenticity_score(user)
            influence_score = self._calculate_influence_score(user)
        except Exception:
            crypto_relevance_score = 0
            engagement_score = 0
            authenticity_score = base_score // 4
            influence_score = 0
            user_timeline = []

        crypto_score = min(
            100,
            int(
                base_score * 0.2
                + crypto_relevance_score * 0.3
                + engagement_score * 0.25
                + authenticity_score * 0.15
                + influence_score * 0.1
            ),
        )

        return EvaluationResult(
            score=crypto_score,
            additional_data={
                **base_data,
                "crypto_relevance_score": crypto_relevance_score,
                "engagement_score": engagement_score,
                "authenticity_score": authenticity_score,
                "influence_score": influence_score,
                "crypto_content_percentage": self._get_crypto_content_percentage(user_timeline),
                "evaluation_type": "crypto_influencer",
            },
        )

    def _calculate_crypto_relevance(self, tweets: List[Any]) -> int:
        """Calculate how relevant the user's content is to crypto using LLM analysis (0-100)"""
        if not tweets:
            return 0

        tweets_text = "\n".join([f"- {tweet.text}" for tweet in tweets[:20]])

        try:
            prompt = self.prompt_manager.get_prompt("crypto_relevance_evaluation_prompt")
            if not prompt:
                return self._fallback_keyword_analysis(tweets)

            formatted_prompt = prompt.format(tweets_text=tweets_text)

            response = self.llm.invoke(formatted_prompt)

            try:
                content = response.content if isinstance(response.content, str) else str(response.content)
                result = json.loads(content.strip())
                crypto_focus = result.get("crypto_focus_score", 0)
                meaningfulness = result.get("meaningfulness_score", 0)

                combined_score = int(crypto_focus * 0.7 + meaningfulness * 0.3)
                return min(100, max(0, combined_score))

            except (json.JSONDecodeError, KeyError):
                return self._fallback_keyword_analysis(tweets)

        except Exception:
            return self._fallback_keyword_analysis(tweets)

    def _fallback_keyword_analysis(self, tweets: List[Any]) -> int:
        """Fallback keyword-based crypto relevance analysis"""
        if not tweets:
            return 0

        crypto_tweets = 0
        total_tweets = len(tweets)

        for tweet in tweets:
            tweet_text = tweet.text.lower()
            if any(keyword in tweet_text for keyword in self.crypto_keywords):
                crypto_tweets += 1

        crypto_percentage = (crypto_tweets / total_tweets) * 100

        if crypto_percentage >= 50:
            return 100
        elif crypto_percentage >= 30:
            return 80
        elif crypto_percentage >= 15:
            return 60
        elif crypto_percentage >= 5:
            return 40
        else:
            return 20

    def _calculate_engagement_score(self, user: Any, tweets: List[Any]) -> int:
        """Calculate engagement quality score (0-100)"""
        followers_count = user.public_metrics.get("followers_count", 0)
        if not tweets or followers_count == 0:
            return 0

        total_engagement = 0
        for tweet in tweets:
            engagement = (
                tweet.public_metrics.get("like_count", 0)
                + tweet.public_metrics.get("retweet_count", 0)
                + tweet.public_metrics.get("reply_count", 0)
            )
            total_engagement += engagement

        avg_engagement = total_engagement / len(tweets)
        engagement_rate = (avg_engagement / followers_count) * 100

        if engagement_rate >= 5:
            return 100
        elif engagement_rate >= 2:
            return 80
        elif engagement_rate >= 1:
            return 60
        elif engagement_rate >= 0.5:
            return 40
        else:
            return 20

    def _calculate_authenticity_score(self, user: Any) -> int:
        """Calculate authenticity score based on account indicators (0-100)"""
        score = 0

        account_age_days = (datetime.now(timezone.utc) - user.created_at).days
        if account_age_days > 1095:
            score += 30
        elif account_age_days > 365:
            score += 20
        elif account_age_days > 180:
            score += 10

        if user.verified:
            score += 25

        if user.profile_image_url:
            score += 15
        if user.description and len(user.description) > 20:
            score += 15
        if user.location:
            score += 10
        if user.url:
            score += 5

        return min(100, score)

    def _calculate_influence_score(self, user: Any) -> int:
        """Calculate influence score based on follower metrics (0-100)"""
        followers = user.public_metrics.get("followers_count", 0)

        if followers >= 100000:
            return 100
        elif followers >= 50000:
            return 80
        elif followers >= 10000:
            return 60
        elif followers >= 1000:
            return 40
        else:
            return 20

    def _get_crypto_content_percentage(self, tweets: List[Any]) -> float:
        """Get the percentage of tweets that contain crypto content"""
        if not tweets:
            return 0.0

        crypto_tweets = sum(
            1 for tweet in tweets if any(keyword in tweet.text.lower() for keyword in self.crypto_keywords)
        )
        return (crypto_tweets / len(tweets)) * 100
