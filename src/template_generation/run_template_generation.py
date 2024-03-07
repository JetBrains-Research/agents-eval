import asyncio
import os
import shutil

import hydra
import pandas as pd
from omegaconf import DictConfig
from openai import AsyncOpenAI

from src.docker.docker_session import docker_session
from src.docker.docker_session_config import DockerSessionConfig
from src.eval.envs.http_env import HttpEnv
from src.eval.metrics.diff_metric import diff_metric
from src.eval.agents.openai.openai_agent import run_tool_calls_loop, get_plan
from src.template_generation.template_generation_prompts import get_user_prompt, get_planning_system_prompt, \
    get_execution_system_prompt


async def run_template_generation(projects: pd.DataFrame, config: DictConfig) -> pd.DataFrame:
    results = []

    for i, project in projects.iterrows():
        repo_owner, repo_name = project["repo_owner"], project["repo_name"]
        print(f"Processing project {i}: {repo_owner}__{repo_name}")

        gen_template_path = os.path.join(config.gen_templates_path, f'{repo_owner}__{repo_name}_gen')
        if os.path.exists(gen_template_path):
            shutil.rmtree(gen_template_path)
        os.makedirs(gen_template_path, exist_ok=True)

        # docker_config = DockerSessionConfig(
        #     image=config.docker_image,
        #     command=[],
        #     working_dir='/app',
        #     ports={5050: 5050},
        #     volumes={
        #         gen_template_path: {"bind": "/project", "mode": "rw"}
        #     }
        # )

        # with docker_session(docker_config) as s:
        http_env = HttpEnv('127.0.0.1', '5050')
        print(await http_env.ping())
        await http_env.init({'content_root_path': config.content_root_path})

        # Run planning
        user_prompt = get_user_prompt(project['description'])
        planning_system_prompt = get_planning_system_prompt()
        plan = await get_plan(AsyncOpenAI(), planning_system_prompt, user_prompt)

        # Run plan execution
        execution_system_prompt = get_execution_system_prompt()
        tool_calls = await run_tool_calls_loop(AsyncOpenAI(), http_env,
                                               execution_system_prompt, user_prompt, plan)

        # Compare with golden project
        template_path = os.path.join(config.repos_path, f'{repo_owner}__{repo_name}')
        diff, metric = await diff_metric(template_path, gen_template_path)
        results.append((project['id'], plan, tool_calls, diff, metric))

    return pd.DataFrame(results)


@hydra.main(config_path="./../../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    category = 'java'
    df = pd.read_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"))[:2]
    df_results = asyncio.run(
        run_template_generation(
            df,
            config
        )
    )
    df_results.to_csv(config.gen_templates_results_path, index=False)


if __name__ == '__main__':
    main()
