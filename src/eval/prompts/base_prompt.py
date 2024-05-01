from abc import ABC
from textwrap import dedent


class BasePrompt(ABC):

    @staticmethod
    def _input_prompt() -> str:
        return dedent("""
            Inputs:
            {input}
        """)
