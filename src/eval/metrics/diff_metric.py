from openai import AsyncOpenAI

from src.eval.agents.openai_agent import chat_completion_request
from src.eval.metrics.metrics_prompts import get_diff_metrics_prompt
from src.utils.git_utils import get_diff_between_directories


async def diff_metric(actual_project_path: str, gen_project_path: str) -> tuple[str, int]:
    diff = get_diff_between_directories(actual_project_path, gen_project_path)
    chat_response = await chat_completion_request(AsyncOpenAI(), messages=[
        {
            "role": "system",
            "content": get_diff_metrics_prompt()
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
