import csv
import os
import re

import hydra
import pandas as pd
from dotenv import load_dotenv
from omegaconf import DictConfig

from src.eval.agents.utils.tokenization_utils import TokenizationUtils
from src.eval.metrics.content_metrics import gen_golden_content_metric, gen_golden_content_metric_by_files
from src.eval.metrics.tree_metrics import gen_vanilla_golden_tree_metric
from src.utils.project_utils import get_project_file_tree_as_dict


async def eval_metrics(config: DictConfig):
    agents = ['gpt-3-5-planning', 'gpt-4-planning']
    vanilla_agent = 'gpt-4-vanilla'
    df_vanilla = pd.read_csv(os.path.join(config.gen_templates_results_path, f'{vanilla_agent}.csv'))
    df_agents = {agent: pd.read_csv(os.path.join(config.gen_templates_results_path, f'{agent}.csv')) for agent in
                 agents}

    for agent, df_agent in df_agents.items():
        for _, project in df_agent[1:].iterrows():
            agent_metrics = {}
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

            with open(os.path.join(config.gen_templates_results_path, f'{agent}-quality-metrics.csv'), 'a',
                      newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(['id', 'full_name', 'owner', 'name'] + list(agent_metrics.keys()))
                writer.writerow(
                    [project['id'], project['full_name'], project['owner'], project['name']] + list(
                        agent_metrics.values()))


def eval_costs(config: DictConfig):
    agents = ['gpt-4-vanilla', 'gpt-3-5-planning', 'gpt-4-planning']
    for agent in agents:
        df = pd.read_csv(os.path.join(config.gen_templates_results_path, f'{agent}.csv'))
        for i, project in df.iterrows():
            tokenization_utils = TokenizationUtils("openai-chat-gpt")
            input_tokens = tokenization_utils.count_tokens([{'system': project['input']}])
            output_tokens = tokenization_utils.count_tokens([{'system': project['output']}])
            intermediate_tokens = tokenization_utils.count_tokens([{'system': project['intermediate_steps']}])
            calls_chain_length = len(re.findall(r'\((.*?),\)', project['intermediate_steps']))
            files_count = len(list(get_project_file_tree_as_dict(project['template_path'], ignore_hidden=False).keys()))

            with open(os.path.join(config.gen_templates_results_path, f'{agent}-cost-metrics.csv'), 'a',
                      newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(
                        ['id', 'full_name', 'owner', 'name', 'time', 'gen_files_count', 'input_tokens', 'output_tokens',
                         'intermediate_tokens', 'calls_chain_length'])
                writer.writerow(
                    [project['id'], project['full_name'], project['owner'], project['name'], project['time'],
                     files_count, input_tokens, output_tokens, intermediate_tokens, calls_chain_length])


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig) -> None:
    # asyncio.run(eval(config))
    eval_costs(config)


if __name__ == '__main__':
    load_dotenv()
    main()
