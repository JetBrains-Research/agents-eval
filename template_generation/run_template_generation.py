import asyncio
import os
import shutil
from collections import defaultdict

import hydra
import pandas as pd
from datasets import Dataset
from omegaconf import DictConfig

from src.eval.agents.openai_planning_agent import OpenAiPlanningAgent
from src.eval.agents.openai_vanilla_agent import OpenAiVanillaAgent
from src.eval.envs.http_env import HttpEnv
from src.utils.hf_utils import load_data
from template_generation.template_generation_prompts import get_planning_system_prompt, \
    get_execution_system_prompt, get_vanilla_user_prompt


async def run_template_generation(projects: Dataset, language: str, config: DictConfig) -> dict[str, list]:
    results = defaultdict(list)

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
                get_user_prompt(project['description'], project['full_name'], language),
            ),
            (
                planning_agent,
                {'agent_name': 'gpt-4-planning', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_user_prompt(project['description'], project['full_name'], language),
            ),
            (
                OpenAiVanillaAgent(env, get_execution_system_prompt()),
                {'agent_name': 'gpt-4-vanilla', 'model_name': 'gpt-4-1106-preview', 'temperature': 0,
                 'model_kwargs': {'seed': 45}},
                get_vanilla_user_prompt(project['description'], project['full_name'], language),
            )
        ]

        for agent, agent_init_params, user_prompt in agents:
            # Init agent
            await agent.init(**agent_init_params)

            # Init template directory
            agent_template_path = os.path.join(config.gen_templates_path, f'{repo_owner}__{repo_name}_{agent.name}')
            if os.path.exists(agent_template_path):
                shutil.rmtree(agent_template_path)
            os.makedirs(agent_template_path, exist_ok=True)

            # Init environment
            await agent.env.init({'content_root_path': agent_template_path})

            messages = await agent.run(user_prompt)
            results[agent.name].append(
                (project['id'], project['full_name'], project['name'], project['owner'],
                 agent_template_path, messages['input'], messages['output'],
                 list(map(lambda s: (s[0].to_json(), s[1]), messages['intermediate_steps'])))
            )

    return results


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    category, split = 'kt', 'test'
    df = load_data(category, split)
    df = df.filter(lambda x: x['full_name'].lower() == 'JetBrains/intellij-platform-plugin-template'.lower())
    results = asyncio.run(run_template_generation(df, category, config))
    os.makedirs(config.gen_templates_results_path, exist_ok=True)
    for agent_name, agent_results in results.items():
        df_results = pd.DataFrame(
            agent_results,
            columns=['id', 'full_name', 'name', 'owner', 'template_path', 'input', 'output', 'intermediate_steps'],
        )
        df_results.to_csv(os.path.join(config.gen_templates_results_path, f'{agent_name}.csv'), index=False)


if __name__ == '__main__':
    main()
