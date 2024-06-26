from src.eval.prompts.base_prompt import BasePrompt


class ReflexionPrompt(BasePrompt):

    def __init__(self, action_prompt: str,
                 evaluator_prompt: str,
                 self_reflexion_prompt: str):
        self._action_prompt = action_prompt
        self._evaluator_prompt = evaluator_prompt
        self._self_reflexion_prompt = self_reflexion_prompt

    def action_prompt(self) -> str:
        return self._action_prompt + self._input_prompt()

    def evaluator_prompt(self) -> str:
        return self._evaluator_prompt + self._input_prompt()

    def self_reflexion_prompt(self) -> str:
        return self._self_reflexion_prompt + self._input_prompt()
