from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from config import Config


class OpenAIClient:
    """Handles OpenAI API communication for Nexus AI Assistant."""

    def __init__(self, config: Config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.api_url
        )

    async def send_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None
    ) -> Any:
        """Send a chat completion request to OpenAI API."""
        try:
            request_params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": temperature or self.config.temperature,
                "extra_body": {
                    "litellm_session_id": session_id
                }
            }

            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            response = await self.client.chat.completions.create(**request_params)
            return response

        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    async def send_follow_up_request(
        self,
        messages: List[Dict[str, Any]],
        session_id: str,
        temperature: Optional[float] = None
    ) -> Any:
        """Send a follow-up request after tool execution."""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=temperature or self.config.temperature,
                extra_body={
                    "litellm_session_id": session_id
                }
            )
            return response

        except Exception as e:
            raise Exception(f"Follow-up API request failed: {str(e)}")

    def get_model_name(self) -> str:
        """Get the current model name."""
        return self.config.model_name
