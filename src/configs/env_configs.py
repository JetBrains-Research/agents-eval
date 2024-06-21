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


@dataclass
class HttpEnvConfig(EnvConfig):
    _target_: str = f"src.eval.envs.code_engine_env.CodeEngineEnv"
    name: str = MISSING
    port: int = MISSING
    docker_image_name: str = MISSING
    docker_container_name: str = MISSING
