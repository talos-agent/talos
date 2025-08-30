from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from talos.services.abstract.service import Service


class Devin(Service, ABC):
    """
    An abstract base class for a Devin service.
    Enables Talos to interact with Devin AI for session management.
    """

    @abstractmethod
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all sessions from Devin.
        
        Returns:
            List of session dictionaries containing session information.
        """
        pass

    @abstractmethod
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves detailed information about a specific session.
        
        Args:
            session_id: The ID of the session to retrieve information for.
            
        Returns:
            Dictionary containing detailed session information.
        """
        pass

    @abstractmethod
    def send_message_to_session(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Sends a message to an existing Devin session.
        
        Args:
            session_id: The ID of the session to send message to.
            message: The message to send.
            
        Returns:
            Dictionary containing the message response result.
        """
        pass

    @abstractmethod
    def create_session(self, description: str, **kwargs) -> Dict[str, Any]:
        """
        Creates a new Devin session.
        
        Args:
            description: The session description/task.
            **kwargs: Additional session parameters.
            
        Returns:
            Dictionary containing the created session information.
        """
        pass
