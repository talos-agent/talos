from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from talos.models.services import TwitterSentimentResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterSentimentSkill(Skill):
    """
    A skill for interacting with Twitter.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: PromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    llm: Any = Field(default_factory=ChatOpenAI)

    @property
    def name(self) -> str:
        return "twitter_sentiment_skill"

    def run(self, **kwargs: Any) -> TwitterSentimentResponse:
        query = kwargs.get("query")
        start_time = kwargs.get("start_time")
        if not query:
            raise ValueError("Query must be provided.")
        response = self.twitter_client.search_tweets(query, start_time=start_time)
        if not response or not response.data:
            return TwitterSentimentResponse(answers=[f"Could not find any tweets for query {query}"], score=None)

        users = {user["id"]: user for user in response.includes.get("users", [])}
        
        tweet_data = []
        for tweet in response.data:
            author_id = tweet.author_id
            author = users.get(author_id, {})
            
            followers = author.get("public_metrics", {}).get("followers_count", 1)
            total_engagement = (tweet.public_metrics.get("like_count", 0) + 
                               tweet.public_metrics.get("retweet_count", 0) + 
                               tweet.public_metrics.get("reply_count", 0) + 
                               tweet.public_metrics.get("quote_count", 0))
            engagement_rate = total_engagement / max(followers, 1) * 100
            
            tweet_data.append({
                "text": tweet.text,
                "author": author.get("username", "unknown"),
                "followers": followers,
                "likes": tweet.public_metrics.get("like_count", 0),
                "retweets": tweet.public_metrics.get("retweet_count", 0),
                "replies": tweet.public_metrics.get("reply_count", 0),
                "quotes": tweet.public_metrics.get("quote_count", 0),
                "total_engagement": total_engagement,
                "engagement_rate": round(engagement_rate, 2),
                "created_at": getattr(tweet, 'created_at', ''),
            })

        prompt = self.prompt_manager.get_prompt("talos_sentiment_summary")
        if not prompt:
            raise ValueError("Could not find prompt 'talos_sentiment_summary'")
        
        analysis_prompt = self._create_analysis_prompt(tweet_data, query)
        formatted_prompt = prompt.template.replace("{results}", analysis_prompt)

        response_content = self.llm.invoke(formatted_prompt)
        
        score, detailed_report = self._parse_llm_response(response_content.content, tweet_data, query)
        
        return TwitterSentimentResponse(answers=[detailed_report], score=score)
    
    def _create_analysis_prompt(self, tweet_data: list, query: str) -> str:
        total_tweets = len(tweet_data)
        total_engagement = sum(t["total_engagement"] for t in tweet_data)
        avg_engagement = total_engagement / max(total_tweets, 1)
        
        top_tweets = sorted(tweet_data, key=lambda x: x["total_engagement"], reverse=True)[:5]
        
        prompt_data = f"""
Query: {query}
Total Tweets Analyzed: {total_tweets}
Average Engagement: {avg_engagement:.1f}

Top Engaging Tweets:
"""
        
        for i, tweet in enumerate(top_tweets, 1):
            prompt_data += f"""
{i}. @{tweet['author']} ({tweet['followers']} followers): "{tweet['text'][:100]}..."
   Engagement: {tweet['total_engagement']} (Likes: {tweet['likes']}, Retweets: {tweet['retweets']}, Replies: {tweet['replies']}, Quotes: {tweet['quotes']})
   Engagement Rate: {tweet['engagement_rate']}%
"""
        
        return prompt_data
    
    def _parse_llm_response(self, llm_response: str, tweet_data: list, query: str) -> tuple[float, str]:
        positive_indicators = ["positive", "bullish", "optimistic", "good", "great", "excellent"]
        negative_indicators = ["negative", "bearish", "pessimistic", "bad", "poor", "terrible"]
        
        response_lower = llm_response.lower()
        positive_count = sum(1 for word in positive_indicators if word in response_lower)
        negative_count = sum(1 for word in negative_indicators if word in response_lower)
        
        if positive_count > negative_count:
            base_score = 60 + min(positive_count * 10, 30)
        elif negative_count > positive_count:
            base_score = 40 - min(negative_count * 10, 30)
        else:
            base_score = 50
        
        total_tweets = len(tweet_data)
        avg_engagement = sum(t["total_engagement"] for t in tweet_data) / max(total_tweets, 1)
        high_engagement_tweets = [t for t in tweet_data if t["total_engagement"] > avg_engagement * 1.5]
        
        if len(high_engagement_tweets) > total_tweets * 0.3:
            base_score += 5
        
        final_score = max(0, min(100, base_score))
        
        detailed_report = self._create_detailed_report(llm_response, tweet_data, query, final_score)
        
        return final_score, detailed_report
    
    def _create_detailed_report(self, llm_summary: str, tweet_data: list, query: str, score: float) -> str:
        total_tweets = len(tweet_data)
        total_engagement = sum(t["total_engagement"] for t in tweet_data)
        
        top_tweets = sorted(tweet_data, key=lambda x: x["total_engagement"], reverse=True)[:3]
        
        high_engagement = len([t for t in tweet_data if t["total_engagement"] > 50])
        medium_engagement = len([t for t in tweet_data if 10 <= t["total_engagement"] <= 50])
        low_engagement = len([t for t in tweet_data if t["total_engagement"] < 10])
        
        report = f"""## Sentiment Analysis Report for "{query}"

**Overall Score: {score}/100**

{llm_summary}

- Total Tweets Analyzed: {total_tweets}
- Total Engagement: {total_engagement:,}
- Average Engagement per Tweet: {total_engagement/max(total_tweets,1):.1f}

- High Engagement (>50): {high_engagement} tweets ({high_engagement/max(total_tweets,1)*100:.1f}%)
- Medium Engagement (10-50): {medium_engagement} tweets ({medium_engagement/max(total_tweets,1)*100:.1f}%)
- Low Engagement (<10): {low_engagement} tweets ({low_engagement/max(total_tweets,1)*100:.1f}%)

"""
        
        for i, tweet in enumerate(top_tweets, 1):
            report += f"""
**{i}. @{tweet['author']}** ({tweet['followers']:,} followers)
"{tweet['text'][:150]}{'...' if len(tweet['text']) > 150 else ''}"
📊 {tweet['total_engagement']} total engagement | ❤️ {tweet['likes']} | 🔄 {tweet['retweets']} | 💬 {tweet['replies']} | 📝 {tweet['quotes']}
"""
        
        return report.strip()
