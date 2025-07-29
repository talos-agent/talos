from typing import Optional
import typer

from talos.skills.twitter_persona import TwitterPersonaSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.skills.twitter_voice import TwitterVoiceSkill

twitter_app = typer.Typer()


@twitter_app.command()
def get_user_prompt(username: str):
    """
    Gets the general voice of a user as a structured persona analysis.
    """
    skill = TwitterPersonaSkill()
    response = skill.run(username=username)
    
    print(f"=== Twitter Persona Analysis for @{username} ===\n")
    print(f"Report:\n{response.report}\n")
    print(f"Topics: {', '.join(response.topics)}\n")
    print(f"Style: {', '.join(response.style)}")


@twitter_app.command()
def get_query_sentiment(query: str, start_time: Optional[str] = None):
    """
    Gets the general sentiment/report on a specific query.

    Args:
        query: Search query for tweets
        start_time: Optional datetime filter (ISO 8601 format, e.g., "2023-01-01T00:00:00Z")
    """
    skill = TwitterSentimentSkill()
    response = skill.run(query=query, start_time=start_time)
    if response.score is not None:
        print(f"Sentiment Score: {response.score}/100")
        print("=" * 50)
    print(response.answers[0])


@twitter_app.command()
def integrate_voice(username: str = "talos_is"):
    """
    Integrate Twitter voice analysis into agent communication.
    
    Args:
        username: Twitter username to analyze (defaults to talos_is)
    """
    skill = TwitterVoiceSkill()
    result = skill.run(username=username)
    
    print(f"=== Voice Integration for @{username} ===\n")
    print(f"Voice Source: {result['voice_source']}")
    print(f"Voice Prompt Generated:\n{result['voice_prompt']}")
    print("\nPersona Analysis:")
    print(f"Topics: {', '.join(result['persona_analysis'].topics)}")
    print(f"Style: {', '.join(result['persona_analysis'].style)}")
