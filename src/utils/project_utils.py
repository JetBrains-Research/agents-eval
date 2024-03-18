import os
import subprocess
from pathlib import Path
from typing import Dict


def get_project_file_tree(project_path) -> str:
    result = subprocess.run(["tree", project_path],
                            capture_output=True,
                            text=True)
    project_file_tree = result.stdout

    return project_file_tree


def get_project_file_tree_as_dict(project_path: str) -> Dict[str, str]:
    file_tree = {}
    for root, dirs, files in os.walk(project_path):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, 'r') as f:
                    print(file_path)
                    content = f.read()
                file_tree[str(file_path)] = content
            except Exception as e:
                print(f"Can not rad file {file_path}", e)

    return file_tree
