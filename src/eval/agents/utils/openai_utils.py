import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import wait_random_exponential, stop_after_attempt, retry

from src.eval.agents.utils.tokenization_utils import TokenizationUtils

DEFAULT_MODEL = "gpt-4-1106-preview"


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
async def chat_completion_request(client: AsyncOpenAI, messages: list[dict[str, str]], temperature=1.0, model: str = DEFAULT_MODEL, **model_kwargs) -> ChatCompletion:
    tokenization_utils = TokenizationUtils(model)
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=tokenization_utils.truncate(messages),
            temperature=temperature,
            **model_kwargs
        )
        return response
    except Exception as e:
        print("Unable to generate chat completion response")
        print(f"Exception: {e}")
        return e


def create_chat(model_name: str, temperature: int, model_kwargs: dict) -> BaseChatModel:
    return ChatOpenAI(model_name=model_name, openai_api_key=os.environ["OPENAI_API_KEY"],
                      temperature=temperature, model_kwargs=model_kwargs)
