import asyncio
import os
import subprocess
from typing import Optional

from git import Repo


async def clone_repo(repo_owner: str, repo_name: str, repo_dir: str) -> Optional[Exception]:
    if os.path.exists(repo_dir):
        print(f"Repo {repo_owner}__{repo_name} has been already cloned")
        return None
    try:
        git_cmd = ["git", "clone", f"https://github.com/{repo_owner}/{repo_name}.git", repo_dir]
        process = await asyncio.create_subprocess_exec(*git_cmd)
        stdout, stderr = await process.communicate()
        print(f"Repository {repo_owner}__{repo_name} cloned successfully to repo_dir.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository {repo_owner}__{repo_name}", e)
        return e


def get_diff_between_directories(actual_project_path: str, gen_project_path: str) -> str:
    repo_a = Repo.init(actual_project_path)
    repo_b = Repo.init(gen_project_path)

    result = subprocess.run(["git", "diff", "--no-index", actual_project_path, gen_project_path],
                            capture_output=True,
                            text=True)
    diff = result.stdout

    return diff
