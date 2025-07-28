from __future__ import annotations

import requests
from typing import Any, Dict, List, Optional
from pydantic import PrivateAttr

from talos.services.abstract.devin import Devin


class DevinService(Devin):
    """
    A service for interacting with Devin AI for session management.
    """

    api_base_url: str = "https://api.devin.ai"
    api_key: Optional[str] = None
    _session: requests.Session = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })

    @property
    def name(self) -> str:
        return "devin"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Makes an HTTP request to the Devin API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self._session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Devin API request failed: {str(e)}")

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all sessions from Devin.
        
        Returns:
            List of session dictionaries containing session information.
        """
        result = self._make_request("GET", "/sessions")
        return result.get("sessions", [])

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific session.
        
        Args:
            session_id: The ID of the session to retrieve information for.
            
        Returns:
            Dictionary containing detailed session information.
        """
        return self._make_request("GET", f"/sessions/{session_id}")

    def send_message_to_session(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Sends a message to an existing Devin session.
        
        Args:
            session_id: The ID of the session to send message to.
            message: The message to send.
            
        Returns:
            Dictionary containing the message response result.
        """
        payload = {"message": message}
        return self._make_request("POST", f"/sessions/{session_id}/messages", json=payload)

    def create_session(self, description: str, **kwargs) -> Dict[str, Any]:
        """
        Creates a new Devin session.
        
        Args:
            description: The session description/task.
            **kwargs: Additional session parameters (idempotent, etc.)
            
        Returns:
            Dictionary containing the created session information.
        """
        payload = {"task": description, **kwargs}
        return self._make_request("POST", "/sessions", json=payload)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Legacy method - redirects to get_all_sessions()"""
        return self.get_all_sessions()

    def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """Legacy method - redirects to get_session_info()"""
        return self.get_session_info(task_id)

    def respond_to_task(self, task_id: str, response: str) -> Dict[str, Any]:
        """Legacy method - redirects to send_message_to_session()"""
        return self.send_message_to_session(task_id, response)

    def create_task(self, description: str, **kwargs) -> Dict[str, Any]:
        """Legacy method - redirects to create_session()"""
        return self.create_session(description, **kwargs)
