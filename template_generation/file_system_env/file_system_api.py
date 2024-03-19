import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict


class FileSystemAPI:

    def __init__(self, content_root_path: str):
        self.content_root_path = content_root_path

    def to_absolute_path(self, path: str) -> str:
        return os.path.join(self.content_root_path, path)

    def to_relative_path(self, path: str) -> str:
        return path.replace(self.content_root_path + '/', '')

    def create_directory(self, path: str):
        os.makedirs(self.to_absolute_path(path), exist_ok=True)

    def delete_directory(self, path: str):
        shutil.rmtree(self.to_absolute_path(path))

    def create_file(self, path: str, text: str):
        self.create_directory(os.path.dirname(self.to_absolute_path(path)))
        with open(self.to_absolute_path(path), 'w') as file:
            file.write(text)

    def delete_file(self, path: str):
        os.remove(self.to_absolute_path(path))

    def read_file(self, path: str) -> Optional[str]:
        with open(self.to_absolute_path(path), 'r') as file:
            return file.read()

    def write_file(self, path: str, text: str):
        with open(self.to_absolute_path(path), 'w') as file:
            file.write(text)

    def list_directory(self, path: str) -> Optional[List[str]]:
        return [os.path.join(path, f) for f in os.listdir(self.to_absolute_path(path))]

    def get_file_tree(self) -> Dict[str, str]:
        file_tree = {}
        for root, dirs, files in os.walk(self.content_root_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r') as f:
                        print(file_path)
                        content = f.read()
                    file_tree[str(file_path)] = content
                except Exception as e:
                    print(f"Can not read file {file_path}", e)

        return file_tree
