from unittest.mock import patch, MagicMock

from talos.models.twitter import TwitterPersonaResponse
from talos.skills.twitter_voice import TwitterVoiceSkill


class TestTwitterVoiceSkill:
    @patch('talos.skills.twitter_voice.TwitterPersonaSkill')
    @patch('talos.skills.twitter_voice.ChatOpenAI')
    def test_fallback_voice_characteristics(self, mock_chat_openai, mock_persona_skill_class):
        """Test that fallback voice characteristics are properly defined."""
        mock_llm = mock_chat_openai.return_value
        mock_persona_skill_class.return_value = MagicMock()
        
        skill = TwitterVoiceSkill(llm=mock_llm)
        fallback = skill._get_fallback_talos_voice()
        
        assert isinstance(fallback, TwitterPersonaResponse)
        assert len(fallback.topics) > 0
        assert len(fallback.style) > 0
        assert "autonomous" in fallback.report.lower()

    @patch('talos.skills.twitter_voice.TwitterPersonaSkill')
    @patch('talos.skills.twitter_voice.ChatOpenAI')
    def test_run_with_twitter_success(self, mock_chat_openai, mock_persona_skill_class):
        """Test successful Twitter analysis."""
        mock_llm = mock_chat_openai.return_value
        mock_response = TwitterPersonaResponse(
            report="Test analysis",
            topics=["AI", "crypto"],
            style=["technical", "concise"]
        )
        mock_persona_skill_instance = MagicMock()
        mock_persona_skill_instance.run.return_value = mock_response
        mock_persona_skill_class.return_value = mock_persona_skill_instance
        
        skill = TwitterVoiceSkill(llm=mock_llm)
        result = skill.run(username="test_user")
        
        assert result["voice_source"] == "twitter_analysis"
        assert result["username"] == "test_user"
        assert "voice_prompt" in result

    @patch('talos.skills.twitter_voice.TwitterPersonaSkill')
    @patch('talos.skills.twitter_voice.ChatOpenAI')
    def test_run_with_twitter_failure(self, mock_chat_openai, mock_persona_skill_class):
        """Test fallback when Twitter analysis fails."""
        mock_llm = mock_chat_openai.return_value
        mock_persona_skill_instance = MagicMock()
        mock_persona_skill_instance.run.side_effect = Exception("API Error")
        mock_persona_skill_class.return_value = mock_persona_skill_instance
        
        skill = TwitterVoiceSkill(llm=mock_llm)
        result = skill.run(username="talos_is")
        
        assert result["voice_source"] == "fallback_analysis"
        assert result["username"] == "talos_is"
        assert "voice_prompt" in result

    @patch('talos.skills.twitter_voice.TwitterPersonaSkill')
    @patch('talos.skills.twitter_voice.ChatOpenAI')
    def test_generate_voice_prompt(self, mock_chat_openai, mock_persona_skill_class):
        """Test voice prompt generation."""
        mock_llm = mock_chat_openai.return_value
        mock_persona_skill_class.return_value = MagicMock()
        
        skill = TwitterVoiceSkill(llm=mock_llm)
        persona = TwitterPersonaResponse(
            report="Test communication style",
            topics=["topic1", "topic2"],
            style=["style1", "style2"]
        )
        
        prompt = skill._generate_voice_prompt(persona)
        assert "style1, style2" in prompt
        assert "topic1, topic2" in prompt
        assert "Test communication style" in prompt
