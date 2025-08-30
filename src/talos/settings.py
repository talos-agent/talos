from typing import Optional
import logging
from pydantic import model_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class GitHubSettings(BaseSettings):
    GITHUB_API_TOKEN: Optional[str] = None

    @model_validator(mode="after")
    def validate_github_token(self):
        if not self.GITHUB_API_TOKEN:
            raise ValueError("GITHUB_API_TOKEN environment variable is required but not set")
        
        from .utils.validation import validate_api_token_format, mask_sensitive_data
        if not validate_api_token_format(self.GITHUB_API_TOKEN, 'github'):
            logger.warning("GitHub API token format appears invalid")
        
        masked_token = mask_sensitive_data(self.GITHUB_API_TOKEN)
        logger.info(f"GitHub settings initialized with token: {masked_token}")
        return self


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def validate_openai_key(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required but not set")
        
        from .utils.validation import validate_api_token_format, mask_sensitive_data
        if not validate_api_token_format(self.OPENAI_API_KEY, 'openai'):
            logger.warning("OpenAI API key format appears invalid")
        
        masked_key = mask_sensitive_data(self.OPENAI_API_KEY)
        logger.info(f"OpenAI settings initialized with key: {masked_key}")
        return self


class PerspectiveSettings(BaseSettings):
    PERSPECTIVE_API_KEY: Optional[str] = None


class GitBookSettings(BaseSettings):
    GITBOOK_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def validate_gitbook_key(self):
        if not self.GITBOOK_API_KEY:
            raise ValueError("GITBOOK_API_KEY environment variable is required but not set")
        
        from .utils.validation import mask_sensitive_data
        masked_key = mask_sensitive_data(self.GITBOOK_API_KEY)
        logger.info(f"GitBook settings initialized with key: {masked_key}")
        return self


class TwitterOAuthSettings(BaseSettings):
    TWITTER_CONSUMER_KEY: Optional[str] = None
    TWITTER_CONSUMER_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None

    @model_validator(mode="after")
    def validate_twitter_oauth(self):
        required_fields = [self.TWITTER_CONSUMER_KEY, self.TWITTER_CONSUMER_SECRET, 
                          self.TWITTER_ACCESS_TOKEN, self.TWITTER_ACCESS_TOKEN_SECRET]
        if not all(required_fields):
            raise ValueError("All Twitter OAuth environment variables are required: TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
        
        from .utils.validation import mask_sensitive_data
        logger.info(f"Twitter OAuth settings initialized with consumer key: {mask_sensitive_data(self.TWITTER_CONSUMER_KEY)}")
        return self
