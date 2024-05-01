from dataclasses import dataclass

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

from src.configs.agent_configs import AgentConfig, OpenAiLangchainAgentConfig, TreeOfThoughtsAgentConfig, \
    ADaPTAgentConfig, ReflexionAgentConfig
from src.configs.data_source_configs import DataSourceConfig, HFDataSourceConfig
from src.configs.env_configs import EnvConfig, HttpEnvConfig
from src.configs.prompt_configs import PlanningPromptConfig, SimplePromptConfig, TreeOfThoughtsPromptConfig, \
    ADaPTPromptConfig, ReflexionPromptConfig


@dataclass
class EvalConfig:
    name: str = MISSING
    env: EnvConfig = MISSING
    agent: AgentConfig = MISSING
    data_source: DataSourceConfig = MISSING
    output_path: str = MISSING


cs = ConfigStore.instance()
cs.store(name="eval_config", node=EvalConfig)

# all available options for the env
cs.store(name="http", group="env", node=HttpEnvConfig)

# all available options for the agents
cs.store(name="openai", group="agent", node=OpenAiLangchainAgentConfig)
cs.store(name="thee_of_thoughts", group="agent", node=TreeOfThoughtsAgentConfig)
cs.store(name="adapt", group="agent", node=ADaPTAgentConfig)
cs.store(name="reflexion", group="agent", node=ReflexionAgentConfig)

# all available options for the prompt
cs.store(name="simple", group="agent/prompt", node=SimplePromptConfig)
cs.store(name="planning", group="agent/prompt", node=PlanningPromptConfig)
cs.store(name="thee_of_thoughts", group="agent/prompt", node=TreeOfThoughtsPromptConfig)
cs.store(name="adapt", group="agent/prompt", node=ADaPTPromptConfig)
cs.store(name="reflexion", group="agent/prompt", node=ReflexionPromptConfig)

# all available options for the data source
cs.store(name="hf", group="data_source", node=HFDataSourceConfig)
