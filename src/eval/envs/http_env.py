import json

import aiohttp

from src.eval.envs.base_env import BaseEnv


class HttpEnv(BaseEnv):

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.base_url = f'http://{self.host}:{self.port}'

    async def init(self, init_params: dict) -> None:
        url = f'{self.base_url}/init'
        headers = {'Content-type': 'application/json'}
        data = json.dumps(init_params)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                await response.text()

    async def reset(self) -> str:
        url = f'{self.base_url}/reset'

        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                return await response.text()

    async def run_command(self, command_name: str, command_params: dict) -> str:
        url = f'{self.base_url}/run_command'
        headers = {'Content-type': 'application/json'}
        data = json.dumps({"command_name": command_name,
                           "command_params": command_params})

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                return await response.text()

    async def get_state(self) -> str:
        url = f'{self.base_url}/state'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    async def get_tools(self) -> list[dict]:
        url = f'{self.base_url}/tools'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return json.loads(await response.text())

    async def ping(self) -> str:
        url = f'{self.base_url}/ping'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
