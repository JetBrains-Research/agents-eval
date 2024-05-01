from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic.v1 import BaseModel, Extra, create_model
from pydantic.v1.fields import Undefined, Field

from src.eval.envs.base_env import BaseEnv

PLUGIN_TO_PYTHON_TYPES = {
    "string": str,
    "integer": int,
    # TODO: Extend types matching
}


class PydanticModel(BaseModel, extra=Extra.forbid):
    pass


class ResetTool(BaseTool, BaseModel):
    env: BaseEnv
    name: str = 'reset'
    description: str = "Reset environment"
    parameters: dict = {}

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        pass

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        args_schema = create_model(f"{self.name}_args_schema", __base__=PydanticModel, **self.parameters)
        args_schema.required = []

        try:
            message = await self.env.reset()
        except Exception as e:
            return f"Failed to run command: {e}"

        return message


def parse_tool(tool_dict: dict, env: BaseEnv) -> StructuredTool:
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
