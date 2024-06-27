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
from src.utils.git_utils import clone_repo
from src.utils.hf_utils import load_data
from src.utils.project_utils import get_project_file_tree_as_dict


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

    # TODO: metrics by files

    with open(metrics_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(['id', 'full_name', 'owner', 'name'] + list(quality_metrics.keys()))
        writer.writerow([gen_template_result['id'],
                         gen_template_result['full_name'],
                         gen_template_result['owner'],
                         gen_template_result['name']] + list(quality_metrics.values()))


def get_cost_metrics(gen_template_result, agent_name: str, repos_path: str, output_path: str):
    metrics_path = os.path.join(output_path, f'cost_metrics.csv')
    if os.path.exists(metrics_path) and gen_template_result['id'] in list(pd.read_csv(metrics_path)['id']):
        print(f"Skipping project: {gen_template_result['full_name']}")
        return

    gen_files_count = len(list(
        get_project_file_tree_as_dict(gen_template_result['project_template_path'],
                                      ignore_hidden=False).keys()))
    golden_files_count = len(list(
        get_project_file_tree_as_dict(
            os.path.join(repos_path, f"{gen_template_result['owner']}__{gen_template_result['name']}"),
            ignore_hidden=False).keys()))

    langsmith_project_name = f"{gen_template_result['full_name']}-{agent_name}"
    client = Client()
    if not client.has_project(langsmith_project_name):
        return

    langsmith_project = client.read_project(project_name=langsmith_project_name)
    intermediate_steps_count, run_url = get_intermediate_steps_count(langsmith_project_name)

    with open(metrics_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(
                ['id', 'full_name', 'owner', 'name', 'time', 'gen_files_count', 'golden_files_count',
                 'total_tokens', 'prompt_tokens',
                 'completion_tokens', 'intermediate_steps_count', 'run_url'])
        writer.writerow(
            [gen_template_result['id'], gen_template_result['full_name'], gen_template_result['owner'],
             gen_template_result['name'], gen_template_result['time'],
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
            for _, dp in df.iterrows():
                get_quality_metrics(dp, config.repos_path, output_path)
                get_cost_metrics(dp, agent_name, config.repos_path, output_path)
                await get_quality_compare_metrics(dp, projects, config.repos_path, output_path)


@hydra.main(config_path="../../configs/template_generation", config_name="metrics", version_base=None)
def main(config: DictConfig) -> None:
    asyncio.run(eval_metrics(config))


if __name__ == '__main__':
    load_dotenv()
    main()
