from dataclasses import dataclass, field
from typing import Dict, Any

from omegaconf import MISSING

from src.configs.prompt_configs import PromptConfig


@dataclass
class AgentConfig:
    _target_: str = MISSING


@dataclass
class OpenAiLangchainAgentConfig(AgentConfig):
    _target_: str = f"src.eval.agents.openai_langchain_agent.OpenAiLangchainAgent"
    prompt: PromptConfig = MISSING
    model_name: str = MISSING
    temperature: int = MISSING
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {})
