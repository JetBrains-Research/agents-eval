from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.eval.prompts.base_prompt import BasePrompt


class SimplePrompt(BasePrompt):

    def __init__(self, execution_system_prompt: str):
        self.execution_system_prompt = execution_system_prompt

    async def chat(self, user_prompt: str, **kwargs) -> ChatPromptTemplate:
        execution_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.execution_system_prompt),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        return execution_prompt
