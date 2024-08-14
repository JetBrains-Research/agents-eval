import os
from typing import Any

from src.eval.agents.utils.tokenization_utils import TokenizationUtils


def count_comments(file_content, file_extension):
    comment_symbols = {'py': ['#', '"""', "'''"],
                       'java': ['//', '/*', '*/'],
                       'kt': ['//', '/*', '*/']}

    comment_symbol = comment_symbols.get(file_extension)

    if comment_symbol:
        in_multiline = False
        comment_lines = 0

        for line in file_content.split('\n'):
            stripped_line = line.strip()
            if not in_multiline:
                if stripped_line.startswith(comment_symbol[0]) or stripped_line.startswith(
                        comment_symbol[1]) or stripped_line.endswith(comment_symbol[1]):
                    comment_lines += 1
                if stripped_line.startswith(comment_symbol[1]):
                    in_multiline = True

            else:
                comment_lines += 1
                if stripped_line.endswith(comment_symbol[2]):
                    in_multiline = False

        return comment_lines

    # If the file extension is not recognized, return None
    return 0


def calc_files_metrics(project_path: str) -> dict:
    files_metrics = {
        'code_lines_count': 0,
        'tokens_count': 0,
        'comment_lines_count': 0,
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
        depth = dir.count(os.path.sep) - project_path.count(os.path.sep) - 1
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
            with open(file_path, 'r') as f:
                try:
                    file_content = f.read()
                except Exception as e:
                    print(file_path, e)
                files_metrics['code_lines_count'] += len(file_content.split('\n'))
                files_metrics['comment_lines_count'] += count_comments(file_content, file_path.split('.')[-1])
                files_metrics['tokens_count'] += TokenizationUtils("gpt-4-1106-preview").count_text_tokens(file_content)
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
