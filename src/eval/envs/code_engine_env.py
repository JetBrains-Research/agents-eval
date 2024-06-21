import asyncio
import json
import os

import aiohttp
import docker

from src.eval.envs.base_env import BaseEnv
from src.template_generation.code_engine_env.code_engine_env_tools import code_engine_tools, \
    code_engine_tools_to_handler


class CodeEngineEnv(BaseEnv):

    def __init__(self, docker_image_name: str, docker_container_name: str, host: str, port: int):
        self.docker_image_name = docker_image_name
        self.docker_container_name = docker_container_name
        self.host = host
        self.port = port
        self.base_url = f'http://{self.host}:{self.port}'
        self.client = docker.from_env()
        self.init_params = None

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
        await asyncio.sleep(1)

        url = f'{self.base_url}/file-system/set-working-dir'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({'workingDir': container_path})

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                await response.text()

    async def reset(self):
        await self.shutdown()
        await self.init(self.init_params)

    async def run_command(self, command_name: str, command_params: dict) -> str:
        command_handler = code_engine_tools_to_handler[command_name]
        url = f'{self.base_url}{command_handler}'
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(command_params)

        async with (aiohttp.ClientSession() as session):
            async with session.post(url, data=data, headers=headers) as response:
                status = response.status
                text = await response.text()
                print(status, command_name, command_params, text)
                return text

    async def get_state(self) -> str:
        url = f'{self.base_url}/state'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def get_tools(self) -> list[dict]:
        return code_engine_tools


async def main():
    env = CodeEngineEnv(docker_image_name='mariatigina/code-engine:latest', docker_container_name='code-engine',
                        host='localhost', port=5050)
    await env.init({'content_root_path': '/Users/Maria.Tigina/PycharmProjects/agents-eval-data/docker_templates/test'})
    await env.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
