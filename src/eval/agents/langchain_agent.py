from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor

from src.eval.agents.agent import IAgent
from src.eval.agents.utils.langchain_utils import parse_tools, create_chat
from src.eval.envs.env import Env


class LangchainAgent(IAgent, ABC):

    def __init__(self, env: Env):
        super().__init__(env)
        self.tools = None
        self.chat = None

    @abstractmethod
    async def _create_agent_executor(self, user_prompt: str) -> AgentExecutor:
        pass

    async def init(self, **kwargs):
        self.tools = await parse_tools(self.env)
        self.name = kwargs.get('agent_name')
        self.chat = create_chat(
            kwargs.get('model_name'),
            kwargs.get('temperature'),
            kwargs.get('model_kwargs'))

    async def run(self, use_prompt: str):
        agent_executor = await self._create_agent_executor(use_prompt)

        return await agent_executor.ainvoke(
            {"input": use_prompt}
        )
