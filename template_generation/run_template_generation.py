import asyncio
import csv
import os
import re
import shutil
import time
from collections import defaultdict

import hydra
from datasets import Dataset
from dotenv import load_dotenv
from langchain_core.tracers.context import tracing_v2_enabled
from omegaconf import DictConfig

from src.eval.agents.openai_planning_agent import OpenAiPlanningAgent
from src.eval.agents.openai_vanilla_agent import OpenAiVanillaAgent
from src.eval.envs.http_env import HttpEnv
from src.utils.git_utils import clone_repo
from src.utils.hf_utils import load_data
from template_generation.template_generation_prompts import get_planning_system_prompt, \
    get_execution_system_prompt, get_vanilla_user_prompt, get_user_prompt


async def run_template_generation(projects: Dataset, language: str, config: DictConfig) -> dict[str, list]:
    os.makedirs(config.gen_templates_results_path, exist_ok=True)

    for project in projects:
        repo_owner, repo_name = project["owner"], project["name"]
        print(f"Processing project {repo_owner}__{repo_name}")

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
                get_user_prompt(project['full_name'], project['description'], language, project['additional_context']),
            ),
            (
                planning_agent,
                {'agent_name': 'gpt-4-planning', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_user_prompt(project['full_name'], project['description'], language, project['additional_context']),
            ),
            (
                OpenAiVanillaAgent(env, get_execution_system_prompt()),
                {'agent_name': 'gpt-4-vanilla', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_vanilla_user_prompt(project['full_name'], project['description'], language,
                                        project['additional_context']),
            )
        ]

        for agent, agent_init_params, user_prompt in agents:
            start_time = time.time()
            # Init agent
            await agent.init(**agent_init_params)

            # Init template directory
            agent_template_path = os.path.join(config.gen_templates_path, f'{repo_owner}__{repo_name}_{agent.name}')
            if os.path.exists(agent_template_path):
                shutil.rmtree(agent_template_path)
            os.makedirs(agent_template_path, exist_ok=True)

            # Init environment
            await agent.env.init({'content_root_path': agent_template_path})

            with tracing_v2_enabled(project_name="-".join([agent.name, project["full_name"]])):
                messages, telemetry = await agent.run(user_prompt)

            end_time = time.time()
            row = (project['id'], project['full_name'], project['name'], project['owner'],
                   end_time - start_time, telemetry,
                   agent_template_path, messages['input'], messages['output'],
                   list(map(lambda s: (str(s[0].to_json()), str(s[1])), messages['intermediate_steps'])))

            with open(os.path.join(config.gen_templates_results_path, f'{agent.name}.csv'), 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(
                        ['id', 'full_name', 'name', 'owner', 'time', 'telemetry', 'template_path', 'input', 'output',
                         'intermediate_steps'])
                writer.writerow(row)


def add_additional_context(project, config: DictConfig):
    repo_owner, repo_name = project["owner"], project["name"]
    repo_dir = os.path.join(config.repos_path, f"{repo_owner}__{repo_name}")
    readme_path = os.path.join(repo_dir, 'README.md')
    with open(readme_path, 'r') as f:
        readme_content = f.read()
        readme_title = readme_content.split('## ')[0]
        readme_title_without_links = re.sub(r'\!?\[(.*?)\]\((.*?)\)', r'\1', readme_title)
        readme_title_without_links = re.sub(r'\!?\[(.*?)\]\((.*?)\)', r'\1', readme_title_without_links)
        project['additional_context'] = readme_title_without_links
    return project


async def clone_repos(projects: Dataset, config: DictConfig):
    for project in projects:
        repo_owner, repo_name = project["owner"], project["name"]
        repo_dir = os.path.join(config.repos_path, f"{repo_owner}__{repo_name}")
        if not os.path.exists(repo_dir):
            await clone_repo(repo_owner, repo_name, repo_dir)


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    load_dotenv()

    category, split = 'java', 'test'
    selected = [197]
    df = load_data(category, split)
    df = df.filter(lambda x: x['id'] in selected)
    asyncio.run(clone_repos(df, config))
    df = df.map(lambda x: add_additional_context(x, config))
    asyncio.run(run_template_generation(df, category, config))
    os.makedirs(config.gen_templates_results_path, exist_ok=True)


if __name__ == '__main__':
    main()
