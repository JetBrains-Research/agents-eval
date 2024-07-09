import os

from src.eval.prompts import PROJECT_DIR
from src.eval.prompts.base_prompt import BasePrompt


class FewShotPrompt(BasePrompt):

    def __init__(self, execution_system_prompt_path: str):
        with open(os.path.join(PROJECT_DIR, execution_system_prompt_path), "r") as f:
            self._execution_system_prompt = f.read()

    async def execution_prompt(self, **kwargs) -> str:
        return self._execution_system_prompt
