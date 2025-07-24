import os
import asyncio
import json
import uuid
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tools import FileTools

# Load environment variables
load_dotenv()


class Chatbot:
    """Core chatbot logic and API communication."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('API_URL')
        )
        self.model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
        self.conversation_history = []
        self.file_tools = FileTools()
        self.tools = FileTools.get_tool_schemas()
        self.session_id = str(uuid.uuid4())  # Generate unique session ID for LiteLLM tracking

    async def send_message(self, message):
        """Send a message to the chatbot and get a response."""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        try:
            # Send request to API with tools
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
                tools=self.tools,
                tool_choice="auto",
                extra_body={
                    "litellm_session_id": self.session_id  # LiteLLM session tracking
                }
            )

            # Get assistant's message
            assistant_message = response.choices[0].message

            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": assistant_message.tool_calls
            })

            # Check if there are tool calls
            if assistant_message.tool_calls:
                return await self._handle_tool_calls(assistant_message.tool_calls)

            return assistant_message.content

        except Exception as e:
            return f"Error: {str(e)}"

    async def _handle_tool_calls(self, tool_calls):
        """Handle tool calls and return the final response."""
        print("\n" + "="*60)
        print("🔧 LLM WANTS TO USE TOOLS!")
        print("="*60)
        print(f"Number of tool calls: {len(tool_calls)}")

        # Execute each tool call automatically
        tool_results = []
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"\nTool Call #{i}:")
            print(f"  📋 Function: {tool_call.function.name}")
            print(f"  📝 Arguments: {tool_call.function.arguments}")
            print(f"  🆔 Call ID: {tool_call.id}")

            # Execute the tool automatically
            print(f"  🔄 Executing tool...")
            result = self.file_tools.execute_tool(tool_call)
            print(f"  ✅ Result: {result}")

            # Add tool result to conversation history
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })

        print("="*60)
        print("🔄 Processing tool results...")

        # Add tool results to conversation history
        self.conversation_history.extend(tool_results)

        # Send follow-up request with tool results automatically
        follow_up_response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self.conversation_history,
            temperature=0.7,
            extra_body={
                "litellm_session_id": self.session_id  # Same session ID for continuity
            }
        )

        final_message = follow_up_response.choices[0].message
        self.conversation_history.append({
            "role": "assistant",
            "content": final_message.content
        })

        print("✅ Tool execution completed!")
        return final_message.content

    def get_available_tools(self):
        """Get list of available tool names."""
        return [tool['function']['name'] for tool in self.tools]

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_session_id(self):
        """Get the current session ID."""
        return self.session_id

    def reset_session(self):
        """Reset session with new ID and clear history."""
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        return self.session_id

    def get_session_info(self):
        """Get session information."""
        return {
            "session_id": self.session_id,
            "message_count": len([msg for msg in self.conversation_history if msg["role"] in ["user", "assistant"]]),
            "tool_calls_count": len([msg for msg in self.conversation_history if msg["role"] == "tool"])
        }
