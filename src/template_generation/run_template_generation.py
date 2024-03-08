import asyncio
import os
import shutil
from collections import defaultdict

import hydra
import pandas as pd
from datasets import Dataset
from omegaconf import DictConfig

from src.eval.agents.agent import Agent, AgentRequest, AgentResult
from src.eval.agents.planning_openai_agent import PlanningOpenAIAgent
from src.eval.agents.vanilla_openai_agent import VanillaOpenAIAgent
from src.eval.envs.http_env import HttpEnv
from src.template_generation.template_generation_prompts import get_user_prompt, get_planning_system_prompt, \
    get_execution_system_prompt, get_vanilla_user_prompt
from src.utils.git_utils import get_diff_between_directories
from src.utils.hf_utils import load_data


async def run_agent(agent: Agent, agent_request: AgentRequest, gen_template_path) -> AgentResult:
    # Init template directory
    if os.path.exists(gen_template_path):
        shutil.rmtree(gen_template_path)
    os.makedirs(gen_template_path, exist_ok=True)

    # Init environment
    await agent_request.env.init({'content_root_path': gen_template_path})
    return await agent.run(agent_request)


async def run_template_generation(projects: Dataset, language: str, config: DictConfig) -> dict[str, list]:
    results = defaultdict(list)

    for project in projects:
        repo_owner, repo_name = project["repo_owner"], project["repo_name"]
        print(f"Processing project {repo_owner}__{repo_name}")
        golden_template_path = os.path.join(config.repos_path, f'{repo_owner}__{repo_name}')

        # Init environment
        env = HttpEnv(config.docker_host, config.docker_port)

        # Agents to compare
        agents = [
            (
                VanillaOpenAIAgent(),
                AgentRequest(
                    env=env,
                    user_prompt=get_vanilla_user_prompt(project['description'], project['repo_name'], language)
                )
            ),
            (
                PlanningOpenAIAgent("gpt-4-1106-preview", "openai-gpt-4", 128000),
                AgentRequest(
                    env=env,
                    user_prompt=get_user_prompt(project['description'], project['repo_name'], language),
                    planning_system_prompt=get_planning_system_prompt(),
                    execution_system_prompt=get_execution_system_prompt(),
                )
            ),
            (
                PlanningOpenAIAgent("gpt-3.5-turbo-1106", "openai-chat-gpt-16k", 16000),
                AgentRequest(
                    env=env,
                    user_prompt=get_user_prompt(project['description'], project['repo_name'], language),
                    planning_system_prompt=get_planning_system_prompt(),
                    execution_system_prompt=get_execution_system_prompt(),
                )
            )
        ]

        for agent, agent_request in agents:
            agent_template_path = os.path.join(config.gen_templates_path, f'{repo_owner}__{repo_name}_{agent.name}')
            agent_result = await run_agent(agent, agent_request, agent_template_path)
            results[agent.name].append(
                (project['id'], project['repo_name'], project['repo_owner'],
                 agent_result.plan,
                 agent_result.tool_calls,
                 agent_template_path,
                 get_diff_between_directories(golden_template_path, agent_template_path))
            )

    return results


# def run_template_metrics(results: dict[str, list]):
#     vanilla_results = results["vanilla"]


@hydra.main(config_path="./../../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    category, split = 'kt', 'test'
    df = load_data(category, split)
    results = asyncio.run(run_template_generation(df, category, config))
    os.makedirs(config.gen_templates_results_path, exist_ok=True)
    for agent_name, agent_results in results.items():
        df_results = pd.DataFrame(
            agent_results,
            columns=['id', 'repo_name', 'repo_owner', 'plan', 'tool_calls', 'template_path', 'golden_diff'],
        )
        df_results.to_csv(os.path.join(config.gen_templates_results_path, f'{agent_name}.csv'), index=False)


if __name__ == '__main__':
    main()
