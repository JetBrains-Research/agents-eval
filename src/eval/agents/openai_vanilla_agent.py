from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

from src.eval.agents.openai_langchain_agent import OpenAiLangchainAgent
from src.eval.envs.env import Env


class OpenAiVanillaAgent(OpenAiLangchainAgent):

    def __init__(self,
                 env: Env,
                 execution_system_prompt: str
                 ):
        super().__init__(env)
        self.execution_system_prompt = execution_system_prompt

    async def _get_execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        execution_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.execution_system_prompt),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name='chat_history', optional=True),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        return execution_prompt
