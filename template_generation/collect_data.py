import json
import os

import huggingface_hub
import hydra
import pandas as pd
from datasets import Dataset, DatasetDict
from omegaconf import DictConfig

from src.data.github_data_provider import GithubDataProvider
from src.utils.hf_utils import CATEGORIES, FEATURES, HUGGINGFACE_REPO, load_data
from src.utils.jsonl_utils import read_jsonl

TEMPLATE_KEYWORDS = [
    "template",
    "boilerplate",
    "starter",
    "skeleton",
    "blueprint",
    "scaffold",
    "pattern",
    "seed",
    "example",
    "demo",
    "sample",
    "showcase",
    "illustration",
    "exemplar",
    "use case",
    "prototype"
]

PERMISSIVE_LICENSES = ['MIT License',
                       'Apache License 2.0',
                       'BSD 3-Clause "New" or "Revised" License',
                       'BSD 2-Clause "Simplified" License']


def load_repos_data(config: DictConfig):
    for category in CATEGORIES:
        with open(os.path.join(config.data_path, f"{category}_search.json"), "r", errors='ignore') as f:
            repos_search = json.load(f)
        repos = [repo['name'].split('/') for repo in repos_search['items']]

        with open(config.github_tokens_path, "r") as f:
            github_tokens = [token.strip() for token in f.readlines()]

        data_provider = GithubDataProvider(github_tokens=github_tokens)
        data_provider.load_repos_meta(repos, os.path.join(config.data_path, f"{category}_repos_meta.jsonl"))


def filter_template_repos(config: DictConfig):
    for category in CATEGORIES:
        repos = read_jsonl(os.path.join(config.data_path, f"{category}_repos_meta.jsonl"))
        template_repos = []
        for repo in repos:
            if repo['license'] is None or repo['license']['name'] not in PERMISSIVE_LICENSES:
                continue
            if repo['description'] is None:
                repo['description'] = ''
            template_keywords = [token for token in TEMPLATE_KEYWORDS if token in repo['description'].lower()]
            if repo['is_template'] or len(template_keywords):
                template_repos.append({
                    'repo_owner': repo['full_name'].split('/')[0],
                    'repo_name': repo['full_name'].split('/')[1],
                    'html_url': repo['html_url'],
                    'is_template': repo['is_template'],
                    'description': repo['description'],
                    'template_keywords': template_keywords,
                    'topics': repo['topics'],
                    'license': repo['license']['name'],
                    'size': repo['size']
                })
        df = pd.DataFrame(template_repos)
        df.sort_values(by='repo_owner', key=lambda col: col.str.lower(), ascending=True, inplace=True)
        df.insert(0, 'id', range(0, len(df)))
        df.to_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"), index=False)


def upload_to_hf(config: DictConfig):
    huggingface_hub.login(token=os.environ['HUGGINGFACE_TOKEN'])

    for category in CATEGORIES:
        df = Dataset.from_csv(
            os.path.join(config.data_path, f'{category}_template_repos.csv'),
            features=FEATURES['template_generation_data'],
        )
        dataset_dict = DatasetDict({
            'dev': df,
            'test': df.filter(lambda dp: dp['id'] in config['splits'][category]),
            'train': df.filter(lambda dp: dp['id'] not in config['splits'][category]),
        })
        dataset_dict.push_to_hub(HUGGINGFACE_REPO, category)


def clone_repos(config: DictConfig):
    for category in CATEGORIES:
        df = load_data(category, 'test')
        with open(config.github_tokens_path, 'r') as f:
            github_tokens = [t.strip() for t in f.readlines()]
        github_data_provider = GithubDataProvider(github_tokens=github_tokens)
        github_data_provider.clone_repos([(d["repo_owner"], d["repo_name"]) for d in df], config.repos_path)


@hydra.main(config_path="../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig):
    # load_repos_data(config)
    # filter_template_repos(config)
    # upload_to_hf(config)
    clone_repos(config)


if __name__ == "__main__":
    main()
