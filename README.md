# Project Title: Nexus AI Assistant

## Introduction
Nexus is an advanced AI-powered assistant with a command-line interface that combines conversational AI with autonomous task execution. Named after the connection point between human goals and AI execution, Nexus utilizes the OpenAI API to generate intelligent responses and can autonomously perform goal-oriented tasks with enhanced colored logging and comprehensive file management capabilities.

## Main Features and Functionality
- **🤖 Conversational AI Assistant**: Engage with Nexus, an intelligent AI assistant that processes user messages and generates responses using OpenAI's language model.
- **🎯 Autonomous Goal Execution**: Automatically creates comprehensive plans and executes them step-by-step to achieve user-defined goals with context-aware decision making.
- **🎨 Enhanced Colored Logging**: Beautiful, color-coded console output with different colors for different types of operations (goals, tools, errors, success messages).
- **📁 Comprehensive File Logging**: All detailed operations are logged to timestamped files in the `logs/` directory for debugging and audit trails.
- **🔧 Secure File Operations**: Provides methods to safely read, write, and list files and directories within the allowed project scope.
- **💬 Interactive CLI**: A user-friendly command-line interface with session management and helpful commands.

## Key Files and Their Purposes
- **`chatbot.py`**: Contains the main logic for Nexus operations, including API communication, message handling, and autonomous goal execution with context-aware decision making.
- **`cli.py`**: Implements a command-line interface for users to interact with Nexus, providing commands and managing sessions with enhanced user experience.
- **`logger.py`**: **NEW!** Enhanced logging system with colored console output and comprehensive file logging to `logs/` directory.
- **`tools.py`**: Offers secure file operations, ensuring safe file and directory management within the project directory.
- **`requirements.txt`**: Lists the necessary Python packages including the new `colorama` dependency for colored output.
- **`logs/`**: Directory containing timestamped log files with detailed operation history (automatically created, ignored by git).

## Installation Instructions
1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    ```
2. **Navigate to the Project Directory**:
    ```bash
    cd <project-directory>
    ```
3. **Install Dependencies**: Ensure Python is installed, then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
4. **Set Up Environment Variables**: Create a `.env` file in the project directory and add your OpenAI API key and other necessary configurations:
    ```plaintext
    OPENAI_API_KEY=your_api_key_here
    API_URL=https://api.openai.com/v1
    MODEL_NAME=gpt-3.5-turbo
    ```

## Usage
1. **Run Nexus**: Execute the CLI program using:
   ```bash
   python cli.py
   ```
2. **Interact with Nexus**: Follow the on-screen instructions to send messages, run goals, and utilize available tools.
   - Type your messages and press Enter to receive responses from Nexus.
   - Use commands like `quit`, `clear`, `session`, `reset`, `goal <text>`, and `help` for various functionalities.

## 🎨 Enhanced Logging Features
- **Colored Console Output**: Different colors for different types of operations:
  - 🎯 **Magenta**: Goal execution start
  - 📋 **Cyan**: Plans and information
  - ⚡ **Yellow**: Execution status
  - 🔄 **Blue**: Actions being performed
  - 🔧 **Cyan → Green**: Tool execution and results
  - ✅ **Green**: Success messages
  - ❌ **Red**: Error messages
  - ⚠️ **Yellow**: Warning messages

- **File Logging**: All operations are automatically logged to timestamped files in the `logs/` directory:
  - Format: `nexus_YYYYMMDD_HHMMSS.log`
  - Contains detailed debug information, user inputs, bot responses, and tool executions
  - Useful for debugging and tracking conversation history

## 🎯 Goal Execution Examples
```bash
# Example goal commands:
goal Create a summary of all Python files in this directory
goal Write a README file explaining the project structure
goal Analyze the code and suggest improvements
goal Create a backup of all important files
```

## 🤖 Meet Nexus
Nexus is your intelligent AI assistant that:
- Understands complex goals and breaks them into actionable steps
- Uses available tools autonomously to complete tasks
- Provides clear, colored feedback on progress
- Maintains conversation context and session history
- Logs all activities for transparency and debugging

## Contact Information
For questions or support, please contact:
- **Your Name**: [amit.upadhyay021@outlook.com]

Feel free to reach out for any help or further information regarding this project.
