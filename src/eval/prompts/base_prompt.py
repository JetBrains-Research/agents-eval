from abc import ABC, abstractmethod

from langchain_core.prompts import ChatPromptTemplate


class BasePrompt(ABC):

    @abstractmethod
    async def execution_prompt(self, user_prompt: str) -> ChatPromptTemplate:
        pass
