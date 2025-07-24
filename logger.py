import os
import logging
from datetime import datetime
from colorama import init, Fore, Back, Style
from typing import Optional

# Initialize colorama for cross-platform color support
init(autoreset=True)

class NexusLogger:
    """Enhanced logging system for Nexus AI Assistant with colors and file logging."""

    def __init__(self, bot_name: str = "Nexus"):
        self.bot_name = bot_name
        self.setup_file_logging()

    def setup_file_logging(self):
        """Setup file logging to logs directory."""
        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"nexus_{timestamp}.log")

        # Configure file logger
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
            ]
        )
        self.file_logger = logging.getLogger('nexus')

    def _log_to_file(self, level: str, message: str):
        """Log message to file."""
        if level.upper() == 'DEBUG':
            self.file_logger.debug(message)
        elif level.upper() == 'INFO':
            self.file_logger.info(message)
        elif level.upper() == 'SUCCESS':
            self.file_logger.info(f"SUCCESS: {message}")
        elif level.upper() == 'ERROR':
            self.file_logger.error(message)
        elif level.upper() == 'GOAL':
            self.file_logger.info(f"GOAL: {message}")

    def welcome(self, model_name: str, session_id: str, tools: list):
        """Print welcome message with bot branding."""
        print(f"{Fore.CYAN}{Style.BRIGHT}🤖 Welcome to {self.bot_name} AI Assistant!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'quit' to exit{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'─' * 50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Using model: {model_name}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Session ID: {session_id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Available tools: {tools}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'─' * 50}{Style.RESET_ALL}")
        self._log_to_file('INFO', f"Session started - Model: {model_name}, Tools: {tools}")

    def goodbye(self):
        """Print goodbye message."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}👋 Goodbye from {self.bot_name}!{Style.RESET_ALL}")
        self._log_to_file('INFO', "Session ended")

    def user_input(self, message: str):
        """Log user input."""
        self._log_to_file('DEBUG', f"User input: {message}")

    def bot_response(self, message: str):
        """Print and log bot response."""
        print(f"\n{Fore.GREEN}{self.bot_name}:{Style.RESET_ALL} {message}")
        self._log_to_file('INFO', f"Bot response: {message}")

    def info(self, message: str):
        """Print info message."""
        print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")
        self._log_to_file('INFO', message)

    def success(self, message: str):
        """Print success message."""
        print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        self._log_to_file('SUCCESS', message)

    def error(self, message: str):
        """Print error message."""
        print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")
        self._log_to_file('ERROR', message)

    def warning(self, message: str):
        """Print warning message."""
        print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")
        self._log_to_file('INFO', f"WARNING: {message}")

    def goal_start(self, goal: str):
        """Print goal execution start."""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🎯 Goal: {goal}{Style.RESET_ALL}")
        self._log_to_file('GOAL', f"Goal started: {goal}")

    def goal_plan(self, plan: str):
        """Print goal plan."""
        print(f"{Fore.CYAN}📋 Plan:{Style.RESET_ALL}\n{plan}")
        self._log_to_file('GOAL', f"Plan created: {plan}")

    def goal_executing(self):
        """Print goal execution start."""
        print(f"{Fore.YELLOW}⚡ Executing...{Style.RESET_ALL}")
        self._log_to_file('GOAL', "Goal execution started")

    def goal_action(self, action: str):
        """Print goal action."""
        print(f"{Fore.BLUE}🔄 {action}{Style.RESET_ALL}")
        self._log_to_file('GOAL', f"Action: {action}")

    def goal_complete(self, result: str):
        """Print goal completion."""
        print(f"{Fore.GREEN}{Style.BRIGHT}✅ Goal completed!{Style.RESET_ALL}")
        self._log_to_file('GOAL', f"Goal completed: {result}")

    def tool_execution(self, tool_name: str, result: str):
        """Print tool execution with result."""
        print(f"{Fore.CYAN}🔧 {tool_name}{Style.RESET_ALL} {Fore.WHITE}→{Style.RESET_ALL} {Fore.GREEN}{result}{Style.RESET_ALL}")
        self._log_to_file('DEBUG', f"Tool executed: {tool_name} -> {result}")

    def session_info(self, info: dict):
        """Print session information."""
        print(f"\n{Fore.MAGENTA}📊 Session Information:{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}Session ID:{Style.RESET_ALL} {info['session_id']}")
        print(f"  {Fore.CYAN}Messages:{Style.RESET_ALL} {info['message_count']}")
        print(f"  {Fore.CYAN}Tool calls:{Style.RESET_ALL} {info['tool_calls_count']}")
        self._log_to_file('INFO', f"Session info requested: {info}")

    def help_message(self, commands: list, tools: list):
        """Print help message."""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🆘 Available commands:{Style.RESET_ALL}")
        for cmd in commands:
            print(f"  {Fore.YELLOW}{cmd}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Available tools:{Style.RESET_ALL} {', '.join(tools)}")
        print(f"\n{Fore.GREEN}You can ask {self.bot_name} to read or write files within the current directory.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Use 'goal' command for autonomous task execution with automatic tool usage.{Style.RESET_ALL}")
        print(f"{Fore.BLUE}All requests are grouped by session ID for tracking in LiteLLM.{Style.RESET_ALL}")
        self._log_to_file('INFO', "Help requested")
