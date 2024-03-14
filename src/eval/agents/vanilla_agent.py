from abc import ABC

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable, RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_tool

from src.eval.agents.langchain_agent import LangchainAgent
from src.eval.envs.env import Env
from template_generation.template_generation_prompts import get_execution_system_prompt


class VanillaAgent(LangchainAgent, ABC):

    def __init__(self, env: Env):
        super().__init__(env)
        self.tools = None
        self.chat = None
        self.execution_messages = None
        self.agent_executor = None

    async def _create_agent_executor(self, user_prompt: str) -> AgentExecutor:
        execution_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", get_execution_system_prompt()),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

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
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=50,
            early_stopping_method="force",
        )

        return agent_executor
