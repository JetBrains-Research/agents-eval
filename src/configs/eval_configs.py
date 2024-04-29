from dataclasses import dataclass

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

from src.configs.agent_configs import AgentConfig, OpenAiLangchainAgentConfig, TreeOfThoughtsAgentConfig
from src.configs.data_configs import DataSourceConfig, HFDataSourceConfig
from src.configs.env_configs import EnvConfig, HttpEnvConfig
from src.configs.prompt_configs import PlanningPromptConfig, SimplePromptConfig, TreeOfThoughtsPromptConfig


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
cs.store(name="thee_of_thoughts", group="agent", node=TreeOfThoughtsAgentConfig)

# all available options for the prompt
cs.store(name="planning", group="agent/prompt", node=PlanningPromptConfig)
cs.store(name="simple", group="agent/prompt", node=SimplePromptConfig)
cs.store(name="thee_of_thoughts", group="agent/prompt", node=TreeOfThoughtsPromptConfig)

# all available options for the input
cs.store(name="hf", group="data_src", node=HFDataSourceConfig)
