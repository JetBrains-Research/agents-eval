import asyncio
import csv
import os
from collections import defaultdict

import hydra
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv
from langsmith import Client
from omegaconf import DictConfig

from src.metrics.project_gen_metrics import gen_golden_content_metrics, gen_golden_content_metric_by_files, \
    get_closest_project_index
from src.metrics.tree_metrics import compare_tree_metric
from src.metrics.file_metrics import get_files_metrics
from src.template_generation.code_engine_env.code_engine_env_tools import code_engine_tools_to_handler
from src.utils.git_utils import clone_repo
from src.utils.hf_utils import load_data


def get_quality_metrics(gen_template_result, repos_path: str, output_path: str):
    golden_project_path = os.path.join(repos_path, f"{gen_template_result['owner']}__{gen_template_result['name']}")

    quality_metrics = {}
    metrics_path = os.path.join(output_path, f'quality_metrics.csv')
    if os.path.exists(metrics_path) and gen_template_result['id'] in list(pd.read_csv(metrics_path)['id']):
        print(f"Skipping project: {gen_template_result['full_name']}")
        return

    print(f"Processing project: {gen_template_result['full_name']}")
    gen_project_path = gen_template_result['project_template_path']

    content_metrics = gen_golden_content_metrics(gen_project_path, golden_project_path)
    quality_metrics.update(content_metrics)

    content_metric_by_files = gen_golden_content_metric_by_files(gen_project_path, golden_project_path)
    quality_metrics.update(content_metric_by_files)

    files_metrics = get_files_metrics(gen_project_path, golden_project_path)
    quality_metrics.update(files_metrics)

    with open(metrics_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(['id', 'full_name', 'owner', 'name'] + list(quality_metrics.keys()))
        writer.writerow([gen_template_result['id'],
                         gen_template_result['full_name'],
                         gen_template_result['owner'],
                         gen_template_result['name']] + list(quality_metrics.values()))


def get_cost_metrics(gen_template_result, agent_name: str, output_path: str):
    metrics_path = os.path.join(output_path, f'cost_metrics.csv')
    if os.path.exists(metrics_path) and gen_template_result['id'] in list(pd.read_csv(metrics_path)['id']):
        print(f"Skipping project: {gen_template_result['full_name']}")
        return

    langsmith_project_name = f"{gen_template_result['full_name']}-{agent_name}"
    client = Client()
    if not client.has_project(langsmith_project_name):
        return

    cost_metrics = {}
    langsmith_project = client.read_project(project_name=langsmith_project_name)
    cost_metrics['total_tokens'] = langsmith_project.total_tokens
    cost_metrics['prompt_tokens'] = langsmith_project.prompt_tokens
    cost_metrics['completion_tokens'] = langsmith_project.completion_tokens

    runs_stats = get_runs_stats(langsmith_project_name)
    cost_metrics.update(runs_stats)

    with open(metrics_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(
                ['id', 'full_name', 'owner', 'name', 'time'] + list(cost_metrics.keys()))
        writer.writerow(
            [gen_template_result['id'],
             gen_template_result['full_name'],
             gen_template_result['owner'],
             gen_template_result['name'],
             gen_template_result['time']] + list(cost_metrics.values()))


def get_runs_stats(langsmith_project_name: str) -> dict:
    client = Client()
    runs = client.list_runs(project_name=langsmith_project_name)
    traces = defaultdict(list)

    for run in runs:
        traces[run.trace_id].append(run)

    runs_stats = {
        'api_calls_count': 0,
        'api_failed_calls_count': 0,
        'llm_calls_count': 0,
        'langsmith_project_link': ""
    }

    for trace_id, trace_runs in traces.items():
        for run in trace_runs:
            if run.name == 'AgentExecutor':
                if client.run_is_shared(run.id):
                    client.unshare_run(run.id)
                runs_stats['langsmith_project_link'] = client.share_run(run.id)
            if run.name == 'ChatOpenAI':
                runs_stats['llm_calls_count'] += 1
            elif run.name in code_engine_tools_to_handler:
                runs_stats['api_calls_count'] += 1
                print(run.outputs)
                if 'Error occurred while executing command' in run.outputs['output']:
                    runs_stats['api_failed_calls_count'] += 1

    return runs_stats


async def get_quality_compare_metrics(gen_template_result, projects: Dataset, repos_path: str, output_path: str):
    golden_project_path = os.path.join(repos_path, f"{gen_template_result['owner']}__{gen_template_result['name']}")
    gen_project_path = gen_template_result['project_template_path']

    metrics_path = os.path.join(output_path, f'quality_closest_metrics.csv')
    if os.path.exists(metrics_path) and gen_template_result['id'] in list(pd.read_csv(metrics_path)['id']):
        print(f"Skipping project: {gen_template_result['full_name']}")
        return

    prove_quality_metrics = {}

    other_projects = projects.filter(lambda p: p['id'] != gen_template_result['id'])
    closest_project_id = get_closest_project_index(
        projects.filter(lambda p: p['id'] == gen_template_result['id'])['gpt_description'][0],
        list(other_projects['gpt_description'])
    )
    closest_project = other_projects[closest_project_id]
    closest_project_path = os.path.join(repos_path, f"{closest_project['owner']}__{closest_project['name']}")

    await clone_repo(closest_project["owner"], closest_project["name"], closest_project_path)
    content_metric = gen_golden_content_metrics(closest_project_path, golden_project_path)
    prove_quality_metrics.update(content_metric)

    content_metric_by_files = gen_golden_content_metric_by_files(closest_project_path, golden_project_path)
    prove_quality_metrics.update(content_metric_by_files)

    tree_metrics = await compare_tree_metric(gen_project_path,
                                             closest_project_path,
                                             golden_project_path)
    prove_quality_metrics['tree_result'] = tree_metrics.get("result", "-1")
    prove_quality_metrics['tree_comment'] = tree_metrics.get("comment", "")

    with open(metrics_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(['id', 'full_name', 'owner', 'name'] +
                            ['closest_id', 'closest_full_name', 'closest_owner', 'closest_name'] +
                            list(prove_quality_metrics.keys()))
        writer.writerow(
            [gen_template_result['id'], gen_template_result['full_name'], gen_template_result['owner'],
             gen_template_result['name']] +
            [closest_project['id'], closest_project['full_name'], closest_project['owner'], closest_project['name']]
            + list(prove_quality_metrics.values()))


async def eval_metrics(config: DictConfig):
    for entry in os.scandir(config.gen_templates_path):
        if not entry.is_dir():
            continue
        agent_name = os.path.basename(entry.path)
        for language in ['py', 'java', 'kt']:
            output_path = str(os.path.join(entry, language))
            if not os.path.exists(output_path):
                continue
            projects = load_data(language, 'dev')
            df = pd.read_csv(os.path.join(output_path, 'results.csv'))
            metrics_path = os.path.join(config.metrics_path, agent_name, language)
            os.makedirs(metrics_path, exist_ok=True)
            for _, dp in df.iterrows():
                get_quality_metrics(dp, config.repos_path, metrics_path)
                get_cost_metrics(dp, agent_name, metrics_path)
                # await get_quality_compare_metrics(dp, projects, config.repos_path, metrics_path)


@hydra.main(config_path="../../configs/template_generation", config_name="metrics", version_base=None)
def main(config: DictConfig) -> None:
    asyncio.run(eval_metrics(config))


if __name__ == '__main__':
    load_dotenv()
    main()
