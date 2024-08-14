import os
from abc import ABC
from textwrap import dedent

from src import PROJECT_DIR


class BasePrompt(ABC):

    @staticmethod
    def _input_prompt() -> str:
        return dedent("""
            Inputs:
            {input}
        """)

    @staticmethod
    def _read_prompt(path) -> str:
        with open(os.path.join(PROJECT_DIR, path), "r") as f:
            return f.read()
