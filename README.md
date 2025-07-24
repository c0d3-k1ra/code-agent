# Project Title: AI Chatbot with Tools

## Introduction
The AI Chatbot with Tools is a command-line interface based application that allows users to interact with an AI-powered chatbot. It utilizes the OpenAI API to generate intelligent responses and can autonomously perform goal-oriented tasks. The application also includes file management tools for secure read, write, and directory operations.

## Main Features and Functionality
- **Conversational AI Chatbot**: Engage with an AI chatbot that processes user messages and generates responses using OpenAI's language model.
- **Goal-Oriented Task Execution**: Automatically creates and executes plans to achieve user-defined goals.
- **Secure File Operations**: Provides methods to safely read, write, and list files and directories within the allowed project scope.
- **Command-Line Interface**: A user-friendly CLI for interacting with the chatbot and executing commands.

## Key Files and Their Purposes
- **`chatbot.py`**: Contains the main logic for chatbot operations, including API communication, message handling, and goal execution.
- **`cli.py`**: Implements a command-line interface for users to interact with the chatbot, providing commands and managing sessions.
- **`tools.py`**: Offers secure file operations, ensuring safe file and directory management within the project directory.
- **`requirements.txt`**: Lists the necessary Python packages for running the application.

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
1. **Run the Chatbot**: Execute the CLI program using:
   ```bash
   python cli.py
   ```
2. **Interact with the Chatbot**: Follow the on-screen instructions to send messages, run goals, and utilize available tools.
   - Type your messages and press Enter to receive responses.
   - Use commands like `quit`, `clear`, `session`, `reset`, `goal <text>`, and `help` for various functionalities.

## Contact Information
For questions or support, please contact:
- **Your Name**: [amit.upadhyay021@outlook.com]

Feel free to reach out for any help or further information regarding this project.
