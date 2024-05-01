from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor

from src.eval.agents.base_agent import BaseAgent
from src.eval.agents.utils.tools_utils import parse_tool
from src.eval.envs.base_env import BaseEnv


class LangchainAgent(BaseAgent, ABC):
    name = "langchain"

    def __init__(self, name: str):
        super().__init__(name)
        self.tools = None

    @abstractmethod
    async def _create_agent_executor(self, **kwargs) -> AgentExecutor:
        pass

    async def _init_tools(self, env: BaseEnv):
        tool_dicts = await env.get_tools()
        self.tools = [parse_tool(tool_dict['function'], env) for tool_dict in tool_dicts]

    async def run(self, env: BaseEnv, user_prompt: str, **kwargs):
        await self._init_tools(env)
        kwargs['user_prompt'] = user_prompt
        agent_executor = await self._create_agent_executor(**kwargs)
        messages = await agent_executor.ainvoke(
            {"input": user_prompt}
        )
        return messages
