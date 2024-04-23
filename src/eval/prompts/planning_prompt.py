from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.base_prompt import BasePrompt


class PlanningPrompt(BasePrompt):

    def __init__(self, model_name: str, temperature: int, model_kwargs: dict,
                 planning_system_prompt: str, execution_system_prompt: str):
        self._chat = create_chat(model_name, temperature, model_kwargs)
        self._planning_system_prompt = planning_system_prompt
        self._execution_system_prompt = execution_system_prompt

    async def execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        planning_prompt = [
            SystemMessage(content=self._planning_system_prompt),
            HumanMessage(content=user_prompt),
        ]

        plan = await self._chat.ainvoke(planning_prompt)
        print(f"Received plan:\n{plan.content}")

        execution_messages = [
            ("system", self._execution_system_prompt),
            ("user", "{input}"),
            ("system", plan.content),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        execution_prompt = ChatPromptTemplate.from_messages(
            execution_messages
        )

        return execution_prompt
