import dataclasses
from abc import ABC, abstractmethod

from src.eval.envs.env import Env


@dataclasses.dataclass
class AgentResult:
    plan: str
    tool_calls: list[tuple[str, str]]


class Agent(ABC):
    name: str = "base"

    @abstractmethod
    async def run_tool_calls_loop(self, env: Env, execution_system_prompt: str, user_prompt: str, plan: str) \
            -> list[tuple[str, str]]:
        pass

    @abstractmethod
    async def get_plan(self, planning_system_prompt: str, user_prompt: str) -> str:
        pass

    async def run(self, env: Env,
                  user_prompt: str,
                  planning_system_prompt: str,
                  execution_system_prompt: str) -> AgentResult:
        plan = await self.get_plan(planning_system_prompt, user_prompt)
        tool_calls = await self.run_tool_calls_loop(env, execution_system_prompt, user_prompt, plan)

        return AgentResult(plan, tool_calls)
