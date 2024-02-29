import json

from openai import AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

from src.eval.agents.agent import Agent
from src.utils.tokenization_utils import TokenizationUtils

GPT_MODEL = "gpt-4-1106-preview"
PROFILE_NAME = "openai-gpt-4"
MAX_TOKENS = 128000


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
async def chat_completion_request(client: AsyncOpenAI, messages, tools=None, tool_choice=None, model=GPT_MODEL):
    tokenization_utils = TokenizationUtils(PROFILE_NAME)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=tokenization_utils.truncate(messages, MAX_TOKENS),
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate chat completion response")
        print(f"Exception: {e}")
        return e


async def get_plan(client: AsyncOpenAI, planning_system_prompt: str, user_prompt: str) -> str:
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
        client, messages
    )

    print(chat_response.choices[0].message.content)
    return chat_response.choices[0].message.content


async def run_tool_calls_loop(
        client: AsyncOpenAI, agent: Agent, execution_system_prompt: str, user_prompt: str, plan: str
) -> list[tuple[str, str]]:
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

    while run_tool_calls:
        try:
            chat_response = await chat_completion_request(
                client, messages, tools=agent.get_tools()
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
            function_response = agent.run(function_name, function_args)
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
