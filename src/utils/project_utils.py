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


MEDIA_EXTENSIONS = {'.jpg', '.png', '.gif', '.jpeg', '.svg', '.bmp', '.tiff', '.webp', '.heic', '.psd', '.raw', '.mp3',
                    '.mp4', '.mov', '.wmv', '.avi', '.mkv'}


def walk_files(project_path: str, ignore_hidden: bool, ignore_media: bool):
    for root, dirs, files in os.walk(project_path):
        if ignore_hidden:
            dirs[:] = [d for d in dirs if not d[0] == '.']
            files = [f for f in files if not f[0] == '.']
        if ignore_media:
            files = [f for f in files if not os.path.splitext(f)[1] in MEDIA_EXTENSIONS]
        yield root, dirs, files


def get_project_file_tree_as_dict(project_path: str,
                                  ignore_media: bool = True,
                                  ignore_hidden: bool = True) -> Dict[str, str]:
    file_tree = {}
    for root, dirs, files in walk_files(project_path, ignore_media, ignore_hidden):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                print(str(file_path))
                file_tree[str(file_path)] = content
            except Exception as e:
                print(f"Can not rad file {file_path}", e)

    return file_tree
