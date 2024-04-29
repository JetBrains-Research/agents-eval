from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor

from src.eval.agents.base_agent import BaseAgent
from src.eval.agents.utils.tools_utils import parse_tool
from src.eval.envs.base_env import BaseEnv


class LangchainAgent(BaseAgent, ABC):
    name = "langchain"

    def __init__(self):
        self.tools = None

    @abstractmethod
    async def _create_agent_executor(self, **kwargs) -> AgentExecutor:
        pass

    async def init_tools(self, env: BaseEnv):
        tools = []
        tool_dicts = await env.get_tools()
        for tool_dict in tool_dicts:
            tool = parse_tool(tool_dict['function'], env)
            tools.append(tool)
        self.tools = tools

    async def run(self, user_prompt: str, **kwargs):
        kwargs['user_prompt'] = user_prompt
        agent_executor = await self._create_agent_executor(**kwargs)
        messages = await agent_executor.ainvoke(
            {"input": user_prompt}
        )
        return messages
