import asyncio
import os
import shutil

import hydra
import pandas as pd
from datasets import Dataset
from omegaconf import DictConfig

from src.eval.agents.openai_agent import OpenAIAgent
from src.eval.envs.http_env import HttpEnv
from src.eval.metrics.diff_metric import diff_metric
from src.template_generation.template_generation_prompts import get_user_prompt, get_planning_system_prompt, \
    get_execution_system_prompt
from src.utils.hf_utils import load_data


async def run_template_generation(projects: Dataset, language: str, config: DictConfig) -> pd.DataFrame:
    results = []

    for project in projects:
        repo_owner, repo_name = project["repo_owner"], project["repo_name"]
        print(f"Processing project {repo_owner}__{repo_name}")

        gen_template_path = os.path.join(config.gen_templates_path, f'{repo_owner}__{repo_name}_gen')
        if os.path.exists(gen_template_path):
            shutil.rmtree(gen_template_path)
        os.makedirs(gen_template_path, exist_ok=True)

        # Init environment
        env = HttpEnv(config.docker_host, config.docker_port)
        await env.init({'content_root_path': gen_template_path})

        # Run agent
        agent = OpenAIAgent()
        result = await agent.run(
            env=env,
            user_prompt=get_user_prompt(project['description'], project['repo_name'], language),
            planning_system_prompt=get_planning_system_prompt(),
            execution_system_prompt=get_execution_system_prompt(),
        )

        # Compare with golden project
        template_path = os.path.join(config.repos_path, f'{repo_owner}__{repo_name}')
        diff, metric = await diff_metric(template_path, gen_template_path)
        results.append((project['id'], result.plan, result.tool_calls, diff, metric))

    return pd.DataFrame(results)


@hydra.main(config_path="./../../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    category, split = 'kt', 'test'
    df = load_data(category, split)
    df_results = asyncio.run(run_template_generation(df, category, config))
    df_results.to_csv(config.gen_templates_results_path, index=False)


if __name__ == '__main__':
    main()
