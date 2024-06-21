from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.eval.prompts.openai_chat_prompt import OpenAIChatPrompt


class SimplePrompt(OpenAIChatPrompt):

    def __init__(self, execution_system_prompt: str):
        self._execution_system_prompt = execution_system_prompt

    async def execution_prompt(self, **kwargs) -> ChatPromptTemplate:
        execution_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", dedent(self._execution_system_prompt)),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        return execution_prompt
