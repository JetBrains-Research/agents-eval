import anthropic
import tiktoken
from transformers import AutoTokenizer


class TokenizationUtils:
    """A wrapper for two tokenization-related operations:
    - estimating the number of tokens for a prompt
    - truncating a prompt to first X tokens.
    """

    PROFILE_NAME_TO_PROVIDER_AND_MODEL = {
        "grazie-gpt-neo-tiny-text": {"model_provider": "huggingface", "model_name": "EleutherAI/gpt-neo-125m"},
        "grazie-replit-code-v1-small": {"model_provider": "huggingface", "model_name": "replit/replit-code-v1-3b"},
        "grazie-pythia-large-text": {"model_provider": "huggingface", "model_name": "EleutherAI/pythia-12b"},
        "grazie-bigcode-starcoder": {"model_provider": "huggingface", "model_name": "bigcode/starcoder"},
        "grazie-chat-llama-v2-7b": {"model_provider": "huggingface", "model_name": "meta-llama/Llama-2-7b-chat"},
        "grazie-chat-llama-v2-13b": {"model_provider": "huggingface", "model_name": "meta-llama/Llama-2-13b-chat"},
        "anthropic-claude": {"model_provider": "anthropic", "model_name": "claude"},
        "anthropic-claude-instant": {"model_provider": "anthropic", "model_name": "claude-instant"},
        "openai-chat-gpt": {"model_provider": "openai", "model_name": "gpt-3.5-turbo"},
        "openai-chat-gpt-16k": {"model_provider": "openai", "model_name": "gpt-3.5-turbo"},
        "openai-gpt-4": {"model_provider": "openai", "model_name": "gpt-4"},
    }

    def __init__(self, profile_name: str):
        model_info = self.PROFILE_NAME_TO_PROVIDER_AND_MODEL.get(profile_name, None)
        if not model_info:
            raise ValueError(f"Unknown profile {profile_name}.")

        self._model_provider = model_info["model_provider"]
        self._model_name = model_info["model_name"]

        if self._model_provider == "openai":
            self._tokenizer = tiktoken.encoding_for_model(self._model_name)
        elif self._model_provider == "anthropic":
            self._tokenizer = anthropic.Anthropic().get_tokenizer()
        elif self._model_provider == "huggingface":
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)

    def _count_tokens(self, text: str) -> int:
        """Estimates the number of tokens for a given string."""
        if self._model_provider == "openai":
            return len(self._tokenizer.encode(text))

        if self._model_provider == "anthropic":
            return len(self._tokenizer.encode(text))

        if self._model_provider == "huggingface":
            return len(self._tokenizer(text).input_ids)

        raise ValueError(f"{self._model_provider} is currently not supported for token estimation.")

    def count_tokens(self, messages: list[dict[str, str]]) -> int:
        """Estimates the number of tokens for a given list of messages.

        Note: Currently, for some agents (e.g., OpenAI) the returned number might be slightly lower than the actual number of tokens, because the
        special tokens are not considered.
        """
        return sum([self._count_tokens(value) for message in messages for key, value in message.items()])

    def _truncate(self, text: str, max_num_tokens: int) -> str:
        """Truncates a given string to first `max_num_tokens` tokens.

        1. Encodes string to a list of tokens via corresponding tokenizer.
        2. Truncates the list of tokens to first `max_num_tokens` tokens.
        3. Decodes list of tokens back to a string.
        """
        if self._model_provider == "openai":
            encoding = self._tokenizer.encode(text)[:max_num_tokens]
            return self._tokenizer.decode(encoding)
        if self._model_provider == "anthropic":
            encoding = self._tokenizer.encode(text)[:max_num_tokens]
            return self._tokenizer.decode(encoding)
        if self._model_provider == "huggingface":
            encoding = self._tokenizer(text).input_ids[:max_num_tokens]
            return self._tokenizer.decode(encoding)

        raise ValueError(f"{self._model_provider} is currently not supported for prompt truncation.")

    def truncate(self, messages: list[dict[str, str]], max_num_tokens: int) -> list[dict[str, str]]:
        """Truncates a given list of messages to first `max_num_tokens` tokens.

        Note: A current version only truncates a last message, which might not be suitable for all use-cases.
        """
        num_tokens_except_last = self.count_tokens(messages[:-1])
        messages[-1]["content"] = self._truncate(
            messages[-1]["content"], max_num_tokens=max_num_tokens - num_tokens_except_last
        )
        return messages
