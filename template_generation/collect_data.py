import json
import logging
import os

import huggingface_hub
import hydra
import pandas as pd
from datasets import Dataset, DatasetDict
from omegaconf import DictConfig

from src.data.github_data_provider import GithubDataProvider
from src.utils.hf_utils import CATEGORIES, FEATURES, HUGGINGFACE_REPO, load_data
from src.utils.jsonl_utils import read_jsonl

logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.INFO
)


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
        data_provider.load_repos_meta(repos, os.path.join(config.data_path, f"{category}_repos_meta_extra.jsonl"))


def filter_template_repos(config: DictConfig):
    for category in ['java', 'kt']:
        with open(os.path.join(config.data_path, f"{category}_search.json"), "r", errors='ignore') as f:
            repos_search = json.load(f)
        repo_name_to_search = {repo['name'].lower(): repo for repo in repos_search['items']}
        repos = read_jsonl(os.path.join(config.data_path, f"{category}_repos_meta.jsonl"))
        repo_name_to_json = {repo['full_name'].lower(): repo for repo in repos}
        template_repos = []
        for _, repo in repo_name_to_json.items():
            logging.info(f"Processing repo {repo['full_name']}")
            if repo['license'] is None or repo['license']['name'] not in PERMISSIVE_LICENSES:
                logging.info(f"Skipping repo {repo['full_name']} as it has not permissive license {repo['license']}")
                continue
            if repo['description'] is None:
                repo['description'] = ''
            template_keywords = [token for token in TEMPLATE_KEYWORDS if token in repo['description'].lower()]
            if repo['full_name'].lower() not in repo_name_to_search:
                logging.info(f"Skipping repo {repo['full_name'].lower()} as it is not presented in search dataset")
                continue
            repo_json = repo_name_to_search[repo['full_name'].lower()]
            if repo_json['isArchived'] or repo_json['isDisabled'] or repo_json['isLocked']:
                logging.info(f"Skipping repo {repo['full_name'].lower()} as it is archived, disabled or locked")
                continue
            if str(repo_json['updatedAt']) < '2023':
                logging.info(f"Skipping repo {repo['full_name'].lower()} as it was updated at {repo_json['updatedAt']} < 2023")
                continue
            if int(repo_json['codeLines']) > 3000:
                logging.info(f"Skipping repo {repo['full_name'].lower()} as it has {repo_json['codeLines']} > 3000")
                continue
            if repo['is_template'] or len(template_keywords):
                template_repos.append({
                    'full_name': repo['full_name'],
                    'owner': repo['full_name'].split('/')[0],
                    'name': repo['full_name'].split('/')[1],
                    'html_url': repo['html_url'],
                    'is_template': repo['is_template'],
                    'description': repo['description'],
                    'template_keywords': template_keywords,
                    'topics': repo['topics'],
                    'license': repo['license']['name'],
                    'size': repo['size'],
                    'metrics': repo_json['metrics'],
                    'languages': repo_json['languages'],
                    'language': repo_json['mainLanguage'],
                    'created_at': repo_json['createdAt'],
                    'updated_at': repo_json['updatedAt'],
                    'code_lines': repo_json['codeLines'],
                })
        df = pd.DataFrame(template_repos)
        df.to_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"), index=False)


def separate_android_repos(config: DictConfig):
    android_dfs = []

    def is_android_repo(repo) -> bool:
        return ('android' in str(repo['description']).lower() or
                'android' in str(repo['topics']).lower() or
                'android' in str(repo['full_name']).lower())

    for category in ['java', 'kt']:
        df = pd.read_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"))
        not_android_df = df[df.apply(lambda row: not is_android_repo(row), axis=1)]
        not_android_df.to_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"), index=False)
        android_df = df[df.apply(lambda row: is_android_repo(row), axis=1)]
        android_dfs.append(android_df)
    pd.concat(android_dfs, axis=0).to_csv(os.path.join(config.data_path, f"android_template_repos.csv"), index=False)


def set_ids(config: DictConfig):
    for category in CATEGORIES:
        df = pd.read_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"))
        df.sort_values(by='owner', key=lambda col: col.str.lower(), ascending=True, inplace=True)
        df.insert(0, 'id', range(0, len(df)))
        df.to_csv(os.path.join(config.data_path, f"{category}_template_repos.csv"), index=False)


def upload_to_hf(config: DictConfig):
    huggingface_hub.login(token=os.environ['HUGGINGFACE_TOKEN'])

    for category in CATEGORIES:
        df = Dataset.from_csv(
            os.path.join(config.data_path, f'{category}_template_repos.csv'),
            features=FEATURES['template_generation_data'],
        )
        test_full_names = [full_name.lower() for full_name in config['splits'][category]]
        dataset_dict = DatasetDict({
            'dev': df,
            'test': df.filter(lambda dp: dp['full_name'].lower() in test_full_names),
            'train': df.filter(lambda dp: dp['full_name'].lower() not in test_full_names),
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
    filter_template_repos(config)
    separate_android_repos(config)
    set_ids(config)
    upload_to_hf(config)
    # clone_repos(config)


if __name__ == "__main__":
    main()
