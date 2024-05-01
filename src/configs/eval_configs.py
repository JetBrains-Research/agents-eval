from dataclasses import dataclass

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING

from src.configs.agent_configs import AgentConfig
from src.configs.data_source_configs import DataSourceConfig
from src.configs.env_configs import EnvConfig


@dataclass
class EvalConfig:
    env: EnvConfig = MISSING
    agent: AgentConfig = MISSING
    data_source: DataSourceConfig = MISSING


cs = ConfigStore.instance()
cs.store(name="eval_config", node=EvalConfig)
