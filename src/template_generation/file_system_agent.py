import os
import shutil
from typing import Optional

from src.eval.agents.agent import Agent
from src.template_generation.file_system_agent_tools import read_write_fs_tools


class FileSystemAgent(Agent):

    def __init__(self, content_root_path: str):
        self.content_root_path = content_root_path

    def _to_absolute_path(self, path: str) -> str:
        return os.path.join(self.content_root_path, path)

    def create_directory(self, path: str):
        os.makedirs(self._to_absolute_path(path), exist_ok=True)

    def delete_directory(self, path: str):
        shutil.rmtree(self._to_absolute_path(path))

    def create_file(self, path: str, text: str):
        self.create_directory(os.path.dirname(self._to_absolute_path(path)))
        with open(self._to_absolute_path(path), 'w') as file:
            file.write(text)

    def delete_file(self, path: str):
        os.remove(self._to_absolute_path(path))

    def read_file(self, path: str) -> Optional[str]:
        with open(self._to_absolute_path(path), 'r') as file:
            return file.read()

    def write_file(self, path: str, text: str):
        with open(self._to_absolute_path(path), 'w') as file:
            file.write(text)

    def list_directory(self, path: str) -> Optional[list[str]]:
        return [os.path.join(path, f) for f in os.listdir(self._to_absolute_path(path))]

    @staticmethod
    def _assert_args(function_name: str, function_args, expected_args: list[str]):
        for arg in expected_args:
            assert function_args.get(arg), Exception(f"Argument {arg} is not provided for tool call {function_name}")

    def run(self, function_name: str, function_args: dict) -> str:
        try:
            if function_name == 'create_directory':
                self._assert_args(function_name, function_args, ['path'])
                self.create_directory(
                    path=function_args.get("path"),
                )
                result = f"Directory {function_args.get('path')} was successfully created"
            elif function_name == 'delete_directory':
                self._assert_args(function_name, function_args, ['path'])
                self.delete_directory(
                    path=function_args.get("path"),
                )
                result = f"Directory {function_args.get('path')} was successfully deleted"
            elif function_name == 'create_file':
                self._assert_args(function_name, function_args, ['path'])
                self.create_file(
                    path=function_args.get("path"),
                    text=function_args.get("text", ""),
                )
                result = f"File {function_args.get('path')} was successfully created"
            elif function_name == 'delete_file':
                self._assert_args(function_name, function_args, ['path'])
                self.delete_file(
                    path=function_args.get("path"),
                )
                result = f"File {function_args.get('path')} was successfully deleted"
            elif function_name == 'read_file':
                self._assert_args(function_name, function_args, ['path'])
                result = self.read_file(
                    path=function_args.get("path"),
                )
            elif function_name == 'write_file':
                self._assert_args(function_name, function_args, ['path', 'text'])
                self.write_file(
                    path=function_args.get("path"),
                    text=function_args.get("text"),
                )
                result = f"Text was successfully written to the file {function_args.get('path')}"
            elif function_name == 'list_directory':
                self._assert_args(function_name, function_args, ['path'])
                result = self.list_directory(
                    path=function_args.get("path"),
                )
            else:
                result = f"Unknown function {function_name}"

            return str(result)

        except Exception as e:
            return (f"Exception occurred while tool call execution: "
                    f"{str(e).replace(self.content_root_path + '/', '')}")

    def get_tools(self) -> list[dict]:
        return read_write_fs_tools
