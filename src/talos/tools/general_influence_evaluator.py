import json
from datetime import datetime, timezone
from typing import Any, List

from langchain_openai import ChatOpenAI

from ..models.evaluation import EvaluationResult
from ..prompts.prompt_managers.file_prompt_manager import FilePromptManager
from .twitter_client import TwitterClient
from .twitter_evaluator import TwitterAccountEvaluator


class GeneralInfluenceEvaluator(TwitterAccountEvaluator):
    """
    Evaluates Twitter accounts for general influence and perception.
    Assesses follower metrics, engagement rates, authenticity, and credibility
    to determine overall influence perception.
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
            content_quality_score = self._calculate_content_quality_score(user_timeline)
            engagement_score = self._calculate_engagement_score(user, user_timeline)
            authenticity_score = self._calculate_authenticity_score(user, user_timeline)
            influence_score = self._calculate_influence_score(user)
            credibility_score = self._calculate_credibility_score(user, user_timeline)
        except Exception:
            content_quality_score = 0
            engagement_score = 0
            authenticity_score = base_score // 4
            influence_score = 0
            credibility_score = 0
            user_timeline = []

        overall_score = min(
            100,
            int(
                base_score * 0.15
                + content_quality_score * 0.20
                + engagement_score * 0.25
                + authenticity_score * 0.15
                + influence_score * 0.15
                + credibility_score * 0.10
            ),
        )

        return EvaluationResult(
            score=overall_score,
            additional_data={
                **base_data,
                "content_quality_score": content_quality_score,
                "engagement_score": engagement_score,
                "authenticity_score": authenticity_score,
                "influence_score": influence_score,
                "credibility_score": credibility_score,
                "total_tweets_analyzed": len(user_timeline),
                "evaluation_type": "general_influence",
            },
        )

    def _calculate_content_quality_score(self, tweets: List[Any]) -> int:
        """Calculate content quality score using LLM analysis (0-100)"""
        if not tweets:
            return 0

        tweets_text = "\n".join([f"- {tweet.text}" for tweet in tweets[:20]])

        try:
            prompt = self.prompt_manager.get_prompt("general_influence_content_quality_prompt")
            if not prompt:
                return self._fallback_content_analysis(tweets)

            formatted_prompt = prompt.format(tweets_text=tweets_text)

            response = self.llm.invoke(formatted_prompt)

            try:
                content = response.content if isinstance(response.content, str) else str(response.content)
                result = json.loads(content.strip())
                quality_score = result.get("content_quality_score", 0)
                originality_score = result.get("originality_score", 0)

                combined_score = int(quality_score * 0.6 + originality_score * 0.4)
                return min(100, max(0, combined_score))

            except (json.JSONDecodeError, KeyError):
                return self._fallback_content_analysis(tweets)

        except Exception:
            return self._fallback_content_analysis(tweets)

    def _fallback_content_analysis(self, tweets: List[Any]) -> int:
        """Fallback content quality analysis based on basic metrics"""
        if not tweets:
            return 0

        total_length = sum(len(tweet.text) for tweet in tweets)
        avg_length = total_length / len(tweets)
        
        if avg_length >= 200:
            length_score = 80
        elif avg_length >= 100:
            length_score = 60
        elif avg_length >= 50:
            length_score = 40
        else:
            length_score = 20

        original_tweets = [tweet for tweet in tweets if not tweet.text.startswith("RT @")]
        originality_ratio = len(original_tweets) / len(tweets) if tweets else 0
        
        if originality_ratio >= 0.8:
            originality_score = 80
        elif originality_ratio >= 0.6:
            originality_score = 60
        elif originality_ratio >= 0.4:
            originality_score = 40
        else:
            originality_score = 20

        return int(length_score * 0.6 + originality_score * 0.4)

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

    def _calculate_authenticity_score(self, user: Any, tweets: List[Any] | None = None) -> int:
        """Calculate enhanced authenticity score with advanced bot detection (0-100)"""
        if tweets is None:
            tweets = []
        
        base_score = self._calculate_base_authenticity(user)
        
        engagement_score = self._calculate_engagement_authenticity(user, tweets)
        
        content_score = self._calculate_content_authenticity(tweets)
        
        temporal_score = self._calculate_temporal_authenticity(tweets)
        
        composite_score = int(
            base_score * 0.40 +
            engagement_score * 0.25 +
            content_score * 0.20 +
            temporal_score * 0.15
        )
        
        return min(100, max(0, composite_score))

    def _calculate_base_authenticity(self, user: Any) -> int:
        """Calculate base authenticity score from account indicators (0-100)"""
        score = 0
        
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days
        if account_age_days > 1825:  # 5+ years
            score += 35
        elif account_age_days > 1095:  # 3+ years  
            score += 30
        elif account_age_days > 730:   # 2+ years
            score += 25
        elif account_age_days > 365:   # 1+ year
            score += 20
        elif account_age_days > 180:   # 6+ months
            score += 10
        elif account_age_days < 30:    # Suspicious new accounts
            score -= 10
        
        if user.verified:
            score += 25
        
        if user.profile_image_url and not user.profile_image_url.endswith('default_profile_images/'):
            score += 15
        if user.description and len(user.description) > 20:
            score += 10
        if user.location:
            score += 5
        if user.url:
            score += 5
        
        following = user.public_metrics.get("following_count", 0)
        
        if following > 50000:
            score -= 15
        elif following > 10000:
            score -= 5
            
        return min(100, max(0, score))

    def _calculate_engagement_authenticity(self, user: Any, tweets: List[Any]) -> int:
        """Analyze engagement patterns for authenticity indicators (0-100)"""
        if not tweets:
            return 50  # Neutral score when no data available
        
        score = 50  # Start with neutral
        followers = user.public_metrics.get("followers_count", 0)
        
        if followers == 0:
            return 20  # Very suspicious
        
        engagement_rates = []
        for tweet in tweets[:20]:  # Analyze recent tweets
            engagement = (
                tweet.public_metrics.get("like_count", 0) +
                tweet.public_metrics.get("retweet_count", 0) +
                tweet.public_metrics.get("reply_count", 0)
            )
            rate = (engagement / followers) * 100
            engagement_rates.append(rate)
        
        if engagement_rates:
            avg_rate = sum(engagement_rates) / len(engagement_rates)
            rate_variance = sum((r - avg_rate) ** 2 for r in engagement_rates) / len(engagement_rates)
            
            if rate_variance < 0.1:  # Very consistent
                score += 20
            elif rate_variance < 1.0:  # Reasonably consistent
                score += 10
            elif rate_variance > 10.0:  # Highly inconsistent (suspicious)
                score -= 15
            
            if avg_rate > 10:  # >10% engagement rate is unusual
                score -= 20
            elif avg_rate > 5:
                score -= 10
            elif avg_rate < 0.1:  # Very low engagement also suspicious
                score -= 10
        
        like_counts = [t.public_metrics.get("like_count", 0) for t in tweets[:10]]
        retweet_counts = [t.public_metrics.get("retweet_count", 0) for t in tweets[:10]]
        
        if sum(like_counts) > 0 and sum(retweet_counts) > 0:
            like_rt_ratio = sum(like_counts) / sum(retweet_counts)
            if 2 <= like_rt_ratio <= 20:  # Normal range
                score += 15
            else:  # Unusual ratios
                score -= 10
        
        return min(100, max(0, score))

    def _calculate_content_authenticity(self, tweets: List[Any]) -> int:
        """Analyze content patterns for authenticity indicators (0-100)"""
        if not tweets:
            return 50  # Neutral score when no data available
        
        score = 50  # Start with neutral
        
        tweet_texts = [tweet.text for tweet in tweets[:20]]
        unique_texts = set(tweet_texts)
        
        if len(tweet_texts) > 0:
            uniqueness_ratio = len(unique_texts) / len(tweet_texts)
            if uniqueness_ratio > 0.9:  # High uniqueness
                score += 25
            elif uniqueness_ratio > 0.7:
                score += 15
            elif uniqueness_ratio < 0.5:  # Low uniqueness (suspicious)
                score -= 20
        
        original_tweets = [t for t in tweets if not t.text.startswith("RT @")]
        
        if len(tweets) > 0:
            original_ratio = len(original_tweets) / len(tweets)
            if original_ratio > 0.7:  # Mostly original content
                score += 20
            elif original_ratio < 0.3:  # Mostly retweets (suspicious)
                score -= 15
        
        hashtag_counts = []
        for tweet in tweets[:10]:
            hashtag_count = tweet.text.count('#')
            hashtag_counts.append(hashtag_count)
        
        if hashtag_counts:
            avg_hashtags = sum(hashtag_counts) / len(hashtag_counts)
            if avg_hashtags > 5:  # Excessive hashtag use
                score -= 15
            elif 1 <= avg_hashtags <= 3:  # Normal hashtag use
                score += 10
        
        if original_tweets:
            avg_length = sum(len(t.text) for t in original_tweets) / len(original_tweets)
            if avg_length > 100:  # Longer, more thoughtful tweets
                score += 15
            elif avg_length < 30:  # Very short tweets (suspicious)
                score -= 10
        
        return min(100, max(0, score))

    def _calculate_temporal_authenticity(self, tweets: List[Any]) -> int:
        """Analyze temporal posting patterns for authenticity indicators (0-100)"""
        if not tweets:
            return 50  # Neutral score when no data available
        
        score = 50  # Start with neutral
        
        # Analyze posting frequency
        tweets_with_dates = [t for t in tweets if t.created_at]
        if len(tweets_with_dates) < 2:
            return score
        
        timestamps = []
        for tweet in tweets_with_dates[:20]:
            try:
                if isinstance(tweet.created_at, str):
                    timestamp = datetime.fromisoformat(tweet.created_at.replace('Z', '+00:00'))
                else:
                    timestamp = tweet.created_at
                timestamps.append(timestamp)
            except (ValueError, AttributeError, TypeError):
                continue
        
        if len(timestamps) < 2:
            return score
        
        timestamps.sort()
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            interval_variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
            
            if interval_variance < (avg_interval * 0.1) ** 2 and len(intervals) > 5:
                score -= 20  # Too regular
            elif interval_variance > (avg_interval * 2) ** 2:
                score += 10   # Natural variance
            
            if avg_interval < 300:  # Less than 5 minutes average
                score -= 25
            elif avg_interval < 3600:  # Less than 1 hour average
                score -= 10
        
        return min(100, max(0, score))

    def _calculate_influence_score(self, user: Any) -> int:
        """Calculate influence score based on follower metrics (0-100)"""
        followers = user.public_metrics.get("followers_count", 0)
        following = user.public_metrics.get("following_count", 0)
        
        if followers >= 1000000:  # 1M+
            follower_score = 100
        elif followers >= 100000:  # 100K+
            follower_score = 80
        elif followers >= 10000:   # 10K+
            follower_score = 60
        elif followers >= 1000:    # 1K+
            follower_score = 40
        else:
            follower_score = 20

        if following > 0:
            ratio = followers / following
            if ratio >= 10:
                ratio_bonus = 20
            elif ratio >= 5:
                ratio_bonus = 15
            elif ratio >= 2:
                ratio_bonus = 10
            elif ratio >= 1:
                ratio_bonus = 5
            else:
                ratio_bonus = 0
        else:
            ratio_bonus = 20  # Following 0 people is unusual but could indicate high status

        return min(100, follower_score + ratio_bonus)

    def _calculate_credibility_score(self, user: Any, tweets: List[Any]) -> int:
        """Calculate credibility score based on account and content indicators (0-100)"""
        score = 0

        if user.verified:
            score += 40

        if user.description:
            score += 15
        if user.location:
            score += 10
        if user.url:
            score += 10

        if tweets:
            tweet_count = user.public_metrics.get("tweet_count", 0)
            account_age_days = (datetime.now(timezone.utc) - user.created_at).days
            
            if account_age_days > 0:
                tweets_per_day = tweet_count / account_age_days
                if 0.5 <= tweets_per_day <= 10:  # Reasonable posting frequency
                    score += 15
                elif tweets_per_day <= 20:  # Moderate posting
                    score += 10
                else:  # Too much or too little posting
                    score += 5

        if user.url and any(domain in user.url for domain in ['.com', '.org', '.edu', '.gov']):
            score += 10

        return min(100, score)
