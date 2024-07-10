import json
import os
import shutil
import subprocess
from collections import defaultdict


def get_subitems(path, exclude_items = None):
    subdirs = []
    subfiles = []

    for item in os.listdir(path):
        if exclude_items and item in exclude_items:
            continue
        subpath = os.path.join(path, item)
        if os.path.isfile(subpath):
            subfiles.append(subpath)
        if os.path.isdir(subpath):
            subdirs.append(subpath)

    return subdirs, subfiles


def get_qodana_metrics(project_path: str, qodana_project_path: str, language: str) -> dict:
    if os.path.exists(qodana_project_path):
        shutil.rmtree(qodana_project_path)
    os.makedirs(qodana_project_path)

    # Sometimes root directory is subdirectory
    subdirs, subfiles = get_subitems(project_path, ['bash'])
    if len(subdirs) == 1 and len(subfiles) == 0:
        project_path = subdirs[0]

    print(f"Coping files from {project_path} to {qodana_project_path}...")
    for filename in os.listdir(project_path):
        src_file_path = os.path.join(project_path, filename)
        if os.path.isfile(src_file_path):
            shutil.copy(src_file_path, qodana_project_path)
        else:
            dst_file_path = os.path.join(qodana_project_path, filename)
            shutil.copytree(src_file_path, dst_file_path)
    print(f"Running Qodana...")
    if language == 'py':
        qodana_command = ['docker', 'run',
                          '-v', f"{qodana_project_path}:/data/project/",
                          '-v', f"{os.path.join(qodana_project_path, '.qodana')}:/data/results/",
                          '-e', f"QODANA_TOKEN={os.environ.get('QODANA_TOKEN')}",
                          'jetbrains/qodana-python']
    else:
        qodana_command = ['docker', 'run',
                          '-v', f"{qodana_project_path}:/data/project/",
                          '-v', f"{os.path.join(qodana_project_path, '.qodana')}:/data/results/",
                          '-e', f"QODANA_TOKEN={os.environ.get('QODANA_TOKEN')}",
                          'jetbrains/qodana-jvm']

    process = subprocess.run(qodana_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logs = process.stdout.decode()
    print(f"\nQodana CLI logs:\n{logs}")

    qodana_metrics = {}
    qodana_metrics['logs'] = logs

    open_in_ide_json_path = os.path.join(qodana_project_path, '.qodana', 'open-in-ide.json')
    if os.path.exists(open_in_ide_json_path):
        with open(open_in_ide_json_path) as json_file:
            data = json.load(json_file)
            qodana_metrics['url'] = data["cloud"]["url"]
    else:
        qodana_metrics['url'] = None

    results_json_path = os.path.join(qodana_project_path, '.qodana', 'report', 'results', 'result-allProblems.json')
    if os.path.exists(results_json_path):
        with open(results_json_path) as json_file:
            data = json.load(json_file)
            qodana_metrics['problems'] = data["listProblem"]
            qodana_metrics['problems_count'] = len(data["listProblem"])
            problems_by_name_count = defaultdict(int)
            for problem in data["listProblem"]:
                problems_by_name_count[problem["attributes"]["inspectionName"]] += 1
            qodana_metrics['problems_by_name_count'] = dict(problems_by_name_count)
    else:
        qodana_metrics['problems'] = None
        qodana_metrics['problems_count'] = None
        qodana_metrics['problems_by_name_count'] = None

    if process.returncode == 0:
        qodana_metrics['open_status'] = True
        qodana_metrics['error'] = None
    else:
        print(f"\nAn error occurred: {process.stderr.decode()}")
        qodana_metrics['open_status'] = False
        qodana_metrics['error'] = process.stderr.decode()

    return qodana_metrics
