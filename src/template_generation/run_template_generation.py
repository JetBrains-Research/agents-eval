import asyncio
import os
import shutil

import hydra
import pandas as pd
from omegaconf import DictConfig
from openai import AsyncOpenAI

from src.eval.metrics.diff_metric import diff_metric
from src.eval.models.openai.openai_model import run_tool_calls_loop, get_plan
from src.template_generation.file_system_agent import FileSystemAgent
from src.template_generation.template_generation_prompts import get_user_prompt, get_planning_system_prompt, \
    get_execution_system_prompt


async def run_template_generation(projects: pd.DataFrame,
                                  project_path: str,
                                  templates_path: str) -> pd.DataFrame:
    results = []

    for i, project in projects.iterrows():
        repo_owner, repo_name = project["url"].split('/')[-2:]
        print(f"Processing project {i}: {repo_owner}__{repo_name}")

        gen_template_path = os.path.join(templates_path, f'{repo_owner}__{repo_name}_gen')
        if os.path.exists(gen_template_path):
            shutil.rmtree(gen_template_path)
        os.makedirs(gen_template_path, exist_ok=True)

        file_system_agent = FileSystemAgent(gen_template_path)

        # Run planning
        user_prompt = get_user_prompt(project['description'])
        planning_system_prompt = get_planning_system_prompt()
        plan = await get_plan(AsyncOpenAI(), planning_system_prompt, user_prompt)

        # Run plan execution
        execution_system_prompt = get_execution_system_prompt()
        tool_calls = await run_tool_calls_loop(AsyncOpenAI(), file_system_agent,
                                               execution_system_prompt, user_prompt, plan)

        # Compare with golden project
        template_path = os.path.join(project_path, f'{repo_owner}__{repo_name}')
        diff, metric = await diff_metric(template_path, gen_template_path)
        results.append((project['id'], plan, tool_calls, diff, metric))

    return pd.DataFrame(results)


@hydra.main(config_path="./../../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    df = pd.read_csv(config.template_repos_path)
    df_results = asyncio.run(
        run_template_generation(
            df,
            config.repos_path,
            config.gen_templates_path,
        )
    )
    df_results.to_csv(config.gen_templates_results_path, index=False)


if __name__ == '__main__':
    main()
