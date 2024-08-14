import ast
import asyncio
import json
import os

import aiohttp
import docker

from src import PROJECT_DIR
from src.eval.envs.base_env import BaseEnv
from src.eval.envs.utils.tree_utils import parse_tree_structure


class CodeEngineEnv(BaseEnv):
    COMMAND_NAME_TO_CODE_ENGINE_HANDLER = {
        "list-directory": "/file-system/list-directory",
        "create-directory": "/file-system/create-directory",
        "create-file": "/file-system/create-file",
        "get-file-text": "/document/get-file-text",
        "set-file-text": "/document/set-file-text",
    }

    @staticmethod
    def _read_tools(path) -> list[dict]:
        with open(os.path.join(PROJECT_DIR, path), 'r') as file:
            tools = ast.literal_eval(file.read())

        return tools

    def __init__(self, docker_image_name: str, docker_container_name: str, host: str, port: int, tools_path: str):
        self.docker_image_name = docker_image_name
        self.docker_container_name = docker_container_name
        self.host = host
        self.port = port
        self.base_url = f'http://{self.host}:{self.port}'
        self.client = docker.from_env()
        self.init_params = None
        self.tools = self._read_tools(tools_path)

        self.command_name_to_code_engine_handler = self.COMMAND_NAME_TO_CODE_ENGINE_HANDLER
        self.command_name_to_function_handler = {
            "create-project-tree": self._run_create_file_tree
        }

    def _run_docker_container(self, local_path, container_path: str):
        volume_mapping = {local_path: {'bind': container_path, 'mode': 'rw'}}
        port_mapping = {f'{self.port}': self.port}
        container = self.client.containers.run(
            image=self.docker_image_name,
            volumes=volume_mapping,
            ports=port_mapping,
            detach=True,
            name=self.docker_container_name
        )
        self.container_id = container.id

    def _stop_docker_container(self):
        existing_containers = self.client.containers.list(all=True, filters={"name": self.docker_container_name})
        for container in existing_containers:
            container.stop()
            container.remove()

    async def shutdown(self):
        self._stop_docker_container()

    async def init(self, init_params: dict) -> None:
        await self.shutdown()
        local_path = init_params.get('content_root_path')
        container_path = f'/{os.path.basename(local_path)}'

        self._run_docker_container(local_path, container_path)
        await asyncio.sleep(2)

        url = f'{self.base_url}/file-system/set-working-dir'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'workingDir': container_path})

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                await response.text()

    async def run_command(self, command_name: str, command_params: dict) -> str:
        if command_name in self.command_name_to_code_engine_handler:
            return await self._run_code_engine_command(command_name, command_params)
        elif command_name in self.command_name_to_function_handler:
            return await self.command_name_to_function_handler[command_name](command_params)
        else:
            return f"Error occurred while tool calling. Unknown command {command_name}."

    async def _run_code_engine_command(self, command_name: str, command_params: dict) -> str:
        print(f"Running command {command_name}...")
        command_handler = self.command_name_to_code_engine_handler[command_name]
        url = f'{self.base_url}{command_handler}'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(command_params)

        async with (aiohttp.ClientSession() as session):
            async with session.post(url, data=data, headers=headers) as response:
                status = response.status
                text = await response.text()
                print(status, command_handler, command_params, text)
                if status != 200:
                    return (
                        f"Error occurred while executing command {command_handler} with parameters: {command_params}: "
                        f"status {status}: {text}")
                if text == "":
                    return f"Command {command_handler} with parameters: {command_params} executed successfully"
                print(text)
                return text

    async def _run_create_file_tree(self, command_params: dict) -> str:
        tree_structure_str = command_params['tree_structure']
        tree_structure = parse_tree_structure(tree_structure_str)
        await self._create_file_tree("", tree_structure)

    async def _create_file_tree(self, base_path, tree_structure: dict):
        for name, children in tree_structure.items():
            if name.endswith('/'):
                command_name = 'create-directory'
            else:
                command_name = 'create-file'
            await self._run_code_engine_command(command_name, {
                'parentDirectory': base_path,
                'name': name
            })
            path = os.path.join(base_path, name) if base_path != "" else name
            await self._create_file_tree(path, children)

    async def get_tools(self) -> list[dict]:
        return self.tools

    async def reset(self):
        await self.shutdown()
        await self.init(self.init_params)

    async def get_state(self) -> str:
        pass
