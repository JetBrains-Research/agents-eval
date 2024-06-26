from src.eval.prompts.base_prompt import BasePrompt


class ADaPTPrompt(BasePrompt):
    def __init__(self,
                 executor_prompt: str,
                 agent_planner_prompt: str,
                 simple_planner_prompt: str):
        self._executor_prompt = executor_prompt
        self._agent_planner_prompt = agent_planner_prompt
        self._simple_planner_prompt = simple_planner_prompt

    def executor_prompt(self) -> str:
        return self._executor_prompt + self._input_prompt()

    def agent_planner_prompt(self) -> str:
        return self._agent_planner_prompt + self._input_prompt()

    def simple_planner_prompt(self) -> str:
        return self._simple_planner_prompt + self._input_prompt()
