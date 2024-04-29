from dataclasses import dataclass, field
from typing import Dict, Any

from omegaconf import MISSING

from src.configs.prompt_configs import PromptConfig, TreeOfThoughtsPromptConfig


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


@dataclass
class TreeOfThoughtsAgentConfig(AgentConfig):
    _target_: str = f"src.eval.agents.tree_of_thoughts_agent.TreeOfThoughtsAgent"
    prompt: TreeOfThoughtsPromptConfig = MISSING
    model_name: str = MISSING
    temperature: int = MISSING
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {})
    value_threshold: float = MISSING
    max_num_thoughts: int = MISSING
    max_num_steps: int = MISSING
