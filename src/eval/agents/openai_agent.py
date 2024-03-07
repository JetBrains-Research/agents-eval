import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, wait_random_exponential, stop_after_attempt

from src.eval.agents.agent import Agent
from src.eval.envs.env import Env
from src.utils.tokenization_utils import TokenizationUtils

DEFAULT_MODEL = "gpt-4-1106-preview"
DEFAULT_PROFILE_NAME = "openai-gpt-4"
DEFAULT_MAX_TOKENS = 128000


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
async def chat_completion_request(client: AsyncOpenAI, messages: list[dict[str, str]], model: str = DEFAULT_MODEL,
                                  max_tokens: int = DEFAULT_MAX_TOKENS, profile_name: str = DEFAULT_PROFILE_NAME,
                                  tools=None, tool_choice=None) -> ChatCompletion:
    tokenization_utils = TokenizationUtils(profile_name)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=tokenization_utils.truncate(messages, max_tokens),
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate chat completion response")
        print(f"Exception: {e}")
        return e


class OpenAIAgent(Agent):
    name = "OpenAI"

    def __init__(self, model: str = DEFAULT_MODEL,
                 profile_name: str = DEFAULT_PROFILE_NAME,
                 max_tokens: int = DEFAULT_MAX_TOKENS):
        self.model = model
        self.profile_name = profile_name
        self.max_tokens = max_tokens
        self.client = AsyncOpenAI()

    async def get_plan(self, planning_system_prompt: str, user_prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": planning_system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        chat_response = await chat_completion_request(
            client=self.client,
            messages=messages,
            model=self.model,
            max_tokens=self.max_tokens,
            profile_name=self.profile_name,
        )

        print(chat_response.choices[0].message.content)
        return chat_response.choices[0].message.content

    async def run_tool_calls_loop(self, agent: Env, execution_system_prompt: str, user_prompt: str, plan: str) \
            -> list[tuple[str, str]]:
        messages = [
            {
                "role": "system",
                "content": execution_system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            },
            {
                "role": "system",
                "content": plan,
            }
        ]

        all_tool_calls = []
        run_tool_calls = True

        tools = await agent.get_tools()

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
                function_response = await agent.run_command(function_name, function_args)
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
