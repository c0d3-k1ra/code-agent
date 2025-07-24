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

    async def send_message(self, message):
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        try:
            # Send request to API
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7
            )

            # Get assistant's message
            assistant_message = response.choices[0].message.content

            # Add assistant's response to conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            return f"Error: {str(e)}"

async def main():
    print("Welcome to the AI Chatbot!")
    print("Type 'quit' to exit")
    print("-" * 50)

    chatbot = Chatbot()
    print(f"Using model: {chatbot.model_name}")
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
