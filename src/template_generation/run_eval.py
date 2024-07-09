import asyncio
import csv
import json
import os
import shutil
import time

import hydra
import pandas as pd
import yaml
from dotenv import load_dotenv
from hydra.core.hydra_config import HydraConfig
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from tenacity import retry, stop_after_attempt

from src.configs.eval_configs import EvalConfig
from src.eval.agents.base_agent import BaseAgent
from src.eval.data_sources.base_data_source import BaseDataSource
from src.eval.envs.base_env import BaseEnv
from src.template_generation.prompts import get_user_prompt


@retry(stop=stop_after_attempt(3))
async def run_template_generation_for_project(project, agent: BaseAgent, env: BaseEnv,
                                              template_generation_path: str, job_name: str) -> dict[str, any]:
    try:
        # Init template directory
        project_name = f'{project["owner"]}__{project["name"]}'
        project_template_path = os.path.join(template_generation_path, project_name)
        if os.path.exists(project_template_path):
            shutil.rmtree(project_template_path)
        os.makedirs(project_template_path)

        # Init environment
        await env.init({'content_root_path': project_template_path})

        # Build user prompt
        user_prompt = get_user_prompt(
            project['full_name'],
            project['description'],
            project['language']
        )

        # Init langsmith project
        client = Client()
        langsmith_project_name = f"{project['full_name']}-{job_name}"
        if client.has_project(langsmith_project_name):
            client.delete_project(project_name=langsmith_project_name)

        start_time = time.time()

        with tracing_v2_enabled(project_name=langsmith_project_name):
            messages = await agent.run(env, user_prompt)

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

    except Exception as e:
        print(e)
        return None
    finally:
        await env.shutdown()

    return result_dict


@retry(stop=stop_after_attempt(3))
async def run_template_generation(agent: BaseAgent, env: BaseEnv, data_source: BaseDataSource,
                                  output_path: str, job_name: str):
    for project, config in data_source:
        config_path = os.path.join(output_path, config)
        os.makedirs(config_path, exist_ok=True)
        result_path = os.path.join(config_path, "results.csv")
        if os.path.exists(result_path) and os.path.getsize(result_path) > 0:
            df = pd.read_csv(result_path)
            if project['full_name'] in list(df['full_name']):
                print(f"Skipping {project['full_name']}")
                continue
        gen_templates_path = os.path.join(config_path, "gen_templates")
        os.makedirs(gen_templates_path, exist_ok=True)

        results_dict = await run_template_generation_for_project(
            project, agent, env, gen_templates_path, job_name)

        with open(result_path, 'a', newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(results_dict.keys())
            writer.writerow(results_dict.values())


@hydra.main(config_path="../../configs/template_generation", config_name="config.yaml", version_base="1.2")
def main(cfg: EvalConfig) -> None:
    agent: BaseAgent = hydra.utils.instantiate(cfg.agent)
    env: BaseEnv = hydra.utils.instantiate(cfg.env)
    data_source: BaseDataSource = hydra.utils.instantiate(cfg.data_source)

    output_path = HydraConfig.get().run.dir
    job_name = HydraConfig.get().job.name

    asyncio.run(run_template_generation(agent, env, data_source, output_path, job_name))


def delete_langsmith_projects():
    client = Client()
    for project in client.list_projects():
        client.delete_project(project_name=project.name)


if __name__ == '__main__':
    os.environ['HYDRA_FULL_ERROR'] = '1'
    load_dotenv()
    main()
