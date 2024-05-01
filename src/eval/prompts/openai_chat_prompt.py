from abc import abstractmethod, ABC

from langchain_core.prompts import ChatPromptTemplate

from src.eval.prompts.base_prompt import BasePrompt


class OpenAIChatPrompt(BasePrompt, ABC):

    @abstractmethod
    async def execution_prompt(self, **kwargs) -> ChatPromptTemplate:
        pass
