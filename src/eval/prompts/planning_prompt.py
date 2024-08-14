from textwrap import dedent

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.eval.agents.utils.openai_utils import create_chat
from src.eval.prompts.openai_chat_prompt import OpenAIChatPrompt


class PlanningPrompt(OpenAIChatPrompt):

    def __init__(self, model_name: str, temperature: int, model_kwargs: dict,
                 planning_system_prompt_path: str, execution_system_prompt_path: str):
        self._model_name = model_name
        self._temperature = temperature
        self._model_kwargs = model_kwargs
        self._planning_system_prompt = self._read_prompt(planning_system_prompt_path)
        self._execution_system_prompt = self._read_prompt(execution_system_prompt_path)

    async def execution_prompt(self, **kwargs) -> ChatPromptTemplate:
        planning_prompt = [
            SystemMessage(content=dedent(self._planning_system_prompt)),
            HumanMessage(content=kwargs.get("user_prompt")),
        ]

        chat = create_chat(self._model_name, self._temperature, self._model_kwargs)
        plan = await chat.ainvoke(planning_prompt)
        print(f"Received plan:\n{plan.content}")

        system_prompt = dedent(self._execution_system_prompt).replace('{', '{{').replace('}', '}}')
        plan_prompt = plan.content.replace('{', '{{').replace('}', '}}')

        execution_messages = [
            ("system", system_prompt),
            ("user", "{input}"),
            ("system", plan_prompt),
            MessagesPlaceholder(variable_name='chat_history', optional=True),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]

        execution_prompt = ChatPromptTemplate.from_messages(
            execution_messages
        )

        return execution_prompt
