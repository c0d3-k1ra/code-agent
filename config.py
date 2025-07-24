import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Centralized configuration management for Nexus AI Assistant."""

    def __init__(self):
        self._validate_required_config()

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return os.getenv('OPENAI_API_KEY', '')

    @property
    def api_url(self) -> str:
        """Get API URL."""
        return os.getenv('API_URL', 'https://api.openai.com/v1')

    @property
    def model_name(self) -> str:
        """Get model name."""
        return os.getenv('MODEL_NAME', 'gpt-3.5-turbo')

    @property
    def temperature(self) -> float:
        """Get temperature for API calls."""
        return float(os.getenv('TEMPERATURE', '0.7'))

    @property
    def max_goal_actions(self) -> int:
        """Get maximum actions for goal execution."""
        return int(os.getenv('MAX_GOAL_ACTIONS', '20'))

    def _validate_required_config(self):
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required but not set in environment variables")

    def get_all_config(self) -> dict:
        """Get all configuration as a dictionary."""
        return {
            'api_key': self.openai_api_key[:10] + '...' if self.openai_api_key else 'Not set',
            'api_url': self.api_url,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_goal_actions': self.max_goal_actions
        }
