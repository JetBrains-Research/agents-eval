from abc import ABC, abstractmethod

from src.eval.envs.env import Env


class IAgent(ABC):
    name: str = "base"

    def __init__(self, env: Env):
        self.env = env

    @abstractmethod
    async def run(self, user_prompt: str):
        pass

    @abstractmethod
    async def init(self, **kwargs):
        pass
