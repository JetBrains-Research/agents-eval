from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, user_text_query: str, **kwargs):
        pass

    @abstractmethod
    async def init_tools(self, tools: list[dict]):
        pass
