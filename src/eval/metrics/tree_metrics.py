import asyncio
import os

from openai import AsyncOpenAI

from src.eval.agents.utils.openai_utils import chat_completion_request
from src.eval.metrics.metrics_prompts import get_gen_vanilla_golden_tree_metric_prompt
from src.eval.metrics.metrics_result import parse_json_result_comment_response
from src.utils.project_utils import get_project_file_tree


async def gen_vanilla_golden_tree_metric(gen_project_path: str, vanilla_project_path: str, golden_project_path: str) -> \
        tuple[str, str]:
    golden_tree = get_project_file_tree(golden_project_path)
    vanilla_tree = get_project_file_tree(vanilla_project_path)
    gen_tree = get_project_file_tree(gen_project_path)

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

    result = -1
    comment = ""
    try:
        result, comment = parse_json_result_comment_response(chat_response.choices[0].message.content)
        result = int(result)
    except Exception as e:
        print("Can not parse score from response:", chat_response.choices[0].message.content, e)

    return result, comment


if __name__ == '__main__':
    base_path = '/Users/Maria.Tigina/PycharmProjects/agents-eval-data/'
    asyncio.run(
        gen_vanilla_golden_tree_metric(
            os.path.join(base_path, 'gen_templates/JetBrains__intellij-platform-plugin-template_gpt-4-vanilla'),
            os.path.join(base_path, 'gen_templates/JetBrains__intellij-platform-plugin-template_gpt-4-planning'),
            os.path.join(base_path, 'repos/JetBrains__intellij-platform-plugin-template')
        )
    )
