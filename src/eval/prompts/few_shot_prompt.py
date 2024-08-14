from src.eval.prompts.base_prompt import BasePrompt


class FewShotPrompt(BasePrompt):

    def __init__(self, execution_system_prompt_path: str):
        self._execution_system_prompt = self._read_prompt(execution_system_prompt_path)

    async def execution_prompt(self, **kwargs) -> str:
        return self._execution_system_prompt
