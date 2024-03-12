from langchain_core.tools import StructuredTool
from pydantic.v1 import Field, Extra, create_model, BaseModel
from pydantic.v1.fields import Undefined

from src.eval.envs.env import Env

PLUGIN_TO_PYTHON_TYPES = {
    "string": str,
    "integer": int,
    # TODO: Extend types matching
}


class PydanticModel(BaseModel, extra=Extra.forbid):
    pass


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
        # TODO: make async
        message = env.run_command(name, kwargs)

        return message

    tool = StructuredTool(
        name=name,
        description=description,
        func=tool_impl,
        # TODO: make async
        coroutine=None,
        args_schema=args_schema,
    )

    return tool
