from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from tenacity import wait_random_exponential, stop_after_attempt, retry

from src.eval.agents.utils.tokenization_utils import TokenizationUtils

DEFAULT_MODEL = "gpt-4-1106-preview"
DEFAULT_PROFILE_NAME = "openai-gpt-4"
DEFAULT_MAX_TOKENS = 128000


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
async def chat_completion_request(client: AsyncOpenAI, messages: list[dict[str, str]], model: str = DEFAULT_MODEL,
                                  max_tokens: int = DEFAULT_MAX_TOKENS, profile_name: str = DEFAULT_PROFILE_NAME,
                                  tools=None, tool_choice=None) -> ChatCompletion:
    tokenization_utils = TokenizationUtils(profile_name)
    tokens_count = tokenization_utils.count_tokens(messages)
    print(f"Tokens: {tokens_count}/{max_tokens}")
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=tokenization_utils.truncate(messages, max_tokens),
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate chat completion response")
        print(f"Exception: {e}")
        return e


def create_chat(model_name: str, temperature: int, model_kwargs: dict) -> BaseChatModel:
    return ChatOpenAI(model_name=model_name, temperature=temperature, model_kwargs=model_kwargs)
