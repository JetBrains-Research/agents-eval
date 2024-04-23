from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.utils.function_calling import convert_to_openai_tool

from src.eval.agents.langchain_agent import LangchainAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.base_prompt import BasePrompt


class OpenAiLangchainAgent(LangchainAgent):

    def __init__(self,
                 prompt: BasePrompt,
                 model_name: str,
                 temperature: int,
                 model_kwargs: dict):
        super().__init__(prompt)
        self.chat = create_chat(model_name, temperature, model_kwargs)

    async def _create_agent_executor(self, execution_prompt: ChatPromptTemplate) -> AgentExecutor:
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
            # TODO: move to yaml
            verbose=False,
            return_intermediate_steps=True,
            max_iterations=50,
            early_stopping_method="force",
        )

        return agent_executor
