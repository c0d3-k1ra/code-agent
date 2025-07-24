import os
import asyncio
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

    async def send_message(self, message):
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        try:
            # Send request to API with tools
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=150,
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

                for i, tool_call in enumerate(assistant_message.tool_calls, 1):
                    print(f"\nTool Call #{i}:")
                    print(f"  📋 Function: {tool_call.function.name}")
                    print(f"  📝 Arguments: {tool_call.function.arguments}")
                    print(f"  🆔 Call ID: {tool_call.id}")

                print("="*60)
                return f"Assistant wants to use tools: {[tc.function.name for tc in assistant_message.tool_calls]}"

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
