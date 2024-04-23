from abc import ABC, abstractmethod

from langchain_core.prompts import ChatPromptTemplate


class BasePrompt(ABC):

    @abstractmethod
    async def chat(self, user_prompt: str, **kwargs) -> ChatPromptTemplate:
        pass
