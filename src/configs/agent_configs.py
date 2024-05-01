from dataclasses import dataclass, field
from typing import Dict, Any

from omegaconf import MISSING

from src.configs.prompt_configs import PromptConfig, TreeOfThoughtsPromptConfig, ADaPTPromptConfig, \
    ReflexionPromptConfig


@dataclass
class AgentConfig:
    _target_: str = MISSING


@dataclass
class OpenAiLangchainAgentConfig(AgentConfig):
    _target_: str = f"src.eval.agents.openai_langchain_agent.OpenAILangchainAgent"
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


@dataclass
class ADaPTAgentConfig(AgentConfig):
    _target_: str = f"src.eval.agents.adapt_agent.ADaPTAgent"
    prompt: ADaPTPromptConfig = MISSING
    model_name: str = MISSING
    temperature: int = MISSING
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {})
    max_depth: int = MISSING
    executor_max_iterations: int = MISSING
    max_num_thoughts: int = MISSING


@dataclass
class ReflexionAgentConfig(AgentConfig):
    _target_: str = f"src.eval.agents.reflexion_agent.ReflexionAgent"
    prompt: ReflexionPromptConfig = MISSING
    model_name: str = MISSING
    temperature: int = MISSING
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {})
    value_threshold: float = MISSING
    max_num_iterations: int = MISSING
