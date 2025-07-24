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
        # Execute each tool call with minimal logging
        tool_results = []
        for tool_call in tool_calls:
            # Execute the tool
            result = self.file_tools.execute_tool(tool_call)

            # Log tool usage with result
            if isinstance(result, dict) and 'success' in result:
                if result['success']:
                    # Show successful result concisely
                    if 'current_directory' in result:
                        print(f"🔧 {tool_call.function.name} → {result['current_directory']}")
                    elif 'files' in result:
                        file_count = len(result['files'])
                        print(f"🔧 {tool_call.function.name} → {file_count} items")
                    elif 'content' in result:
                        content_preview = result['content'][:50] + "..." if len(result['content']) > 50 else result['content']
                        print(f"🔧 {tool_call.function.name} → {content_preview}")
                    elif 'message' in result:
                        print(f"🔧 {tool_call.function.name} → {result['message']}")
                    else:
                        print(f"🔧 {tool_call.function.name} → Success")
                else:
                    print(f"🔧 {tool_call.function.name} → Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"🔧 {tool_call.function.name} → {str(result)[:50]}...")

            # Add tool result to conversation history
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": json.dumps(result)
            })

        # Add tool results to conversation history
        self.conversation_history.extend(tool_results)

        # Send follow-up request with tool results
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

    async def run_goal(self, goal):
        """Run an autonomous goal-oriented task with simplified execution."""
        # Clear any existing conversation history for clean goal execution
        original_history = self.conversation_history.copy()
        self.conversation_history = []

        print(f"\n🎯 Goal: {goal}")

        try:
            # 1. PLAN ONCE - Create comprehensive plan
            plan = await self._create_master_plan(goal)
            print(f"📋 Plan:\n{plan}")
            print("⚡ Executing...")

            # 2. EXECUTE UNTIL DONE
            max_actions = 20  # Prevent infinite loops
            action_count = 0
            completed_actions = []  # Track what's been done

            while action_count < max_actions:
                # Decide next action with context of what's been completed
                next_action = await self._decide_next_action(goal, plan, completed_actions)

                # Check if goal is complete
                if "GOAL_COMPLETE" in next_action.upper() or "FINISHED" in next_action.upper():
                    print("✅ Goal completed!")
                    return next_action

                # Log and execute action
                print(f"🔄 {next_action}")
                result = await self._execute_action(next_action)

                # Track completed action
                completed_actions.append({
                    "action": next_action,
                    "result": result
                })

                action_count += 1

            return f"Goal execution reached maximum actions ({max_actions})"

        except Exception as e:
            print(f"❌ Goal execution failed: {str(e)}")
            return f"Goal execution failed: {str(e)}"

        finally:
            # Restore original conversation history
            self.conversation_history = original_history

    async def _create_master_plan(self, goal):
        """Create a comprehensive plan for achieving the goal."""
        plan_prompt = f"""Create a comprehensive plan to achieve this goal: {goal}

Available tools: {', '.join(self.get_available_tools())}

Create a detailed, step-by-step plan that will accomplish the goal completely.
List all the specific actions needed in order.
Be thorough and consider all necessary steps."""

        temp_history = [
            {"role": "system", "content": "You are an autonomous AI agent. Create comprehensive plans to achieve goals."},
            {"role": "user", "content": plan_prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=temp_history,
            temperature=0.3,
            extra_body={
                "litellm_session_id": self.session_id
            }
        )

        return response.choices[0].message.content

    async def _decide_next_action(self, goal, plan, completed_actions):
        """Decide what action to take next based on the goal, plan, and completed actions."""
        completed_summary = ""
        if completed_actions:
            completed_summary = "\n\nCompleted Actions:\n"
            for i, action_info in enumerate(completed_actions, 1):
                completed_summary += f"{i}. {action_info['action']}\n"

        action_prompt = f"""Goal: {goal}
Plan: {plan}{completed_summary}

Based on the goal, plan, and what has already been completed, what is the next specific action you should take?

IMPORTANT: Do not repeat actions that have already been completed. Move to the next logical step in the plan.

If the goal is complete, respond with "GOAL_COMPLETE: [summary]"
Otherwise, respond with a brief description of the next action to take."""

        temp_history = [
            {"role": "system", "content": "You are executing a plan. Decide the next specific action based on what's already been done."},
            {"role": "user", "content": action_prompt}
        ]

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=temp_history,
            temperature=0.2,
            extra_body={
                "litellm_session_id": self.session_id
            }
        )

        return response.choices[0].message.content

    async def _execute_action(self, action):
        """Execute a specific action using available tools."""
        execute_prompt = f"""Execute this action: {action}

Use the available tools to complete this action.
Be direct and efficient."""

        # Add system context for execution
        self.conversation_history.append({"role": "system", "content": "Execute the requested action using available tools."})

        # Execute the action
        result = await self.send_message(execute_prompt)

        return result
