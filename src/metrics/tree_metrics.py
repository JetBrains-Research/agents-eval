import json
from typing import Any

from openai import AsyncOpenAI

from src.eval.agents.utils.openai_utils import chat_completion_request
from src.metrics.metrics_prompts import get_gen_vanilla_golden_tree_metric_prompt
from src.metrics.metrics_result import parse_json_response
from src.utils.project_utils import get_project_file_tree


async def compare_tree_metric(gen_project_path: str, vanilla_project_path: str, golden_project_path: str) \
        -> dict[str, Any]:
    gen_tree = get_project_file_tree(gen_project_path)
    vanilla_tree = get_project_file_tree(vanilla_project_path)
    golden_tree = get_project_file_tree(golden_project_path)

    chat_response = await chat_completion_request(AsyncOpenAI(), messages=[
        {
            "role": "system",
            "content": get_gen_vanilla_golden_tree_metric_prompt()
        },
        {
            "role": "user",
            "content": f"Golden tree:\n{golden_tree}\nFirst tree:\n{vanilla_tree}\nSecond tree:\n{gen_tree}"
        }
    ])

    json_response = {"unparsed_response": chat_response.choices[0].message.content}
    try:
        json_response = parse_json_response(chat_response.choices[0].message.content)
        return json_response
    except Exception as e:
        print("Can not parse score from response json'''...''':", chat_response.choices[0].message.content, e)

    try:
        json_response = json.loads(chat_response.choices[0].message.content)
        return json_response
    except Exception as e:
        print("Can not parse score from response dict:", chat_response.choices[0].message.content, e)

    return json_response
