from abc import ABC, abstractmethod

from planning_library.action_executors import MetaTools
from planning_library.strategies import BaseCustomStrategy

from src.eval.agents.base_agent import BaseAgent
from src.eval.agents.utils.tools_utils import parse_tool, AsyncTool
from src.eval.envs.base_env import BaseEnv


class LangchainStrategicAgent(BaseAgent, ABC):
    name = "langchain"

    def __init__(self):
        self.tools = None
        self.meta_tools = None

    @abstractmethod
    async def _create_strategy(self) -> BaseCustomStrategy:
        pass

    async def init_tools(self, env: BaseEnv):
        tools = []
        tool_dicts = await env.get_tools()
        for tool_dict in tool_dicts:
            tools.append(parse_tool(tool_dict['function'], env))
        self.tools = tools

        # TODO: find better solution to set meta tools
        self.meta_tools = MetaTools(
            reset=AsyncTool(env=env, name='reset', description='Reset environment', parameters={})
        )

    async def run(self, user_prompt: str, **kwargs):
        strategy_executor = await self._create_strategy()
        messages = await strategy_executor.ainvoke(
            {"input": user_prompt}
        )
        return messages
