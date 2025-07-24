import json
from typing import List, Dict, Any, Optional
from api_client import OpenAIClient
from session import Session
from tools import FileTools
from logger import NexusLogger
from config import Config


class GoalExecutor:
    """Handles autonomous goal execution for Nexus AI Assistant."""

    def __init__(self, api_client: OpenAIClient, file_tools: FileTools, logger: NexusLogger, config: Config):
        self.api_client = api_client
        self.file_tools = file_tools
        self.logger = logger
        self.config = config

    async def execute_goal(self, goal: str, session_id: str) -> str:
        """Execute an autonomous goal-oriented task."""
        self.logger.goal_start(goal)

        try:
            # 1. Create comprehensive plan
            plan = await self._create_master_plan(goal, session_id)
            self.logger.goal_plan(plan)
            self.logger.goal_executing()

            # 2. Execute until done
            max_actions = self.config.max_goal_actions
            action_count = 0
            completed_actions = []

            while action_count < max_actions:
                # Decide next action
                next_action = await self._decide_next_action(goal, plan, completed_actions, session_id)

                # Check if goal is complete
                if "GOAL_COMPLETE" in next_action.upper() or "FINISHED" in next_action.upper():
                    self.logger.goal_complete(next_action)
                    return next_action

                # Log and execute action
                self.logger.goal_action(next_action)
                result = await self._execute_action(next_action, session_id)

                # Track completed action
                completed_actions.append({
                    "action": next_action,
                    "result": result
                })

                action_count += 1

            error_msg = f"Goal execution reached maximum actions ({max_actions})"
            self.logger.error(error_msg)
            return error_msg

        except Exception as e:
            error_msg = f"Goal execution failed: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def _create_master_plan(self, goal: str, session_id: str) -> str:
        """Create a comprehensive plan for achieving the goal."""
        plan_prompt = f"""Create a comprehensive plan to achieve this goal: {goal}

Available tools: {', '.join(self._get_available_tools())}

Create a detailed, step-by-step plan that will accomplish the goal completely.
List all the specific actions needed in order.
Be thorough and consider all necessary steps."""

        temp_messages = [
            {"role": "system", "content": "You are an autonomous AI agent. Create comprehensive plans to achieve goals."},
            {"role": "user", "content": plan_prompt}
        ]

        response = await self.api_client.send_chat_completion(
            messages=temp_messages,
            session_id=session_id,
            temperature=0.3
        )

        return response.choices[0].message.content

    async def _decide_next_action(self, goal: str, plan: str, completed_actions: List[Dict[str, Any]], session_id: str) -> str:
        """Decide what action to take next based on the goal, plan, and completed actions."""
        completed_summary = ""
        if completed_actions:
            completed_summary = "\n\nCOMPLETED ACTIONS AND RESULTS:\n"
            for i, action_info in enumerate(completed_actions, 1):
                action = action_info['action']
                result_preview = str(action_info['result'])[:100] + "..." if len(str(action_info['result'])) > 100 else str(action_info['result'])
                completed_summary += f"{i}. ✅ {action}\n   Result: {result_preview}\n"

        action_prompt = f"""GOAL: {goal}

ORIGINAL PLAN:
{plan}
{completed_summary}

CRITICAL INSTRUCTIONS:
1. Look at what has ALREADY been completed above
2. Determine if the goal is fully achieved based on completed actions
3. If goal is achieved, respond with "GOAL_COMPLETE: [brief summary of what was accomplished]"
4. If goal is NOT achieved, identify the NEXT logical step from the original plan that hasn't been done yet
5. DO NOT repeat any action that has already been completed successfully

What should happen next?"""

        temp_messages = [
            {"role": "system", "content": "You are a goal execution agent. Analyze completed work and decide if goal is complete or what specific action comes next. Be decisive and avoid repeating completed actions."},
            {"role": "user", "content": action_prompt}
        ]

        response = await self.api_client.send_chat_completion(
            messages=temp_messages,
            session_id=session_id,
            temperature=0.1
        )

        return response.choices[0].message.content

    async def _execute_action(self, action: str, session_id: str) -> str:
        """Execute a specific action using available tools."""
        # Create a temporary session for action execution
        temp_session = Session()
        temp_session.add_system_message("Execute the requested action using available tools.")
        temp_session.add_user_message(f"Execute this action: {action}\n\nUse the available tools to complete this action.\nBe direct and efficient.")

        # Execute the action with tools
        response = await self.api_client.send_chat_completion(
            messages=temp_session.get_conversation_history(),
            session_id=session_id,
            tools=FileTools.get_tool_schemas()
        )

        assistant_message = response.choices[0].message

        # Handle tool calls if present
        if assistant_message.tool_calls:
            return await self._handle_tool_calls_for_action(assistant_message.tool_calls, temp_session, session_id)

        return assistant_message.content or "Action completed"

    async def _handle_tool_calls_for_action(self, tool_calls: Any, temp_session: Session, session_id: str) -> str:
        """Handle tool calls during action execution."""
        # Add assistant message with tool calls
        temp_session.add_assistant_message(None, tool_calls)

        # Execute each tool call
        tool_results = []
        for tool_call in tool_calls:
            result = self.file_tools.execute_tool(tool_call)

            # Log tool usage
            self._log_tool_execution(tool_call, result)

            # Add tool result
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })

        # Add tool results to session
        temp_session.add_tool_results(tool_results)

        # Send follow-up request
        follow_up_response = await self.api_client.send_follow_up_request(
            messages=temp_session.get_conversation_history(),
            session_id=session_id
        )

        return follow_up_response.choices[0].message.content or "Action completed with tools"

    def _log_tool_execution(self, tool_call: Any, result: Any) -> None:
        """Log tool execution with result."""
        if isinstance(result, dict) and 'success' in result:
            if result['success']:
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

    def _get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [tool['function']['name'] for tool in FileTools.get_tool_schemas()]
