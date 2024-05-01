from src.eval.prompts.base_prompt import BasePrompt


class TreeOfThoughtsPrompt(BasePrompt):

    def __init__(self, thought_evaluator_prompt: str, thought_generator_prompt: str):
        self._thought_evaluator_prompt = thought_evaluator_prompt
        self._thought_generator_prompt = thought_generator_prompt

    def thought_evaluator_prompt(self) -> str:
        return self._thought_evaluator_prompt + self._input_prompt()

    def thought_generator_prompt(self) -> str:
        return self._thought_generator_prompt + self._input_prompt()
