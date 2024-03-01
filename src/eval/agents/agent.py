from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def run(self, function_name: str, function_params: dict) -> str:
        pass

    @abstractmethod
    def get_tools(self) -> list[str]:
        pass
