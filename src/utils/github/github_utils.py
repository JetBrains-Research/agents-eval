import asyncio
import dataclasses
import logging
import subprocess
import time
from datetime import datetime
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

import aiohttp
from tenacity import after_log, before_sleep_log, retry, retry_if_result, stop_after_attempt, wait_fixed

GITHUB_API_TRIES_LIMIT = 10
OTHER_ERRORS_SLEEP_TIME = 10
TIME_DIVERGENCE_CONST = 300
GITHUB_API_URL = "https://api.github.com"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
Github API specific headers
"""
RETRY_AFTER = "Retry-After"  # Indicates when the request should be retried after hitting secondary rate limit
X_RATELIMIT_RESET = "X-RateLimit-Reset"  # Indicates when the primary rate limit will be reset


@dataclasses.dataclass(frozen=True)
class GithubRepository:
    """
    Github repository github with branch, last commit SHA and collection timestamp
    """

    repo_id: Optional[int]
    name: str
    owner: str
    created_at: Optional[datetime]
    branch: Optional[str]
    commit_sha: Optional[str]
    collection_timestamp: datetime
    meta: Optional[dict]
    problems: Optional[str]


@dataclasses.dataclass(frozen=True)
class GithubApiRequestQuery:
    """
    Search request for Github API containing created_at date range, query based on Github API query language and
    some other parameters like sorting.
    """

    created_at_start_date: datetime
    created_at_end_date: datetime
    search_query: str
    other_parameters: str


@dataclasses.dataclass(frozen=True)
class GithubApiResponse:
    """
    Basic Github API response with one header "next" (link to the next page of results in search) if it exists
    """

    data: dict
    headers: dict


@dataclasses.dataclass(frozen=True)
class GithubApiListRepositoriesResponse:
    """
    Search response which contains repository github, link to the next page of results if any and basic information
    like total number of found repositories and whether the search result is incomplete.
    """

    total_count: int
    incomplete_results: bool
    repositories: List[GithubRepository]
    next_page_url: Optional[str]


GithubApiResponseOrError = Union[GithubApiResponse, Exception]
GithubRepositoryOrError = Union[GithubRepository, Exception]
GithubApiListRepositoriesResponseOrError = Union[GithubApiListRepositoriesResponse, Exception]


# Github API related errors


class GithubApiError(Exception):
    pass


class NotRetryableGithubApiError(Exception):
    pass


# General requests methods
def return_last_value(retry_state):
    """return the result of the last call attempt"""
    if retry_state.args:
        logger.error(f"Not processed: url {retry_state.args[-1]}")
    else:
        logger.error(f"Not processed: args - {retry_state.args} kwargs - {retry_state.kwargs}")
    return retry_state.outcome.result()


@retry(
    reraise=True,
    wait=wait_fixed(OTHER_ERRORS_SLEEP_TIME),
    stop=stop_after_attempt(GITHUB_API_TRIES_LIMIT),
    retry=retry_if_result(lambda res: isinstance(res, Exception) and not isinstance(res, NotRetryableGithubApiError)),
    before_sleep=before_sleep_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
    retry_error_callback=return_last_value,
)
async def make_github_http_request(
        http_session: aiohttp.ClientSession,
        github_token: str,
        url: str,
) -> GithubApiResponseOrError:
    """
    Make http request for specified url with github authorization and return http response body
    or throw an aggregated error.
    :param http_session: http session
    :param github_token: GitHub auth token
    :param url: url to open
    :return: response body and important headers or throws an exception
    """

    headers = {
        "Authorization": f"token {github_token}",
        # "Accept": "application/vnd.github.mercy-preview+json",  # allows to retrieve topics from repositories
        "Accept": "application/vnd.github+json",
        # according to the recommendation https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28
    }

    try:
        logger.debug(f"Trying to make a request: {url}")
        async with http_session.get(url, headers=headers, allow_redirects=False) as response:
            status_code = response.status

            if status_code == 200:
                response_headers = {}
                if "next" in response.links and "url" in response.links["next"]:
                    response_headers["next"] = response.links["next"]["url"]
                return GithubApiResponse(await response.json(), response_headers)

            if status_code == 301:
                # Sometimes action requests are redirected.
                url_redirected = response.headers["Location"]
                return await make_github_http_request(http_session, github_token, url_redirected)

            if status_code == 302:  # the URL is redirected if we download logs.
                url_redirected = response.headers["Location"]
                return await make_github_http_request(http_session, github_token, url_redirected)

            elif status_code == 403:
                return await handle_github_rate_limit(response)

            elif status_code == 504:
                return await handle_github_ban(response)

            elif status_code in [404, 422, 409, 451, 410, 502]:
                # Not retryable errors:
                # 404 - Not Found
                # 422 - Unprocessable Entity
                # 409 - Conflict
                # 451 - Unavailable For Legal Reasons
                # 410 - Gone
                response_json = await response.json()
                error_message = response_json.get("message", f'No "message" key in response. HTTP code {status_code}.')
                logger.error(f"{error_message} for {url}; {response}")
                return NotRetryableGithubApiError(error_message)
            else:
                error_message = f"HTTP code {status_code} for {url}; {response}"
                logger.error(error_message)
                return GithubApiError(error_message)

    except (aiohttp.ClientError, asyncio.exceptions.TimeoutError) as e:
        error_message = f"Error happened while performing the request for {url}: {e}"
        return GithubApiError(error_message)


async def handle_github_ban(response: aiohttp.ClientResponse) -> GithubApiError:
    sleep_time = 600
    error_message = f"Github API returned 504 error. {response.url} sleep for {sleep_time}"
    logger.warning(error_message)
    await asyncio.sleep(sleep_time)
    return GithubApiError(error_message)


async def handle_github_rate_limit(response: aiohttp.ClientResponse) -> GithubApiError:
    """
    Rate limit errors from github have 403 HTTP status. This method handles rate limit errors and propagates other errors.
    To fix exceeded rate limit this method performs a delay before making the next call.
    :param response: http response
    :return: an error about rate limiting or an error during parsing the response
    """
    response_json = await response.json()

    if "message" in response_json:
        message = response_json["message"]

        if message.startswith("You have exceeded a secondary rate limit."):
            sleep_time = int(response.headers[RETRY_AFTER])
            error_message = f"Secondary Github API rate limit was exceeded. {response.url} sleep for {sleep_time}"
            logger.warning(error_message)
            await asyncio.sleep(sleep_time)
            return GithubApiError(error_message)

        elif message.startswith("API rate limit exceeded"):
            reset_time = int(response.headers[X_RATELIMIT_RESET])
            #  add some time because of possible time divergence
            sleep_time = reset_time - int(time.time()) + TIME_DIVERGENCE_CONST


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Extract repository owner and name from a github url
    https://github.com/DimaProskurin/News-Bot -> (DimaProskurin, News-Bot)
    :param url: github url
    :return: tuple with repository owner and name
    """
    owner, name = urlparse(url).path.split("/")[1:]
    return owner, name


async def clone_repo(owner: str, name: str, github_token: str, repo_dir: str) -> Optional[Exception]:
    try:
        git_cmd = ["git", "clone", f"https://{github_token}@github.com/{owner}/{name}.git", repo_dir]
        process = await asyncio.create_subprocess_exec(*git_cmd)
        stdout, stderr = await process.communicate()
        print(f"Repository {owner}/{name} cloned successfully to {repo_dir}.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository {owner}/{name}", e)
        return e
