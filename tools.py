import json
from pathlib import Path


class FileTools:
    """File system operations with security checks."""

    def __init__(self, current_dir=None):
        self.current_dir = current_dir or Path.cwd()

    def _is_safe_path(self, file_path):
        """Check if the file path is within the current directory for security."""
        try:
            # Convert to absolute path and resolve any .. or . components
            abs_path = Path(file_path).resolve()
            # Check if the path is within current directory
            return str(abs_path).startswith(str(self.current_dir.resolve()))
        except Exception:
            return False

    def read_file(self, file_path):
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

    def write_file(self, file_path, content):
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

    def execute_tool(self, tool_call):
        """Execute a tool call and return the result."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "read_file":
            return self.read_file(arguments.get("file_path"))
        elif function_name == "write_file":
            return self.write_file(arguments.get("file_path"), arguments.get("content"))
        else:
            return {"error": f"Unknown function: {function_name}"}

    @staticmethod
    def get_tool_schemas():
        """Return the OpenAI function schemas for file tools."""
        return [
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
