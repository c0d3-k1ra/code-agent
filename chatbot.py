import json
from config import Config
from session import Session
from api_client import OpenAIClient
from goal_executor import GoalExecutor
from tools import FileTools
from logger import NexusLogger


class Chatbot:
    """Main chatbot orchestrator - coordinates between different modules."""

    def __init__(self):
        self.config = Config()
        self.session = Session()
        self.api_client = OpenAIClient(self.config)
        self.file_tools = FileTools()
        self.logger = NexusLogger()
        self.goal_executor = GoalExecutor(
            self.api_client,
            self.file_tools,
            self.logger,
            self.config
        )
        self.tools = FileTools.get_tool_schemas()

    async def send_message(self, message):
        """Send a message to the chatbot and get a response."""
        # Add user message to session
        self.session.add_user_message(message)

        try:
            # Send request to API with tools
            response = await self.api_client.send_chat_completion(
                messages=self.session.get_conversation_history(),
                session_id=self.session.session_id,
                tools=self.tools
            )

            # Get assistant's message
            assistant_message = response.choices[0].message

            # Add assistant's response to session
            self.session.add_assistant_message(
                assistant_message.content,
                assistant_message.tool_calls
            )

            # Check if there are tool calls
            if assistant_message.tool_calls:
                return await self._handle_tool_calls(assistant_message.tool_calls)

            return assistant_message.content

        except Exception as e:
            return f"Error: {str(e)}"

    async def _handle_tool_calls(self, tool_calls):
        """Handle tool calls and return the final response."""
        # Execute each tool call with minimal logging
        tool_results = []
        for tool_call in tool_calls:
            # Execute the tool
            result = self.file_tools.execute_tool(tool_call)

            # Log tool usage with result using logger
            self._log_tool_execution(tool_call, result)

            # Add tool result
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })

        # Add tool results to session
        self.session.add_tool_results(tool_results)

        # Send follow-up request with tool results
        follow_up_response = await self.api_client.send_follow_up_request(
            messages=self.session.get_conversation_history(),
            session_id=self.session.session_id
        )

        final_message = follow_up_response.choices[0].message
        self.session.add_assistant_message(final_message.content)

        return final_message.content

    def _log_tool_execution(self, tool_call, result):
        """Log tool execution with result."""
        if isinstance(result, dict) and 'success' in result:
            if result['success']:
                # Show successful result concisely
                if 'current_directory' in result:
                    self.logger.tool_execution(tool_call.function.name, result['current_directory'])
                elif 'files' in result:
                    file_count = len(result['files'])
                    self.logger.tool_execution(tool_call.function.name, f"{file_count} items")
                elif 'content' in result:
                    content_preview = result['content'][:50] + "..." if len(result['content']) > 50 else result['content']
                    self.logger.tool_execution(tool_call.function.name, content_preview)
                elif 'message' in result:
                    self.logger.tool_execution(tool_call.function.name, result['message'])
                else:
                    self.logger.tool_execution(tool_call.function.name, "Success")
            else:
                error_msg = f"Error: {result.get('error', 'Unknown error')}"
                self.logger.tool_execution(tool_call.function.name, error_msg)
        else:
            result_preview = str(result)[:50] + "..." if len(str(result)) > 50 else str(result)
            self.logger.tool_execution(tool_call.function.name, result_preview)

    def get_available_tools(self):
        """Get list of available tool names."""
        return [tool['function']['name'] for tool in self.tools]

    def clear_history(self):
        """Clear conversation history."""
        self.session.clear_history()

    def get_session_id(self):
        """Get the current session ID."""
        return self.session.session_id

    def reset_session(self):
        """Reset session with new ID and clear history."""
        return self.session.reset_session()

    def get_session_info(self):
        """Get session information."""
        return self.session.get_session_info()

    def get_model_name(self):
        """Get the current model name."""
        return self.api_client.get_model_name()

    async def run_goal(self, goal):
        """Run an autonomous goal-oriented task using the goal executor."""
        # Backup current session history
        original_history = self.session.backup_history()

        try:
            # Use the dedicated goal executor
            result = await self.goal_executor.execute_goal(goal, self.session.session_id)
            return result
        finally:
            # Restore original conversation history
            self.session.restore_history(original_history)
