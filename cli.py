import asyncio
from chatbot import Chatbot


class CLI:
    """Command line interface for the chatbot."""

    def __init__(self):
        self.chatbot = Chatbot()

    def print_welcome(self):
        """Print welcome message and setup information."""
        print("Welcome to the AI Chatbot with Tools!")
        print("Type 'quit' to exit")
        print("-" * 50)
        print(f"Using model: {self.chatbot.model_name}")
        print(f"Available tools: {self.chatbot.get_available_tools()}")
        print("-" * 50)

    def print_goodbye(self):
        """Print goodbye message."""
        print("\nGoodbye!")

    async def run(self):
        """Main application loop."""
        self.print_welcome()

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() == 'quit':
                    self.print_goodbye()
                    break

                if user_input.lower() == 'clear':
                    self.chatbot.clear_history()
                    print("Conversation history cleared!")
                    continue

                if user_input.lower() == 'help':
                    self.print_help()
                    continue

                if user_input:
                    response = await self.chatbot.send_message(user_input)
                    print("\nBot:", response)
                else:
                    print("Please enter a message or type 'quit' to exit.")

            except KeyboardInterrupt:
                self.print_goodbye()
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again or type 'quit' to exit.")

    def print_help(self):
        """Print help information."""
        print("\nAvailable commands:")
        print("  quit  - Exit the chatbot")
        print("  clear - Clear conversation history")
        print("  help  - Show this help message")
        print(f"\nAvailable tools: {', '.join(self.chatbot.get_available_tools())}")
        print("\nYou can ask the chatbot to read or write files within the current directory.")


async def main():
    """Entry point for the application."""
    cli = CLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
