from abc import ABC, abstractmethod


class Agent(ABC):

    @abstractmethod
    async def init(self, init_params: dict) -> str:
        pass

    @abstractmethod
    async def run_command(self, command_name: str, command_params: dict) -> str:
        pass

    @abstractmethod
    async def get_tools(self) -> list[str]:
        pass

    @abstractmethod
    async def get_state(self) -> str:
        pass
