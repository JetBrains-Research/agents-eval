import json

import hydra
import pandas as pd
from omegaconf import DictConfig

from src.data.github_data_provider import GithubDataProvider
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

PERMISSIVE_LICENSES = ["MIT License",
                       "Apache License 2.0",
                       "BSD 3-Clause New or Revised License",
                       "BSD 2-Clause Simplified License"]


def load_repos_data(config: DictConfig):
    with open(config.repos_list_path, "r", errors='ignore') as f:
        repos_search = json.load(f)
    repos = [repo['name'].split('/') for repo in repos_search['items']]
    with open(config.github_tokens_path, "r") as f:
        github_tokens = [token.strip() for token in f.readlines()]

    data_provider = GithubDataProvider(github_tokens=github_tokens)
    data_provider.load_repos_meta(repos, config.repos_meta_path)


def filter_template_repos(config: DictConfig):
    repos = read_jsonl(config.repos_meta_path)
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
                'repo_url': repo['html_url'],
                'is_template': repo['is_template'],
                'description': repo['description'],
                'template_key_words': template_keywords,
                'license': repo['license']['name'],
            })
    df = pd.DataFrame(template_repos)
    df.to_csv(config.template_repos_path, index=False)


@hydra.main(config_path="../../configs", config_name="template_generation", version_base=None)
def main(config: DictConfig):
    load_repos_data(config)
    filter_template_repos(config)


if __name__ == "__main__":
    main()
