import asyncio
import csv
import json
import os
import shutil
import time

import hydra
from dotenv import load_dotenv
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from tenacity import stop_after_attempt, retry

from src.configs.eval_configs import EvalConfig
from src.eval.agents.base_agent import BaseAgent
from src.eval.data.base import BaseDataSource
from src.eval.envs.base_env import BaseEnv
from src.template_generation.template_generation_prompts import get_user_prompt


@retry(stop=stop_after_attempt(3))
async def run_template_generation_for_project(project, agent: BaseAgent, env: BaseEnv,
                                              gen_templates_path: str, eval_name: str) -> dict[str, any]:
    start_time = time.time()
    # Init agent
    await agent.init_tools(env)

    # Init template directory
    project_template_path = os.path.join(gen_templates_path, f'{project["owner"]}__{project["name"]}_{eval_name}')
    if os.path.exists(project_template_path):
        shutil.rmtree(project_template_path)
    os.makedirs(project_template_path, exist_ok=True)

    # Init environment
    await env.init({'content_root_path': project_template_path})

    # Build user prompt
    user_prompt = get_user_prompt(
        project['full_name'],
        project['description'],
        project['language'],
        project['gpt_description']
    )

    # Init langsmith project
    langsmith_project_name = "-".join([eval_name, project["full_name"]])
    client = Client()
    if client.has_project(langsmith_project_name):
        client.delete_project(project_name=langsmith_project_name)
    with tracing_v2_enabled(project_name=langsmith_project_name):
        messages = await agent.run(user_prompt)

    end_time = time.time()

    # Collect results
    result_dict = {
        'id': project['id'],
        'full_name': project['full_name'],
        'name': project['name'],
        'owner': project['owner'],
        'language': project['language'],
        'time': end_time - start_time,
        'project_template_path': project_template_path,
        'input': messages['input'],
        'output': messages['output'],
        'intermediate_steps': json.dumps(
            list(map(lambda s: {"s0": s[0].dict(), "s1": s[1]}, messages['intermediate_steps'])))
    }

    return result_dict


async def run_template_generation(agent: BaseAgent, env: BaseEnv, data_src: BaseDataSource,
                                  output_path: str, eval_name: str):
    gen_templates_path = os.path.join(output_path, "gen_templates")
    os.makedirs(gen_templates_path, exist_ok=True)

    results_path = os.path.join(output_path, "results")
    os.makedirs(results_path, exist_ok=True)

    for project in data_src:
        results_dict = await run_template_generation_for_project(
            project, agent, env, gen_templates_path, eval_name)

        result_csv_path = os.path.join(results_path, f"{project['language']}-{eval_name}.csv")
        with open(result_csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(results_dict.keys())
            writer.writerow(results_dict.values())


@hydra.main(config_path="../../configs", version_base="1.1")
def main(cfg: EvalConfig) -> None:
    agent: BaseAgent = hydra.utils.instantiate(cfg.agent)
    env: BaseEnv = hydra.utils.instantiate(cfg.env)
    data_src: BaseDataSource = hydra.utils.instantiate(cfg.data_src)
    output_path = cfg.output_path
    eval_name = cfg.name

    asyncio.run(run_template_generation(agent, env, data_src, output_path, eval_name))


if __name__ == '__main__':
    load_dotenv()
    main()
