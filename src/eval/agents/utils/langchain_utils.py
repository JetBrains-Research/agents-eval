from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Extra, create_model
from pydantic.v1.fields import Undefined, Field

from src.eval.envs.env import Env

PLUGIN_TO_PYTHON_TYPES = {
    "string": str,
    "integer": int,
    # TODO: Extend types matching
}


class PydanticModel(BaseModel, extra=Extra.forbid):
    pass


async def parse_tools(env: Env) -> List[StructuredTool]:
    tools = []
    tool_dicts = await env.get_tools()
    for tool_dict in tool_dicts:
        tool = parse_tool(tool_dict['function'], env)
        tools.append(tool)
    return tools


def parse_tool(tool_dict: dict, env: Env) -> StructuredTool:
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
        message = await env.run_command(name, kwargs)

        return message

    tool = StructuredTool(
        name=name,
        description=description,
        func=None,
        coroutine=tool_impl,
        args_schema=args_schema,
    )

    return tool


def create_chat(model_name: str, temperature: int, model_kwargs: dict) -> BaseChatModel:
    # TODO: Support not only openai models
    return ChatOpenAI(model_name=model_name, temperature=temperature, model_kwargs=model_kwargs)
