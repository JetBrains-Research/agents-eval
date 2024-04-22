from dataclasses import dataclass

from omegaconf import MISSING


@dataclass
class EnvConfig:
    _target_: str = MISSING


@dataclass
class HttpEnvConfig(EnvConfig):
    _target_: str = f"src.eval.envs.http_env.HttpEnv"
    name: str = MISSING
    port: int = MISSING
