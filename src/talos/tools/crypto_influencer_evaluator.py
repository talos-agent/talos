from datetime import datetime, timezone
from typing import Any, List

from ..models.evaluation import EvaluationResult
from .twitter_evaluator import TwitterAccountEvaluator
from .twitter_client import TwitterClient


class CryptoInfluencerEvaluator(TwitterAccountEvaluator):
    """
    Evaluates Twitter accounts specifically for crypto influencer relevance.
    Extends the base TwitterAccountEvaluator with crypto-specific metrics.
    """
    
    def __init__(self, twitter_client: TwitterClient):
        self.twitter_client = twitter_client
        self.crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency', 
            'blockchain', 'defi', 'nft', 'web3', 'dao', 'degen', 'hodl',
            'altcoin', 'trading', 'yield', 'staking', 'mining', 'wallet'
        ]
    
    def evaluate(self, user: Any) -> EvaluationResult:
        follower_following_ratio = user.followers_count / user.friends_count if user.friends_count > 0 else user.followers_count
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days
        is_verified = user.verified
        is_default_profile_image = user.default_profile_image
        
        base_score = 0
        if follower_following_ratio > 1:
            base_score += 25
        if account_age_days > 365:
            base_score += 25
        if is_verified:
            base_score += 25
        if not is_default_profile_image:
            base_score += 25
        
        base_data = {
            "follower_following_ratio": follower_following_ratio,
            "account_age_days": account_age_days,
            "is_verified": is_verified,
            "is_default_profile_image": is_default_profile_image,
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
        
        crypto_score = min(100, int(
            base_score * 0.2 +
            crypto_relevance_score * 0.3 +
            engagement_score * 0.25 +
            authenticity_score * 0.15 +
            influence_score * 0.1
        ))
        
        return EvaluationResult(
            score=crypto_score,
            additional_data={
                **base_data,
                "crypto_relevance_score": crypto_relevance_score,
                "engagement_score": engagement_score,
                "authenticity_score": authenticity_score,
                "influence_score": influence_score,
                "crypto_content_percentage": self._get_crypto_content_percentage(user_timeline),
                "evaluation_type": "crypto_influencer"
            }
        )
    
    def _calculate_crypto_relevance(self, tweets: List[Any]) -> int:
        """Calculate how relevant the user's content is to crypto (0-100)"""
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
        if not tweets or user.followers_count == 0:
            return 0
        
        total_engagement = 0
        for tweet in tweets:
            engagement = (
                tweet.public_metrics.get('like_count', 0) +
                tweet.public_metrics.get('retweet_count', 0) +
                tweet.public_metrics.get('reply_count', 0)
            )
            total_engagement += engagement
        
        avg_engagement = total_engagement / len(tweets)
        engagement_rate = (avg_engagement / user.followers_count) * 100
        
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
        
        if not user.default_profile_image:
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
        followers = user.followers_count
        
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
            
        crypto_tweets = sum(1 for tweet in tweets 
                          if any(keyword in tweet.text.lower() for keyword in self.crypto_keywords))
        return (crypto_tweets / len(tweets)) * 100
