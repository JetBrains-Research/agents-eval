import multiprocessing
import os
import re
from typing import Optional

import hydra
import pandas as pd
import tiktoken
from dotenv import load_dotenv
from git import Repo
from omegaconf import DictConfig

from src.utils.hf_utils import CATEGORIES

tokenizer = tiktoken.encoding_for_model('gpt-4')


def count_repo_symbols(content: dict[str, str]):
    return sum([count_symbols(content) for content in content.values() if content])


def count_repo_tokens(content: dict[str, str]) -> Optional[int]:
    try:
        return sum([count_tokens(content) for content in content.values() if content])
    except Exception as e:
        print(e)
    return None


def count_repo_words(content: dict[str, str]) -> Optional[int]:
    try:
        return sum([count_words(content) for content in content.values() if content])
    except Exception as e:
        print(e)
    return None


def count_repo_lines(content: dict[str, str]):
    return sum(count_lines(content) for content in content.values() if content)


def count_symbols(text: str) -> int:
    return len(text)


def count_tokens(text: str) -> Optional[int]:
    try:
        return len(tokenizer.encode(text))
    except Exception as e:
        print(e)
    return None


def count_lines(text: str) -> int:
    return len(text.split('\n'))


def count_words(text: str) -> int:
    return len(text.split())


def get_repo_content(repos_path, owner: str, name: str) -> dict[str, str]:
    repo_path = os.path.join(repos_path, f'{owner}__{name}')
    if not os.path.exists(repo_path):
        Repo.clone_from(f'https://github.com/{owner}/{name}.git', repo_path)

    repo_content = {}
    for root, dir, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    repo_content[file_path] = f.read()
            except Exception as e:
                print('Can not read file {}'.format(file_path), e)
    return repo_content


def get_readme(repo_content):
    readme_content = None
    for f, c in repo_content.items():
        if f.lower().endswith('readme.md'):
            readme_content = c
            break
    if readme_content is None:
        return ''

    # Delete some build or other indicator links
    readme_content = re.sub(r'\[\!\[.*?\]\(.*?\)\]\(.*?\)', '', readme_content)
    readme_content = re.sub("\n+", "\n", readme_content)
    readme_content = readme_content.strip('\n')
    readme_content = readme_content.strip('#')

    return readme_content


def add_stats(config: DictConfig, dp, category: str):
    print(f"Processing {dp['owner']}/{dp['name']}")
    repo_content = get_repo_content(config.repos_path, dp['owner'], dp['name'])

    dp['repo_symbols_count'] = count_repo_symbols(repo_content)
    dp['repo_tokens_count'] = count_repo_tokens(repo_content)
    dp['repo_words_count'] = count_repo_words(repo_content)
    dp['repo_lines_count'] = count_repo_lines(repo_content)
    dp['repo_files_count'] = len(repo_content)

    code_repo_content = {f: c for f, c in repo_content.items() if f.endswith(f'.{category}')}
    dp['repo_code_symbols_count'] = count_repo_symbols(code_repo_content)
    dp['repo_code_tokens_count'] = count_repo_tokens(code_repo_content)
    dp['repo_code_words_count'] = count_repo_words(code_repo_content)
    dp['repo_code_lines_count'] = count_repo_lines(code_repo_content)
    dp['repo_code_files_count'] = len(code_repo_content)

    description = dp['description']
    dp['description_symbols_count'] = count_symbols(description)
    dp['description_tokens_count'] = count_tokens(description)
    dp['description_words_count'] = count_words(description)
    dp['description_lines_count'] = count_lines(description)

    readme = get_readme(repo_content)
    dp['readme'] = readme
    dp['readme_symbols_count'] = count_symbols(readme)
    dp['readme_tokens_count'] = count_tokens(readme)
    dp['readme_words_count'] = count_words(readme)
    dp['readme_lines_count'] = count_lines(readme)

    return dp


def add_stats_to_repo_data(config, dps: list[tuple[dict, str]]):
    return [add_stats(config, dp, category) for dp, category in dps]


def calc_stats(config: DictConfig):
    for category in CATEGORIES:
        df = pd.read_csv(os.path.join(config.data_path, f'{category}_template_repos.csv'))

        params = [(config, dp, category) for _, dp in df.iterrows()]

        cpus = multiprocessing.cpu_count()
        with multiprocessing.Pool(processes=cpus) as pool:
            results = pool.starmap(add_stats, params)
        df = pd.DataFrame(results).dropna()
        df['repo_tokens_count'] = df['repo_tokens_count'].astype('int64')
        df['repo_code_tokens_count'] = df['repo_code_tokens_count'].astype('int64')
        df['description_tokens_count'] = df['description_tokens_count'].astype('int64')
        df['readme_tokens_count'] = df['readme_tokens_count'].astype('int64')
        df.to_csv(os.path.join(config.data_path, f'{category}_template_repos.csv'), index=False)


@hydra.main(config_path="../../configs/template_generation", config_name="data", version_base=None)
def main(config: DictConfig):
    calc_stats(config)


if __name__ == "__main__":
    load_dotenv()
    main()
