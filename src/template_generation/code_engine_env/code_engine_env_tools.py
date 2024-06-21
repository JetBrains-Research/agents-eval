code_engine_tools_to_handler = {
    "list-directory": "/file-system/list-directory",
    "create-directory": "/file-system/create-directory",
    "create-file": "/file-system/create-file",
    "get-file-text": "/document/get-file-text",
    "set-file-text": "/document/set-file-text",
}

code_engine_tools = [
    {
        "type": "function",
        "function": {
            "name": "list-directory",
            "description": "Gets a list of files and directories within given directory path. "
                           "Returns the contents of the given directory or exception description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Path from the working directory to the directory to be listed."
                    }
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create-directory",
            "description": "Create new directory in given parent directory with given name if it doesn't exist. "
                           "Returns empty string is case of success or exception description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parentDirectory": {
                        "type": "string",
                        "description": "Path from the working directory to the parent directory "
                                       "where new directory should be created."
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the new directory that should be created."
                    }
                },
                "required": ["parentDirectory", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create-file",
            "description": "Create new file in given parent directory with given name if it doesn't exist. "
                           "Returns empty string is case of success or exception description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parentDirectory": {
                        "type": "string",
                        "description": "Path from the working directory to the parent directory "
                                       "where new file should be created."
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the new file that should be created."
                    }
                },
                "required": ["parentDirectory", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get-file-text",
            "description": "Reads file by given path. "
                           "Returns text of the file or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "Path from working directory to the file that should be read."
                    },
                },
                "required": ["filePath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set-file-text",
            "description": "Set given text to the file by given path. "
                           "Returns text description of success or exception.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filePath": {
                        "type": "string",
                        "description": "Path from working directory to the file that should be modified."
                    },
                    "text": {
                        "type": "string",
                        "description": "Text that should be written to the file."
                    },
                },
                "required": ["filePath", "text"]
            }
        }
    }
]

meta_code_engine_tools = [
    {
        "type": "function",
        "function": {
            "name": "reset",
            "description": "Reset working directory to initial state.",
            "parameters": {
                "type": "object",
                "properties": {},
                'required': []
            },
        }
    },
]
