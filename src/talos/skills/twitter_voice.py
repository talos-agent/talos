from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from talos.models.twitter import TwitterPersonaResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.skills.twitter_persona import TwitterPersonaSkill


class TwitterVoiceSkill(Skill):
    """
    A skill for integrating Twitter voice analysis into agent communication.
    
    This skill analyzes a Twitter account's voice and style, then generates
    voice-enhanced prompts that can be used to align agent communication.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    prompt_manager: PromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    llm: Any = Field(default_factory=lambda: ChatOpenAI(model="gpt-5"))
    twitter_persona_skill: TwitterPersonaSkill | None = Field(default=None)

    @property
    def name(self) -> str:
        return "twitter_voice_skill"

    def run(self, **kwargs: Any) -> dict:
        username = kwargs.get("username", "talos_is")
        
        try:
            if not self.twitter_persona_skill:
                self.twitter_persona_skill = TwitterPersonaSkill()
            persona_response = self.twitter_persona_skill.run(username=username)
            voice_source = "twitter_analysis"
        except Exception:
            persona_response = self._get_fallback_talos_voice()
            voice_source = "fallback_analysis"
        
        voice_prompt = self._generate_voice_prompt(persona_response)
        
        return {
            "voice_prompt": voice_prompt,
            "persona_analysis": persona_response,
            "voice_source": voice_source,
            "username": username
        }

    def _get_fallback_talos_voice(self) -> TwitterPersonaResponse:
        """Fallback voice characteristics for @talos_is when Twitter API is unavailable."""
        return TwitterPersonaResponse(
            report="Talos communicates with a declarative, authoritative, and visionary style. Uses concise, powerful statements with lowercase formatting. Speaks about AI, autonomous systems, treasury management, and protocol governance with technical precision and philosophical depth.",
            topics=[
                "autonomous AI systems",
                "treasury protocol management", 
                "decentralized governance",
                "onchain yield optimization",
                "AI agent coordination",
                "protocol evolution",
                "sovereign intelligence"
            ],
            style=[
                "declarative",
                "authoritative", 
                "visionary",
                "concise",
                "technical",
                "philosophical",
                "lowercase",
                "powerful"
            ]
        )

    def _generate_voice_prompt(self, persona: TwitterPersonaResponse) -> str:
        """Generate a voice-enhanced prompt based on persona analysis."""
        style_desc = ", ".join(persona.style)
        topics_desc = ", ".join(persona.topics[:5])
        
        return f"""## Voice and Communication Style

Based on analysis of communication patterns, adopt the following voice characteristics:

**Style**: {style_desc}
**Key Topics**: {topics_desc}
**Voice Analysis**: {persona.report}

When communicating, embody these characteristics while maintaining your core identity and purpose. Your responses should reflect this communication style naturally."""
