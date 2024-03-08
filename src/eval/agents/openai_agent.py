import json
from abc import ABC

from openai import AsyncOpenAI

from src.eval.agents.agent import Agent
from src.eval.agents.utils.openai_utils import DEFAULT_MODEL, DEFAULT_PROFILE_NAME, DEFAULT_MAX_TOKENS, \
    chat_completion_request
from src.eval.envs.env import Env


class OpenAIAgent(Agent, ABC):

    def __init__(self, model: str = DEFAULT_MODEL,
                 profile_name: str = DEFAULT_PROFILE_NAME,
                 max_tokens: int = DEFAULT_MAX_TOKENS):
        self.model = model
        self.profile_name = profile_name
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI()
        self.name = self.model

    async def _run_request(self, messages: list[dict]) -> str:
        chat_response = await chat_completion_request(
            client=self.client,
            messages=messages,
            model=self.model,
            max_tokens=self.max_tokens,
            profile_name=self.profile_name,
        )

        print(chat_response.choices[0].message.content)
        return chat_response.choices[0].message.content

    async def _run_tool_calls_loop(self, env: Env, messages: list[dict]) -> list[tuple[str, str]]:
        all_tool_calls = []
        run_tool_calls = True

        tools = await env.get_tools()

        while run_tool_calls:
            try:
                chat_response = await chat_completion_request(
                    client=self.client,
                    messages=messages,
                    model=self.model,
                    max_tokens=self.max_tokens,
                    profile_name=self.profile_name,
                    tools=tools
                )

                print(chat_response.choices[0].message)
                tool_calls = chat_response.choices[0].message.tool_calls
            except Exception as e:
                print(e)
                run_tool_calls = False
                continue

            if not tool_calls:
                run_tool_calls = False
                continue

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = await env.run_command(function_name, function_args)
                print(function_response)
                messages.append(
                    {
                        "role": "function",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    }
                )
                all_tool_calls.append((str(tool_call), function_response))

        return all_tool_calls
