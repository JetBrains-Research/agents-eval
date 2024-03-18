from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.utils.function_calling import convert_to_openai_tool

from src.eval.agents.langchain_agent import LangchainAgent
from src.eval.envs.env import Env


class OpenAiLangchainAgent(LangchainAgent, ABC):

    def __init__(self, env: Env):
        super().__init__(env)
        self.tools = None
        self.chat = None

    async def _create_agent_executor(self, user_prompt: str) -> AgentExecutor:
        execution_prompt = await self._get_execution_prompt(user_prompt)
        agent: RunnableSerializable = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    )
                )
                | execution_prompt
                | self.chat.bind(tools=[convert_to_openai_tool(tool) for tool in self.tools])
                | OpenAIToolsAgentOutputParser()
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=True,
            max_iterations=50,
            early_stopping_method="force",
        )

        return agent_executor

    @abstractmethod
    async def _get_execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        pass
