from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

from src.eval.agents.openai_langchain_agent import OpenAiLangchainAgent
from src.eval.envs.env import Env


class OpenAiPlanningAgent(OpenAiLangchainAgent):

    def __init__(self,
                 env: Env,
                 planning_system_prompt: str,
                 execution_system_prompt: str):
        super().__init__(env)
        self.planning_system_prompt = planning_system_prompt
        self.execution_system_prompt = execution_system_prompt

    async def _get_execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        planning_prompt = [
            SystemMessage(content=self.planning_system_prompt),
            HumanMessage(content=user_prompt),
        ]

        plan = await self.chat.ainvoke(planning_prompt)
        print(f"Received plan:\n{plan.content}")

        execution_messages = [
            ("system", self.execution_system_prompt),
            ("user", "{input}"),
            ("system", plan.content),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        execution_prompt = ChatPromptTemplate.from_messages(
            execution_messages
        )

        return execution_prompt
