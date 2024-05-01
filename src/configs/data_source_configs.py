from dataclasses import dataclass
from typing import Optional, List

from omegaconf import MISSING


@dataclass
class DataSourceConfig:
    _target_: str = MISSING


@dataclass
class HFDataSourceConfig(DataSourceConfig):
    _target_: str = f"src.eval.data_sources.hf_data_source.HFDataSource"
    cache_dir: Optional[str] = None
    hub_name: str = MISSING
    configs: List[str] = MISSING
    split: str = "test"
