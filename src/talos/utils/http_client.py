import requests
import logging
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter  # type: ignore
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class SecureHTTPClient:
    """Secure HTTP client with proper timeouts, retries, and error handling."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Secure GET request with proper error handling."""
        try:
            response = self.session.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                verify=True,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for URL: {url}")
            raise
        except requests.exceptions.SSLError:
            logger.error(f"SSL verification failed for URL: {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for URL: {url}, Error: {e}")
            raise
    
    def post(self, url: str, data: Any = None, json: Any = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Secure POST request with proper error handling."""
        try:
            response = self.session.post(
                url, 
                data=data,
                json=json,
                headers=headers, 
                timeout=self.timeout,
                verify=True,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP POST request failed for URL: {url}, Error: {e}")
            raise
