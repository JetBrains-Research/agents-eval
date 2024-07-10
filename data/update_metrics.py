import os
import shutil
from pathlib import Path

if __name__ == '__main__':
    local_data_path = "./../../agents-eval-data/metrics"
    repo_data_path = Path(__file__).resolve().parent / 'metrics'

    for agent in os.listdir(local_data_path):
        for language in os.listdir(os.path.join(local_data_path, agent)):
            for metrics_csv in os.listdir(os.path.join(local_data_path, agent, language)):
                file_path = os.path.join(agent, language, metrics_csv)
                if os.path.isfile(os.path.join(local_data_path, file_path)):
                    os.makedirs(os.path.join(repo_data_path, agent, language), exist_ok=True)
                    shutil.copyfile(os.path.join(local_data_path, file_path), os.path.join(repo_data_path, file_path))
