from abc import ABC, abstractmethod

from src.eval.envs.base_env import BaseEnv


class BaseAgent(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, env: BaseEnv, user_prompt: str, **kwargs):
        pass
        # while true:
        #     command = requests.get('ura/server/ide/{user_prompt}')
        #     if command = 'finish':
        #         return
        #     env.run_command(command.name, command.params)
        #
