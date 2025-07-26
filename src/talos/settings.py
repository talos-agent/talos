from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings


class GitHubSettings(BaseSettings):
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_TOKEN: Optional[str] = None

    @model_validator(mode="after")
    def validate_github_token(self):
        if not self.GITHUB_TOKEN and not self.GITHUB_API_TOKEN:
            raise ValueError("Either GITHUB_TOKEN or GITHUB_API_TOKEN environment variable is required but not set")
        return self


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def validate_openai_key(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required but not set")
        return self


class PerspectiveSettings(BaseSettings):
    PERSPECTIVE_API_KEY: Optional[str] = None


class GitBookSettings(BaseSettings):
    GITBOOK_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def validate_gitbook_key(self):
        if not self.GITBOOK_API_KEY:
            raise ValueError("GITBOOK_API_KEY environment variable is required but not set")
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
        return self
