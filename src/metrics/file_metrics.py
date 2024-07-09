import os
from typing import Any


def calc_files_metrics(project_path: str) -> dict:
    files_metrics = {
        'files_count': 0,
        'empty_files_count': 0,
        'dirs_count': 0,
        'empty_dirs_count': 0,
        'file_tree_depth': 0,
        'has_root_dir': len(os.listdir(project_path)) == 1,
    }

    for dir, subdirs, files in os.walk(project_path):
        if '.git' in dir:
            continue
        depth = dir.count(os.path.sep) - project_path.count(os.path.sep)
        if depth > files_metrics['file_tree_depth']:
            files_metrics['file_tree_depth'] = depth
        files_metrics['dirs_count'] += 1
        if len(subdirs) == 0 and len(files) == 0:
            print(f'Empty dir: {dir}')
            files_metrics['empty_dirs_count'] += 1

        for filename in files:
            files_metrics['files_count'] += 1
            if filename == '__init__.py':
                continue
            file_path = os.path.join(dir, filename)
            if os.path.getsize(file_path) == 0:
                files_metrics['empty_files_count'] += 1

    return files_metrics


def empty_directories_count(project_path: str):
    empty_count = 0
    for dir, subdirs, files in os.walk(project_path):
        if len(subdirs) == 0 and len(files) == 0:
            empty_count += 1
    return empty_count


def get_files_metrics(gen_project_path: str, golden_project_path: str) -> dict[str, Any]:
    files_metrics = {}
    for pref, project_path in [('gen', gen_project_path), ('golden', golden_project_path)]:
        file_metrics = calc_files_metrics(project_path)
        for k, v in file_metrics.items():
            files_metrics[f'{pref}_{k}'] = v

    return files_metrics
