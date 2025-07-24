import asyncio
from chatbot import Chatbot
from logger import NexusLogger


class CLI:
    """Command line interface for the chatbot."""

    def __init__(self):
        self.chatbot = Chatbot()
        self.logger = NexusLogger()

    def print_welcome(self):
        """Print welcome message and setup information."""
        self.logger.welcome(
            self.chatbot.model_name,
            self.chatbot.get_session_id(),
            self.chatbot.get_available_tools()
        )

    def print_goodbye(self):
        """Print goodbye message."""
        self.logger.goodbye()

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
                    self.logger.success("Conversation history cleared!")
                    continue

                if user_input.lower() == 'help':
                    self.print_help()
                    continue

                if user_input.lower() == 'session':
                    self.print_session_info()
                    continue

                if user_input.lower() == 'reset':
                    new_session_id = self.chatbot.reset_session()
                    self.logger.success(f"Session reset! New session ID: {new_session_id}")
                    continue

                if user_input.lower().startswith('goal '):
                    goal_text = user_input[5:].strip()  # Remove 'goal ' prefix
                    if goal_text:
                        self.logger.user_input(user_input)
                        result = await self.chatbot.run_goal(goal_text)
                        self.logger.info(f"Goal Result: {result}")
                    else:
                        self.logger.warning("Please provide a goal after 'goal '. Example: goal Summarize all .md files into summary.md")
                    continue

                if user_input:
                    self.logger.user_input(user_input)
                    response = await self.chatbot.send_message(user_input)
                    self.logger.bot_response(response)
                else:
                    self.logger.warning("Please enter a message or type 'quit' to exit.")

            except KeyboardInterrupt:
                self.print_goodbye()
                break
            except Exception as e:
                self.logger.error(str(e))
                self.logger.warning("Please try again or type 'quit' to exit.")

    def print_session_info(self):
        """Print current session information."""
        info = self.chatbot.get_session_info()
        self.logger.session_info(info)

    def print_help(self):
        """Print help information."""
        commands = [
            "quit       - Exit the chatbot",
            "clear      - Clear conversation history",
            "session    - Show session information",
            "reset      - Reset session (new ID + clear history)",
            "goal <text> - Run autonomous goal (e.g., 'goal Summarize all .md files into summary.md')",
            "help       - Show this help message"
        ]
        self.logger.help_message(commands, self.chatbot.get_available_tools())


async def main():
    """Entry point for the application."""
    cli = CLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
