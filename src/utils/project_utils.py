import subprocess


def get_project_file_tree(project_path) -> str:
    result = subprocess.run(["tree", project_path],
                            capture_output=True,
                            text=True)
    project_file_tree = result.stdout

    return project_file_tree
