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
class VanillaPromptConfig(PromptConfig):
    _target_: str = f"src.eval.prompts.planning_prompt.VanillaPrompt"
    execution_system_prompt: str = MISSING