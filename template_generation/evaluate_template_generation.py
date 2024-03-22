import asyncio
import csv
import os
from collections import defaultdict

import hydra
import pandas as pd
from dotenv import load_dotenv
from langsmith import Client
from omegaconf import DictConfig

from src.eval.metrics.content_metrics import gen_golden_content_metric, gen_golden_content_metric_by_files
from src.eval.metrics.tree_metrics import gen_vanilla_golden_tree_metric
from src.utils.project_utils import get_project_file_tree_as_dict


async def eval_metrics(config: DictConfig):
    agents = ['gpt-3-5-planning', 'gpt-4-planning', 'gpt-4-vanilla']
    vanilla_agent = 'gpt-4-vanilla'
    language = 'java'
    df_vanilla = pd.read_csv(os.path.join(config.gen_templates_results_path, f'{language}-{vanilla_agent}.csv'))
    df_agents = {agent: pd.read_csv(os.path.join(config.gen_templates_results_path, f'{language}-{agent}.csv')) for
                 agent in agents}

    for agent, df_agent in df_agents.items():
        results_path = os.path.join(config.gen_templates_results_path, f'{language}-{agent}-quality-metrics.csv')
        df_prev_results = None
        if os.path.exists(results_path):
            df_prev_results = pd.read_csv(results_path)
        for _, project in df_agent.iterrows():
            agent_metrics = {}
            if df_prev_results is not None and project['id'] in list(df_prev_results['id']):
                print(f"Skipping project: {project['full_name']}")
                continue

            print(f"Processing project: {project['full_name']}")
            vanilla_project_path = df_vanilla[df_vanilla['id'] == project['id']]['template_path'].values[0]
            golden_project_path = os.path.join(config.repos_path, f"{project['owner']}__{project['name']}")
            gen_project_path = project['template_path']

            content_metric = gen_golden_content_metric(gen_project_path, golden_project_path)
            agent_metrics.update(content_metric)

            content_metric_by_files = gen_golden_content_metric_by_files(gen_project_path, golden_project_path)
            agent_metrics.update(content_metric_by_files)

            tree_metrics = await gen_vanilla_golden_tree_metric(gen_project_path,
                                                                golden_project_path,
                                                                vanilla_project_path)
            agent_metrics['tree_result'] = tree_metrics.get("result", "-1")
            agent_metrics['tree_comment'] = tree_metrics.get("comment", "")

            with open(results_path, 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(['id', 'full_name', 'owner', 'name'] + list(agent_metrics.keys()))
                writer.writerow([project['id'], project['full_name'], project['owner'],
                                 project['name']] + list(agent_metrics.values()))


def eval_costs(config: DictConfig):
    agents = ['gpt-4-vanilla', 'gpt-3-5-planning', 'gpt-4-planning']
    client = Client()
    language = 'java'
    for agent in agents:
        df = pd.read_csv(os.path.join(config.gen_templates_results_path, f'{language}-{agent}.csv'))
        for i, project in df.iterrows():
            gen_files_count = len(list(
                get_project_file_tree_as_dict(project['template_path'],
                                              ignore_hidden=False).keys()))
            golden_files_count = len(list(
                get_project_file_tree_as_dict(os.path.join(config.repos_path, f"{project['owner']}__{project['name']}"),
                                              ignore_hidden=False).keys()))

            langsmith_project_name = f"{agent}-{project['full_name']}"
            if not client.has_project(langsmith_project_name):
                continue
            langsmith_project = client.read_project(project_name=langsmith_project_name)
            intermediate_steps_count, run_url = get_intermediate_steps_count(langsmith_project_name)

            with open(os.path.join(config.gen_templates_results_path, f'{language}-{agent}-cost-metrics.csv'), 'a',
                      newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(
                        ['id', 'full_name', 'owner', 'name', 'time', 'gen_files_count', 'golden_files_count',
                         'total_tokens', 'prompt_tokens',
                         'completion_tokens', 'intermediate_steps_count', 'run_url'])
                writer.writerow(
                    [project['id'], project['full_name'], project['owner'], project['name'], project['time'],
                     gen_files_count, golden_files_count, langsmith_project.total_tokens,
                     langsmith_project.prompt_tokens,
                     langsmith_project.completion_tokens, intermediate_steps_count, run_url])


def get_intermediate_steps_count(langsmith_project_name: str) -> tuple[int, str]:
    client = Client()
    runs = client.list_runs(project_name=langsmith_project_name)
    traces = defaultdict(list)

    for run in runs:
        traces[run.trace_id].append(run)

    intermediate_steps_count = 0
    share_run = ""

    for trace_id, trace_runs in traces.items():
        for run in trace_runs:
            if run.name == 'AgentExecutor':
                if client.run_is_shared(run.id):
                    client.unshare_run(run.id)
                share_run = client.share_run(run.id)
            if (run.outputs and
                    'output' in run.outputs and \
                    'return_values' in run.outputs['output'] and \
                    'intermediate_steps' in run.outputs['output']['return_values']):
                intermediate_steps_count += len(run.outputs['output']['return_values']['intermediate_steps'])

    return intermediate_steps_count, share_run


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    asyncio.run(eval_metrics(config))
    eval_costs(config)


if __name__ == '__main__':
    load_dotenv()
    main()
