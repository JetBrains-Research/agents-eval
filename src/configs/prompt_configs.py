from dataclasses import dataclass, field
from typing import Dict, Any

from omegaconf import MISSING


@dataclass
class PromptConfig:
    _target_: str = MISSING


@dataclass
class PlanningPromptConfig(PromptConfig):
    _target_: str = f"src.eval.prompts.planning_prompt.PlanningPrompt"
    model_name: str = MISSING
    temperature: int = MISSING
    model_kwargs: Dict[str, Any] = field(default_factory=lambda: {})
    planning_system_prompt: str = MISSING
    execution_system_prompt: str = MISSING


@dataclass
class TreeOfThoughtsPromptConfig(PromptConfig):
    _target_: str = f"src.eval.prompts.tree_of_thoughts_prompt.PlanningPrompt"
    thought_evaluator_message: str = MISSING
    thought_generator_message: str = MISSING


@dataclass
class SimplePromptConfig(PromptConfig):
    _target_: str = f"src.eval.prompts.simple_prompt.SimplePrompt"
    execution_system_prompt: str = MISSING
