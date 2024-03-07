read_fs_tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads file by given path. "
                           "Returns text of the file or None if file does not exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the file to be read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Gets a list of files and directories within given directory path. "
                           "Returns list of files and directories names, or None if given directory does not exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the directory to be listed"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

read_write_fs_tools = [
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create directory if it doesn't exist. "
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to directory to create",
                    },
                },
                "required": ["path"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_directory",
            "description": "Delete directory if exists."
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to directory to delete"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates file by given path and text content if doesn't exist. "
                           "If text is not provided, empty file will be created."
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the file to be created"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to be written into the created file"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file by given path if exists. "
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the file to be deleted"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads file by given path. "
                           "Returns text of the file or exception description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the file to be read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes text to the file by given path. "
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the file to be written"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to be written into the file"
                    }
                },
                "required": ["path", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Gets a list of files and directories within given directory path. "
                           "Returns list of files and directories names, or exception description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path from content root to the directory to be listed"
                    }
                },
                "required": ["path"]
            }
        }
    }
]
