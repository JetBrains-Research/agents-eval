import os
from typing import List

from flask import Flask, request, jsonify

from file_system_api import FileSystemAPI
from file_system_env_tools import read_write_fs_tools

app = Flask(__name__)

agent: FileSystemAPI = None


@app.route('/init', methods=['POST'])
def init():
    global agent
    content_root_path = request.json.get('content_root_path')
    agent = FileSystemAPI(content_root_path)
    return jsonify({"status": "success"}), 200


@app.route('/run_command', methods=['POST'])
def run():
    command_name = request.json.get('command_name')
    command_params = request.json.get('command_params')

    try:
        if command_name == 'create_directory':
            _assert_args(command_name, command_params, ['path'])
            agent.create_directory(
                path=command_params.get("path"),
            )
            message = f"Directory {command_params.get('path')} was successfully created"
        elif command_name == 'delete_directory':
            _assert_args(command_name, command_params, ['path'])
            agent.delete_directory(
                path=command_params.get("path"),
            )
            message = f"Directory {command_params.get('path')} was successfully deleted"
        elif command_name == 'create_file':
            _assert_args(command_name, command_params, ['path'])
            agent.create_file(
                path=command_params.get("path"),
                text=command_params.get("text", ""),
            )
            message = f"File {command_params.get('path')} was successfully created"
        elif command_name == 'delete_file':
            _assert_args(command_name, command_params, ['path'])
            agent.delete_file(
                path=command_params.get("path"),
            )
            message = f"File {command_params.get('path')} was successfully deleted"
        elif command_name == 'read_file':
            _assert_args(command_name, command_params, ['path'])
            message = agent.read_file(
                path=command_params.get("path"),
            )
        elif command_name == 'write_file':
            _assert_args(command_name, command_params, ['path', 'text'])
            agent.write_file(
                path=command_params.get("path"),
                text=command_params.get("text"),
            )
            message = f"Text was successfully written to the file {command_params.get('path')}"
        elif command_name == 'list_directory':
            _assert_args(command_name, command_params, ['path'])
            message = agent.list_directory(
                path=command_params.get("path"),
            )
        else:
            message = f"Unknown function {command_name}"

        return jsonify({"status": "success", "message": message}), 200

    except Exception as e:
        return jsonify({"status": "fail",
                        "message": "Exception occurred while tool call execution",
                        "error": agent.to_relative_path(str(e))}), 403


@app.route('/tools', methods=['GET'])
def get_tools():
    return jsonify(read_write_fs_tools), 200


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "pong"}), 200


@app.route('/status', methods=['GET'])
def get_status():
    try:
        file_tree = agent.get_file_tree()
        return jsonify({"status": "success", "data": file_tree}), 200
    except Exception as e:
        return jsonify({"status": "fail", "error": agent.to_relative_path(str(e))}), 403


def _assert_args(command_name: str, command_params, expected_args: List[str]):
    for arg in expected_args:
        assert command_params.get(arg), Exception(f"Argument {arg} is not provided for tool call {command_name}")


if __name__ == '__main__':
    app.run(port=os.environ.get('FLASK_RUN_PORT', 5050),
            host=os.environ.get('FLASK_RUN_HOST', '127.0.0.1'))
