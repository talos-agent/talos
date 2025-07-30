import re
import logging

logger = logging.getLogger(__name__)

def validate_github_username(username: str) -> bool:
    """Validate GitHub username format."""
    if not username or len(username) > 39:
        return False
    return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9_-]*[a-zA-Z0-9])?$', username) is not None

def validate_github_repo_name(repo_name: str) -> bool:
    """Validate GitHub repository name format."""
    if not repo_name or len(repo_name) > 100:
        return False
    return re.match(r'^[a-zA-Z0-9._-]+$', repo_name) is not None

def validate_twitter_username(username: str) -> bool:
    """Validate Twitter username format."""
    if not username or len(username) > 15:
        return False
    return re.match(r'^[a-zA-Z0-9_]+$', username) is not None

def sanitize_user_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input by removing potentially dangerous characters."""
    if not input_str:
        return ""
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)
    return sanitized[:max_length]

def validate_api_token_format(token: str, token_type: str) -> bool:
    """Validate API token format based on type."""
    if not token:
        return False
    
    patterns = {
        'github': r'^(ghp_|gho_|ghu_|ghs_|ghr_)[a-zA-Z0-9]{36}$',
        'openai': r'^sk-[a-zA-Z0-9]{48}$',
        'twitter': r'^[a-zA-Z0-9]{25}$'
    }
    
    pattern = patterns.get(token_type.lower())
    if pattern:
        return re.match(pattern, token) is not None
    return len(token) >= 10

def mask_sensitive_data(data: str, mask_char: str = '*') -> str:
    """Mask sensitive data for logging."""
    if len(data) <= 8:
        return mask_char * len(data)
    return data[:4] + mask_char * (len(data) - 8) + data[-4:]
