import os
import asyncio
import json
from pathlib import Path
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Chatbot:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('API_URL')
        )
        self.model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')  # Default if not set
        self.conversation_history = []
        self.current_dir = Path.cwd()

        # Define tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file from the file system",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file in the file system",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to write to"
                            },
                            "content": {
                                "type": "string",
                                "description": "The content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            }
        ]

    def _is_safe_path(self, file_path):
        """Check if the file path is within the current directory for security."""
        try:
            # Convert to absolute path and resolve any .. or . components
            abs_path = Path(file_path).resolve()
            # Check if the path is within current directory
            return str(abs_path).startswith(str(self.current_dir.resolve()))
        except Exception:
            return False

    def _read_file(self, file_path):
        """Read file contents with safety checks."""
        if not self._is_safe_path(file_path):
            return {"error": "Access denied: File path is outside current directory"}

        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}

            if not path.is_file():
                return {"error": f"Path is not a file: {file_path}"}

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {"success": True, "content": content, "file_path": str(path)}

        except PermissionError:
            return {"error": f"Permission denied: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    def _write_file(self, file_path, content):
        """Write file contents with safety checks."""
        try:
            # Debug: Print current directory and file path
            print(f"  🔍 Current directory: {self.current_dir}")
            print(f"  🔍 Requested file path: {file_path}")
            print(f"  🔍 Content type: {type(content)}")
            print(f"  🔍 Content value: {repr(content)}")

            # Ensure content is a string
            if content is None:
                content = ""
            elif not isinstance(content, str):
                content = str(content)

            if not self._is_safe_path(file_path):
                return {"error": "Access denied: File path is outside current directory"}

            path = Path(file_path)

            # Make path relative to current directory if it's not absolute
            if not path.is_absolute():
                path = self.current_dir / path

            print(f"  🔍 Resolved path: {path}")

            # Create parent directories if they don't exist
            if path.parent != path:  # Avoid creating parent for root
                path.parent.mkdir(parents=True, exist_ok=True)
                print(f"  📁 Created directories: {path.parent}")

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {"success": True, "message": f"File written successfully: {file_path}", "file_path": str(path)}

        except PermissionError as e:
            return {"error": f"Permission denied: {file_path} - {str(e)}"}
        except Exception as e:
            return {"error": f"Error writing file: {str(e)} (path: {file_path})"}

    def _execute_tool(self, tool_call):
        """Execute a tool call and return the result."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "read_file":
            return self._read_file(arguments.get("file_path"))
        elif function_name == "write_file":
            return self._write_file(arguments.get("file_path"), arguments.get("content"))
        else:
            return {"error": f"Unknown function: {function_name}"}

    async def send_message(self, message):
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        try:
            # Send request to API with tools
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
                tools=self.tools,
                tool_choice="auto"
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
                print("\n" + "="*60)
                print("🔧 LLM WANTS TO USE TOOLS!")
                print("="*60)
                print(f"Number of tool calls: {len(assistant_message.tool_calls)}")

                # Execute each tool call automatically
                tool_results = []
                for i, tool_call in enumerate(assistant_message.tool_calls, 1):
                    print(f"\nTool Call #{i}:")
                    print(f"  📋 Function: {tool_call.function.name}")
                    print(f"  📝 Arguments: {tool_call.function.arguments}")
                    print(f"  🆔 Call ID: {tool_call.id}")

                    # Execute the tool automatically
                    print(f"  🔄 Executing tool...")
                    result = self._execute_tool(tool_call)
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
                )

                final_message = follow_up_response.choices[0].message
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message.content
                })

                print("✅ Tool execution completed!")
                return final_message.content

            return assistant_message.content

        except Exception as e:
            return f"Error: {str(e)}"

async def main():
    print("Welcome to the AI Chatbot with Tools!")
    print("Type 'quit' to exit")
    print("-" * 50)

    chatbot = Chatbot()
    print(f"Using model: {chatbot.model_name}")
    print(f"Available tools: {[tool['function']['name'] for tool in chatbot.tools]}")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == 'quit':
            print("\nGoodbye!")
            break

        if user_input:
            response = await chatbot.send_message(user_input)
            print("\nBot:", response)

if __name__ == "__main__":
    asyncio.run(main())
