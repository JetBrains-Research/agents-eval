from abc import ABC, abstractmethod

from src.eval.envs.base_env import BaseEnv


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, env: BaseEnv, user_prompt: str, **kwargs):
        pass
