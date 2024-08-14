from src.eval.envs.base_env import BaseEnv
from src.eval.envs.utils.tree_utils import parse_project_structure, parse_files_content, create_tree


class FewShotEnv(BaseEnv):

    def __init__(self):
        self.local_path = None

    async def init(self, init_params: dict) -> str:
        self.local_path = init_params.get('content_root_path')

    async def reset(self) -> str:
        pass

    async def get_tools(self) -> list[dict]:
        pass

    async def get_state(self) -> str:
        pass

    async def shutdown(self):
        pass

    async def run_command(self, command_name: str, command_params: dict) -> dict:
        description = command_params['description']

        project_structure = parse_project_structure(description)
        print(project_structure)

        project_structure = parse_files_content(project_structure, description)
        print(project_structure)

        create_tree(self.local_path, project_structure)

        return project_structure
