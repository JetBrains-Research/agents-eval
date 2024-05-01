from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.utils.function_calling import convert_to_openai_tool

from src.eval.agents.langchain_agent import LangchainAgent
from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.openai_chat_prompt import OpenAIChatPrompt


class OpenAILangchainAgent(LangchainAgent):
    name = "openai_langchain"

    def __init__(self, model_name: str, temperature: int, model_kwargs: dict, prompt: OpenAIChatPrompt):
        super().__init__()
        self._model_name = model_name
        self._temperature = temperature
        self._model_kwargs = model_kwargs
        self._prompt = prompt

    async def _create_agent_executor(self, **kwargs) -> AgentExecutor:
        execution_prompt = await self._prompt.execution_prompt(**kwargs)
        chat = create_chat(self._model_name, self._temperature, self._model_kwargs)
        agent: RunnableSerializable = (
                RunnablePassthrough.assign(
                    agent_scratchpad=lambda x: format_to_openai_tool_messages(
                        x["intermediate_steps"]
                    )
                )
                | execution_prompt
                | chat.bind(tools=[convert_to_openai_tool(tool) for tool in self.tools])
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
