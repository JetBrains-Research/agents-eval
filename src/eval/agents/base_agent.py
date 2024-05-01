from abc import ABC, abstractmethod

from src.eval.envs.base_env import BaseEnv


class BaseAgent(ABC):

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, env: BaseEnv, user_prompt: str, **kwargs):
        pass
