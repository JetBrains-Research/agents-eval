from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.eval.prompts.base_prompt import BasePrompt


class SimplePrompt(BasePrompt):

    async def chat(self, user_text_query: str, **kwargs) -> ChatPromptTemplate:
        execution_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", kwargs.get('execution_system_prompt')),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        return execution_prompt
