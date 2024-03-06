from contextlib import contextmanager

from src.docker.docker_interface import DockerInterface
from src.docker.docker_session_config import DockerSessionConfig


@contextmanager
def docker_session(docker_session_config: DockerSessionConfig) -> DockerInterface:
    docker_interface = DockerInterface()

    try:
        docker_interface.initialize(docker_session_config)
        yield docker_interface
    finally:
        docker_interface.destroy(silent=True)
