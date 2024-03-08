from openai import AsyncOpenAI

from src.eval.agents.openai_agent import chat_completion_request
from src.eval.metrics.metrics_prompts import get_gen_golden_diff_metric_prompt, \
    get_gen_vanilla_golden_diff_metric_prompt
from src.utils.git_utils import get_diff_between_directories


async def gen_golden_diff_metric(gen_project_path: str, golden_project_path: str) -> tuple[str, int]:
    diff = get_diff_between_directories(golden_project_path, gen_project_path)
    chat_response = await chat_completion_request(AsyncOpenAI(), messages=[
        {
            "role": "system",
            "content": get_gen_golden_diff_metric_prompt()
        },
        {
            "role": "user",
            "content": diff
        }
    ])
    print(chat_response.choices[0].message.content)
    score = -1
    try:
        score = int(chat_response.choices[0].message.content)
    except ValueError:
        print("Can not parse score from response:", chat_response.choices[0].message.content)
    return diff, score


async def gen_vanilla_golden_diff_metric(gen_project_path: str, vanilla_project_path: str, golden_project_path: str) -> \
        tuple[str, str, int]:
    vanilla_diff = get_diff_between_directories(golden_project_path, vanilla_project_path)
    gen_diff = get_diff_between_directories(golden_project_path, gen_project_path)

    chat_response = await chat_completion_request(AsyncOpenAI(), messages=[
        {
            "role": "system",
            "content": get_gen_vanilla_golden_diff_metric_prompt()
        },
        {
            "role": "user",
            "content": f"First diff:\n{vanilla_diff}\nSecond diff:\n{gen_diff}"
        }
    ])
    print(chat_response.choices[0].message.content)
    score = -1
    try:
        score = int(chat_response.choices[0].message.content)
    except ValueError:
        print("Can not parse score from response:", chat_response.choices[0].message.content)

    return vanilla_diff, gen_diff, score
