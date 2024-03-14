from abc import ABC, abstractmethod


class Env(ABC):

    @abstractmethod
    async def init(self, init_params: dict) -> str:
        pass

    @abstractmethod
    async def run_command(self, command_name: str, command_params: dict) -> str:
        pass

    @abstractmethod
    async def get_tools(self) -> list[dict]:
        pass

    @abstractmethod
    async def get_state(self) -> str:
        pass
