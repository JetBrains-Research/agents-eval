from dataclasses import dataclass

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

from src.configs.agent_configs import AgentConfig, OpenAiLangchainAgentConfig
from src.configs.data_configs import DataSourceConfig, HFDataSourceConfig
from src.configs.env_configs import EnvConfig, HttpEnvConfig
from src.configs.prompt_configs import PlanningPromptConfig, VanillaPromptConfig


@dataclass
class EvalConfig:
    name: str = MISSING
    env: EnvConfig = MISSING
    agent: AgentConfig = MISSING
    data_src: DataSourceConfig = MISSING
    output_path: str = MISSING


cs = ConfigStore.instance()
cs.store(name="eval_config", node=EvalConfig)
# all available options for the env
cs.store(name="http", group="env", node=HttpEnvConfig)
# all available options for the backbone
cs.store(name="openai", group="agent", node=OpenAiLangchainAgentConfig)
# all available options for the prompt
cs.store(name="planning", group="agent/prompt", node=PlanningPromptConfig)
cs.store(name="vanilla", group="agent/prompt", node=VanillaPromptConfig)
# all available options for the input
cs.store(name="hf", group="data_src", node=HFDataSourceConfig)
