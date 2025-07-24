import json
import os
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

    def list_directory(self, directory_path="."):
        """List contents of a directory with file/folder information."""
        try:
            # Use current directory if no path provided
            if directory_path == ".":
                directory_path = str(self.current_dir)
            
            if not self._is_safe_path(directory_path):
                return {"error": "Access denied: Directory path is outside current directory"}

            path = Path(directory_path)
            
            # Make path relative to current directory if it's not absolute
            if not path.is_absolute():
                path = self.current_dir / path
                
            if not path.exists():
                return {"error": f"Directory not found: {directory_path}"}

            if not path.is_dir():
                return {"error": f"Path is not a directory: {directory_path}"}

            items = []
            for item in sorted(path.iterdir()):
                try:
                    stat_info = item.stat()
                    item_info = {
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat_info.st_size if item.is_file() else None,
                        "modified": stat_info.st_mtime,
                        "path": str(item.relative_to(self.current_dir)) if str(item).startswith(str(self.current_dir)) else str(item)
                    }
                    items.append(item_info)
                except (PermissionError, OSError):
                    # Skip items we can't access
                    continue

            return {
                "success": True,
                "directory": str(path.relative_to(self.current_dir)) if str(path).startswith(str(self.current_dir)) else str(path),
                "items": items,
                "total_items": len(items)
            }

        except PermissionError:
            return {"error": f"Permission denied: {directory_path}"}
        except Exception as e:
            return {"error": f"Error listing directory: {str(e)}"}

    def get_current_directory(self):
        """Get the current working directory."""
        try:
            return {
                "success": True,
                "current_directory": str(self.current_dir),
                "absolute_path": str(self.current_dir.resolve())
            }
        except Exception as e:
            return {"error": f"Error getting current directory: {str(e)}"}

    def change_directory(self, directory_path):
        """Change the current working directory."""
        try:
            if not self._is_safe_path(directory_path):
                return {"error": "Access denied: Directory path is outside allowed scope"}

            path = Path(directory_path)
            
            # Make path relative to current directory if it's not absolute
            if not path.is_absolute():
                path = self.current_dir / path
                
            path = path.resolve()
            
            if not path.exists():
                return {"error": f"Directory not found: {directory_path}"}

            if not path.is_dir():
                return {"error": f"Path is not a directory: {directory_path}"}

            # Update current directory
            old_dir = str(self.current_dir)
            self.current_dir = path
            
            return {
                "success": True,
                "message": f"Changed directory from {old_dir} to {str(path)}",
                "old_directory": old_dir,
                "new_directory": str(path)
            }

        except PermissionError:
            return {"error": f"Permission denied: {directory_path}"}
        except Exception as e:
            return {"error": f"Error changing directory: {str(e)}"}

    def create_directory(self, directory_path):
        """Create a new directory."""
        try:
            if not self._is_safe_path(directory_path):
                return {"error": "Access denied: Directory path is outside current directory"}

            path = Path(directory_path)
            
            # Make path relative to current directory if it's not absolute
            if not path.is_absolute():
                path = self.current_dir / path

            if path.exists():
                return {"error": f"Directory already exists: {directory_path}"}

            path.mkdir(parents=True, exist_ok=False)
            
            return {
                "success": True,
                "message": f"Directory created successfully: {directory_path}",
                "directory_path": str(path)
            }

        except PermissionError:
            return {"error": f"Permission denied: {directory_path}"}
        except Exception as e:
            return {"error": f"Error creating directory: {str(e)}"}

    def get_file_info(self, file_path):
        """Get detailed information about a file or directory."""
        try:
            if not self._is_safe_path(file_path):
                return {"error": "Access denied: File path is outside current directory"}

            path = Path(file_path)
            
            # Make path relative to current directory if it's not absolute
            if not path.is_absolute():
                path = self.current_dir / path

            if not path.exists():
                return {"error": f"Path not found: {file_path}"}

            stat_info = path.stat()
            
            info = {
                "success": True,
                "name": path.name,
                "path": str(path.relative_to(self.current_dir)) if str(path).startswith(str(self.current_dir)) else str(path),
                "absolute_path": str(path.resolve()),
                "type": "directory" if path.is_dir() else "file",
                "size": stat_info.st_size,
                "created": stat_info.st_ctime,
                "modified": stat_info.st_mtime,
                "accessed": stat_info.st_atime,
                "permissions": oct(stat_info.st_mode)[-3:],
                "is_readable": os.access(path, os.R_OK),
                "is_writable": os.access(path, os.W_OK),
                "is_executable": os.access(path, os.X_OK)
            }
            
            if path.is_file():
                info["extension"] = path.suffix
                
            return info

        except PermissionError:
            return {"error": f"Permission denied: {file_path}"}
        except Exception as e:
            return {"error": f"Error getting file info: {str(e)}"}

    def execute_tool(self, tool_call):
        """Execute a tool call and return the result."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "read_file":
            return self.read_file(arguments.get("file_path"))
        elif function_name == "write_file":
            return self.write_file(arguments.get("file_path"), arguments.get("content"))
        elif function_name == "list_directory":
            return self.list_directory(arguments.get("directory_path", "."))
        elif function_name == "get_current_directory":
            return self.get_current_directory()
        elif function_name == "change_directory":
            return self.change_directory(arguments.get("directory_path"))
        elif function_name == "create_directory":
            return self.create_directory(arguments.get("directory_path"))
        elif function_name == "get_file_info":
            return self.get_file_info(arguments.get("file_path"))
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
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List the contents of a directory with file and folder information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "The path to the directory to list (defaults to current directory if not provided)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_directory",
                    "description": "Get the current working directory path",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "change_directory",
                    "description": "Change the current working directory to a specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "The path to the directory to change to"
                            }
                        },
                        "required": ["directory_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Create a new directory at the specified path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "The path where the new directory should be created"
                            }
                        },
                        "required": ["directory_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_file_info",
                    "description": "Get detailed information about a file or directory including size, permissions, and timestamps",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file or directory to get information about"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            }
        ]