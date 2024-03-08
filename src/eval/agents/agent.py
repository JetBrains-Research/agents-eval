import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

from src.eval.envs.env import Env


@dataclasses.dataclass
class AgentRequest:
    env: Env
    user_prompt: str
    planning_system_prompt: Optional[str] = None
    execution_system_prompt: Optional[str] = None


@dataclasses.dataclass
class AgentResult:
    plan: Optional[str]
    tool_calls: list[tuple[str, str]]


class Agent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, agent_request: AgentRequest) -> AgentResult:
        pass
