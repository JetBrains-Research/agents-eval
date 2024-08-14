import os
import re


def parse_files_content(project_structure: dict, gpt_description: str):
    files_content_pattern = r'```\s+CONTENT_GENERATION\s+```(.*?)```\s+VALIDATION\s+```'

    files_content_str = re.findall(files_content_pattern, gpt_description, re.DOTALL)
    if len(files_content_str) == 0:
        print("Can not parse CONTENT_GENERATION section")
        return project_structure

    for file_content_str in files_content_str[0].split('```'):
        if file_content_str.strip() == "":
            continue
        file_name, file_content = file_content_str.split('\n', 1)
        current_level = project_structure
        file_name_tokens = file_name.lstrip('/').split('/')
        for i, file_name_token in enumerate(file_name_tokens):
            if file_name_token.strip() == "":
                continue
            if file_name_token not in current_level:
                print(f"No {file_name_token} in {current_level.keys()}. Adding...")
                current_level[file_name_token] = {}
                continue
            if i == len(file_name_tokens) - 1:
                current_level[file_name_token] = file_content
                break
            current_level = current_level[file_name_token]

    return project_structure


def create_tree(base_path, project_structure: dict):
    for name, children in project_structure.items():
        path = os.path.join(base_path, name)
        if isinstance(children, dict):
            os.makedirs(path, exist_ok=True)
            create_tree(path, children)
        else:
            with open(path, 'w') as f:
                f.write(children)


def parse_tree_structure(tree_structure_str: str) -> dict:
    tree_structure = {}
    path_stack = []
    for line in tree_structure_str.splitlines():
        if not line.strip():
            continue
        depth = (len(line) - len(line.lstrip('│ '))) // 4 + 1
        name = line.strip().lstrip('│├└─/ ').strip()
        while len(path_stack) > depth:
            path_stack.pop()
        current_level = tree_structure
        for part in path_stack:
            current_level = current_level[part]
        current_level[name] = {}
        path_stack.append(name)

    return tree_structure


def parse_project_structure(gpt_description: str):
    project_structure_pattern = r'```PROJECT\s+([^`]*)```'

    project_structure_str = re.findall(project_structure_pattern, gpt_description, re.DOTALL)
    if len(project_structure_str) == 0:
        print("Can not parse PROJECT section")
        return {}

    project_structure_str = project_structure_str[0].strip()

    return parse_tree_structure(project_structure_str)
