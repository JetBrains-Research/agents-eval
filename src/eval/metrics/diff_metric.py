from openai import AsyncOpenAI

from src.eval.models.openai.openai_model import chat_completion_request
from src.utils.git_utils import get_diff_between_directories


async def diff_metric(actual_project_path: str, gen_project_path: str) -> tuple[str, int]:
    diff = get_diff_between_directories(actual_project_path, gen_project_path)
    chat_response = await chat_completion_request(AsyncOpenAI(), messages=[
        {
            "role": "system",
            "content": "Estimate the difference between two projects. "
                       "Return 1 if they are the same in terms of functionality or 0 if the essential part is missed."
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
        print("Invalid resonance:", chat_response.choices[0].message.content)
    return diff, score
