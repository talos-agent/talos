from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime, timezone
from ..models.evaluation import EvaluationResult

class TwitterAccountEvaluator(ABC):
    @abstractmethod
    def evaluate(self, user: Any) -> EvaluationResult:
        pass

class DefaultTwitterAccountEvaluator(TwitterAccountEvaluator):
    def evaluate(self, user: Any) -> EvaluationResult:
        # Follower/Following Ratio
        if user.friends_count > 0:
            follower_following_ratio = user.followers_count / user.friends_count
        else:
            follower_following_ratio = user.followers_count

        # Account Age
        account_age_days = (datetime.now(timezone.utc) - user.created_at).days

        # Verified Status
        is_verified = user.verified

        # Default Profile Image
        is_default_profile_image = user.default_profile_image

        # Calculate score
        score = 0
        if follower_following_ratio > 1:
            score += 25
        if account_age_days > 365:
            score += 25
        if is_verified:
            score += 25
        if not is_default_profile_image:
            score += 25

        return EvaluationResult(
            score=score,
            additional_data={
                "follower_following_ratio": follower_following_ratio,
                "account_age_days": account_age_days,
                "is_verified": is_verified,
                "is_default_profile_image": is_default_profile_image,
            }
        )
