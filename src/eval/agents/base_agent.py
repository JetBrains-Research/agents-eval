from abc import ABC, abstractmethod

from src.eval.envs.base_env import BaseEnv


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, user_prompt: str, **kwargs):
        pass

    @abstractmethod
    async def init_tools(self, env: BaseEnv):
        pass
