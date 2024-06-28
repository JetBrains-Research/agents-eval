import os
import shutil
import subprocess

from dotenv import load_dotenv


def qodana_opens_project(project_path: str, language: str):
    qodana_projects_path = os.path.join(os.path.dirname(os.path.dirname(project_path)), 'gen_templates_qodana')
    os.makedirs(qodana_projects_path, exist_ok=True)

    qodana_project_path = os.path.join(qodana_projects_path, os.path.basename(project_path))
    if os.path.exists(qodana_project_path):
        shutil.rmtree(qodana_project_path)
    os.makedirs(qodana_project_path)

    for filename in os.listdir(project_path):
        src_file_path = os.path.join(project_path, filename)
        if os.path.isfile(src_file_path):
            shutil.copy(src_file_path, qodana_project_path)
        else:
            dst_file_path = os.path.join(qodana_project_path, filename)
            shutil.copytree(src_file_path, dst_file_path)

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

    if process.returncode == 0:
        return True, logs, None
    else:
        print(f"\nAn error occurred: {process.stderr.decode()}")
        return False, logs, process.stderr.decode()


def get_qodana_metrics(gen_project_path: str, golden_project_path: str, language: str) -> dict[str, Any]:
    qodana_metrics = {}
    for pref, project_path in [('gen', gen_project_path), ('golden', golden_project_path)]:
        status, log, error = qodana_opens_project(project_path, language)
        qodana_metrics[pref + '_qodana_status'] = status
        qodana_metrics[pref + '_qodana_log'] = log
        qodana_metrics[pref + '_qodana_error'] = error

    return qodana_metrics


if __name__ == '__main__':
    load_dotenv()
    metrics = get_qodana_metrics(
        '/Users/Maria.Tigina/PycharmProjects/agents-eval-data/template_generation/planning_gpt-4-1106-preview/java/gen_templates/AdamBien__aws-lambda-cdk-plain',
        '/Users/Maria.Tigina/PycharmProjects/agents-eval-data/repos/AdamBien__aws-lambda-cdk-plain',
        'java'
    )
    print(metrics)
