from abc import ABC, abstractmethod

from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from pydantic.v1 import BaseModel, Extra, create_model
from pydantic.v1.fields import Undefined, Field

from src.eval.agents.base_agent import BaseAgent
from src.eval.envs.base_env import BaseEnv
from src.eval.prompts.base_prompt import BasePrompt

PLUGIN_TO_PYTHON_TYPES = {
    "string": str,
    "integer": int,
    # TODO: Extend types matching
}


class PydanticModel(BaseModel, extra=Extra.forbid):
    pass


class LangchainAgent(BaseAgent, ABC):

    def __init__(self, prompt: BasePrompt):
        self.prompt = prompt
        self.tools = None

    @abstractmethod
    async def _create_agent_executor(self, chat_prompt: ChatPromptTemplate) -> AgentExecutor:
        pass

    async def init_tools(self, env: BaseEnv):
        tools = []
        tool_dicts = await env.get_tools()
        for tool_dict in tool_dicts:
            tool = self._parse_tool(tool_dict['function'], env)
            tools.append(tool)
        self.tools = tools

    @staticmethod
    def _parse_tool(tool_dict: dict, env: BaseEnv) -> StructuredTool:
        name = tool_dict["name"]
        description = tool_dict["description"]
        parameters = {}

        for p_name, p_data in tool_dict['parameters']['properties'].items():
            p_type = PLUGIN_TO_PYTHON_TYPES.get(p_data['type'], object)
            p_desc = p_data["description"]
            if p_name in tool_dict['parameters']['required']:
                p_default = Undefined
            else:
                p_default = ...
            parameters[p_name] = (p_type, Field(p_default, description=p_desc))

        args_schema = create_model(f"{name}_args_schema", __base__=PydanticModel, **parameters)
        args_schema.required = []  # type: ignore

        async def tool_impl(**kwargs):
            args_schema(**kwargs)
            args_schema.validate(kwargs)
            try:
                message = await env.run_command(name, kwargs)
            except Exception as e:
                return f"Failed to run command: {e}"

            return message

        tool = StructuredTool(
            name=name,
            description=description,
            func=None,
            coroutine=tool_impl,
            args_schema=args_schema,
        )

        return tool

    async def run(self, user_prompt: str, **kwargs):
        execution_prompt = await self.prompt.execution_prompt(user_prompt)
        agent_executor = await self._create_agent_executor(execution_prompt)
        messages = await agent_executor.ainvoke(
            {"input": user_prompt}
        )
        return messages
