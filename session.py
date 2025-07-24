import uuid
from typing import List, Dict, Any, Optional


class Session:
    """Manages conversation history and session tracking for Nexus AI Assistant."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.conversation_history: List[Dict[str, Any]] = []

    def add_user_message(self, content: str) -> None:
        """Add a user message to conversation history."""
        self.conversation_history.append({
            "role": "user",
            "content": content
        })

    def add_assistant_message(self, content: Optional[str], tool_calls: Optional[Any] = None) -> None:
        """Add an assistant message to conversation history."""
        message = {
            "role": "assistant",
            "content": content
        }
        if tool_calls:
            message["tool_calls"] = tool_calls

        self.conversation_history.append(message)

    def add_tool_results(self, tool_results: List[Dict[str, Any]]) -> None:
        """Add tool execution results to conversation history."""
        self.conversation_history.extend(tool_results)

    def add_system_message(self, content: str) -> None:
        """Add a system message to conversation history."""
        self.conversation_history.append({
            "role": "system",
            "content": content
        })

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []

    def reset_session(self) -> str:
        """Reset session with new ID and clear history."""
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        return self.session_id

    def get_session_info(self) -> Dict[str, Any]:
        """Get session information."""
        return {
            "session_id": self.session_id,
            "message_count": len([msg for msg in self.conversation_history if msg["role"] in ["user", "assistant"]]),
            "tool_calls_count": len([msg for msg in self.conversation_history if msg["role"] == "tool"])
        }

    def backup_history(self) -> List[Dict[str, Any]]:
        """Create a backup of current conversation history."""
        return self.conversation_history.copy()

    def restore_history(self, backup: List[Dict[str, Any]]) -> None:
        """Restore conversation history from backup."""
        self.conversation_history = backup.copy()

    def create_temporary_history(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create a temporary conversation history for specific operations."""
        return messages.copy()
