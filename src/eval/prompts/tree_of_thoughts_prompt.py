from textwrap import dedent

from langchain_core.prompts import ChatPromptTemplate

from src.eval.prompts.base_prompt import BasePrompt


class TreeOfThoughtsPrompt(BasePrompt):

    def __init__(self, thought_evaluator_message: str, thought_generator_message: str):
        self._thought_evaluator_message = thought_evaluator_message
        self._thought_generator_message = thought_generator_message

    async def execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        raise NotImplementedError("This strategy does not require execution prompt")

    @staticmethod
    def _input_prompt() -> str:
        return dedent("""
            Inputs:
            {input}
        """)

    def thought_evaluator_message(self) -> str:
        return self._thought_evaluator_message + self._input_prompt()

    def thought_generator_message(self) -> str:
        return self._thought_generator_message + self._input_prompt()
