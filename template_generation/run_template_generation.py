import asyncio
import csv
import json
import os
import shutil
import time

import hydra
from datasets import Dataset
from dotenv import load_dotenv
from langchain_core.tracers.context import tracing_v2_enabled
from langsmith import Client
from omegaconf import DictConfig
from tenacity import stop_after_attempt, retry

from src.eval.agents.agent import IAgent
from src.eval.agents.openai_planning_agent import OpenAiPlanningAgent
from src.eval.agents.openai_vanilla_agent import OpenAiVanillaAgent
from src.eval.envs.http_env import HttpEnv
from src.utils.hf_utils import load_data
from template_generation.template_generation_prompts import get_planning_system_prompt, \
    get_execution_system_prompt, get_vanilla_user_prompt, get_user_prompt


@retry(stop=stop_after_attempt(3))
async def run_template_generation_for_project(agent: IAgent, agent_init_params: dict, user_prompt: str, project,
                                              gen_templates_path: str) -> tuple:
    start_time = time.time()
    # Init agent
    await agent.init(**agent_init_params)

    # Init template directory
    agent_template_path = os.path.join(gen_templates_path, f'{project["owner"]}__{project["name"]}_{agent.name}')
    if os.path.exists(agent_template_path):
        shutil.rmtree(agent_template_path)
    os.makedirs(agent_template_path, exist_ok=True)

    # Init environment
    await agent.env.init({'content_root_path': agent_template_path})

    langsmith_project_name = "-".join([agent.name, project["full_name"]])
    client = Client()
    if client.has_project(langsmith_project_name):
        client.delete_project(project_name=langsmith_project_name)
    with tracing_v2_enabled(project_name=langsmith_project_name):
        messages = await agent.run(user_prompt)

    intermediate_steps = json.dumps(
        list(map(lambda s: {"s0": s[0].dict(), "s1": s[1]}, messages['intermediate_steps'])))
    end_time = time.time()
    # messages['intermediate_steps'][0][0].to_json()['kwargs']['message_log'][0].to_json()
    row = (project['id'], project['full_name'], project['name'], project['owner'], end_time - start_time,
           agent_template_path, messages['input'], messages['output'], intermediate_steps)

    return row


async def run_template_generation(projects: Dataset, language: str, config: DictConfig) -> dict[str, list]:
    os.makedirs(config.gen_templates_results_path, exist_ok=True)

    for project in projects:
        print(f"Processing project {project['owner']}__{project['name']}")

        # Init environment
        env = HttpEnv(config.docker_host, config.docker_port)

        # Planning agent
        planning_agent = OpenAiPlanningAgent(
            env,
            get_planning_system_prompt(),
            get_execution_system_prompt(),
        )

        # Agents to compare
        agents = [
            (
                planning_agent,
                {'agent_name': 'gpt-3-5-planning', 'model_name': 'gpt-3.5-turbo-1106', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_user_prompt(project['full_name'], project['description'], language, project['gpt_description']),
            ),
            (
                planning_agent,
                {'agent_name': 'gpt-4-planning', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_user_prompt(project['full_name'], project['description'], language, project['gpt_description']),
            ),
            (
                OpenAiVanillaAgent(env, get_execution_system_prompt()),
                {'agent_name': 'gpt-4-vanilla', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_vanilla_user_prompt(project['full_name'], project['description'], language,
                                        project['gpt_description']),
            )
        ]

        for agent, agent_init_params, user_prompt in agents:
            row = await run_template_generation_for_project(
                agent, agent_init_params, user_prompt, project, config.gen_templates_path)

            result_path = os.path.join(config.gen_templates_results_path, f'{language}-{agent.name}.csv')
            with open(result_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(
                        ['id', 'full_name', 'name', 'owner', 'time', 'template_path', 'input', 'output',
                         'intermediate_steps'])
                writer.writerow(row)


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    load_dotenv()

    category, split = 'java', 'test'
    df = load_data(category, split)
    df = df.filter(lambda x: x['id'] in [57, 197])
    asyncio.run(run_template_generation(df, category, config))
    os.makedirs(config.gen_templates_results_path, exist_ok=True)


if __name__ == '__main__':
    main()
