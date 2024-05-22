import asyncio
import logging
import os
from enum import Enum
from typing import Optional, Callable, Any

import aiohttp

from src.utils.jsonl_utils import append_to_jsonl
from src.utils.github.github_utils import make_github_http_request, clone_repo, GITHUB_API_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LoadTarget(Enum):
    ISSUES = "issues"
    COMMENTS = "comments"
    PULLS = "pulls"
    PULLS_COMMENTS = "pulls/comments"
    REPOS = "repos"
    ACTIONS_RUNS = "actions/runs"

    def __str__(self):
        return self.value


class GithubDataProvider:

    def __init__(self, github_tokens: Optional[list[str]] = None, batch_size: int = 20, per_page: int = 100):
        self.batch_size = batch_size
        self.per_page = per_page
        self.github_tokens = github_tokens

    def load_repos_data(self, repos: list[tuple[str, str]], load_target: LoadTarget, data_path: str):
        os.makedirs(data_path, exist_ok=True)
        asyncio.run(
            self._load_by_batch(
                repos,
                lambda repo_owner, repo_name, github_token:
                self._load_repo_data_by_page(repo_owner, repo_name, github_token, load_target, data_path)
            )
        )

    def load_repos_meta(self, repos: list[tuple[str, str]], data_path: str):
        asyncio.run(
            self._load_by_batch(
                repos,
                lambda repo_owner, repo_name, github_token:
                self._load_repo_meta(repo_owner, repo_name, github_token, data_path)
            )
        )

    def clone_repos(self, repos: list[tuple[str, str]], data_path: str):
        os.makedirs(data_path, exist_ok=True)
        asyncio.run(
            self._load_by_batch(
                repos,
                lambda repo_owner, repo_name, github_token:
                self._clone_repo(repo_owner, repo_name, github_token, data_path)
            )
        )

    def _batch(self, lst: list[Any]):
        for i in range(0, len(lst), self.batch_size):
            yield lst[i:i + self.batch_size]

    async def _load_by_batch(
            self,
            repos: list[tuple[str, str]],
            task: Callable[[str, str, str], Any]
    ):
        for repos_butch in self._batch(repos):
            prepare_repositories_coroutines = []
            tokens_count = len(self.github_tokens)
            for i, repo in enumerate(repos_butch):
                repo_owner, repo_name = repo
                github_token = self.github_tokens[i % tokens_count] if self.github_tokens is not None else None
                prepare_repositories_coroutines.append(
                    task(repo_owner, repo_name, github_token)
                )
            for repositories_future in asyncio.as_completed(prepare_repositories_coroutines):
                await repositories_future

    @staticmethod
    async def _load_repo_meta(repo_owner: str, repo_name: str, github_token: str, data_path: str):
        try:
            async with (aiohttp.ClientSession() as http_session):
                logger.info(f"Started processing {repo_owner}/{repo_name}")
                data_url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}"
                github_api_response_or_error = \
                    await make_github_http_request(http_session, github_token, data_url)

                if isinstance(github_api_response_or_error, Exception):
                    logger.error(f"Failed to process {repo_owner}/{repo_name}",
                                 github_api_response_or_error)
                    return github_api_response_or_error

                if github_api_response_or_error is None:
                    return

                data = github_api_response_or_error.data
                append_to_jsonl([data], data_path)
                logger.info(f"Successfully finished processing {repo_owner}/{repo_name}")
        except asyncio.exceptions.TimeoutError as e:
            logger.error(f"Failed to process {repo_owner}/{repo_name}", e)

    async def _load_repo_data_by_page(
            self,
            repo_owner: str,
            repo_name: str,
            github_token: str,
            load_target: LoadTarget,
            data_path: str
    ):
        jsonl_path = os.path.join(data_path, f"{repo_owner}__{repo_name}.jsonl")
        if os.path.exists(jsonl_path):
            logger.info(f"Data for repo {repo_owner}/{repo_name} is already loaded")
            return
        try:
            logger.info(f"Started processing {repo_owner}/{repo_name}")
            current_url = f"{GITHUB_API_URL}/repos/{repo_owner}/{repo_name}/{load_target}?per_page={self.per_page}&state=all"
            async with (aiohttp.ClientSession() as http_session):
                while current_url is not None:
                    github_api_response_or_error = \
                        await make_github_http_request(http_session, github_token, current_url)

                    if isinstance(github_api_response_or_error, Exception):
                        logger.error(f"Finished processing {repo_owner}/{repo_name} with exception",
                                     github_api_response_or_error)
                        return github_api_response_or_error

                    data = github_api_response_or_error.data
                    append_to_jsonl(data, data_path)

                    # Actual for actions not to load after some date
                    if len(data) < self.per_page:
                        current_url = None
                    else:
                        current_url = github_api_response_or_error.headers.get("next", None)

                logger.info(f"Successfully finished processing {repo_owner}/{repo_name}")
        except asyncio.exceptions.TimeoutError as e:
            logger.error(f"Failed to process {repo_owner}/{repo_name}", e)

        return None

    @staticmethod
    async def _clone_repo(repo_owner: str, repo_name: str, github_token: str, data_path: str) -> Optional[Exception]:
        repo_dir = f"{data_path}/{repo_owner}__{repo_name}"
        if os.path.exists(repo_dir):
            print(f"Repo {repo_owner}/{repo_name} has been already cloned")
            return None
        return await clone_repo(repo_owner, repo_name, github_token, repo_dir)
