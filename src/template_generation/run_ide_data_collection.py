import json
import os
import shutil
import zipfile

import hydra
from datasets import Dataset
from dotenv import load_dotenv
from huggingface_hub.hf_api import api
from omegaconf import DictConfig

from src.utils.hf_utils import FEATURES


def upload_to_hf(config):
    df = Dataset.from_csv(
        os.path.join(config.data_path, f'ide_template_repos.csv'),
        features=FEATURES['ide_template_generation_data'],
    )
    df.push_to_hub('JetBrains-Research/template-generation-ide', split='train')


def zip_project(project_name: str, projects_path: str, archives_path: str):
    project_path = os.path.join(projects_path, project_name)
    archive_path = os.path.join(archives_path, f"{project_name}.zip")
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            try:
                for file in files:
                    if file in ['.venv', '.idea']:
                        continue
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, project_path))
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    zipf.write(dir_path, os.path.relpath(dir_path, project_path))
            except Exception as e:
                print(e)


def upload_projects(config: DictConfig):
    df = Dataset.from_csv(
        os.path.join(config.data_path, f'ide_template_repos.csv'),
        features=FEATURES['ide_template_generation_data'],
    )
    repos_paths = []
    os.makedirs(config.archives_path, exist_ok=True)
    for pd in df:
        dir_name = pd['name'] + 'Project'
        zip_project(dir_name, config.projects_path, config.archives_path)
        repos_paths.append(f'./projects/{dir_name}.zip')

    api.upload_folder(
        folder_path=config.archives_path,
        repo_id='JetBrains-Research/template-generation-ide',
        path_in_repo=f'./projects',
        repo_type="dataset"
    )

    shutil.rmtree(config.archives_path, ignore_errors=True)
    os.makedirs(config.archives_path, exist_ok=True)
    path_json_path = os.path.join(config.archives_path, 'projects.json')
    with open(path_json_path, 'w') as f:
        json.dump({'projects': repos_paths}, f)

    api.upload_file(
        path_or_fileobj=path_json_path,
        repo_id='JetBrains-Research/template-generation-ide',
        repo_type="dataset",
        path_in_repo="projects.json"
    )


@hydra.main(config_path="../../configs/template_generation", config_name="data", version_base=None)
def main(config: DictConfig):
    load_dotenv()
    upload_projects(config)


if __name__ == "__main__":
    main()
