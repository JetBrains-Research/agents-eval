from contextlib import contextmanager

from src.docker.docker_session import DockerInterface
from src.docker.docker_session_config import DockerSessionConfig
from src.eval.agents.agent import Agent


class DockerizedAgent(Agent):

    _docker_session: DockerInterface = None
    _docker_session_config: DockerSessionConfig = None

    def __init__(self, docker_session_config: DockerSessionConfig):
        self.docker_session_config = docker_session_config

    @contextmanager
    def docker_session(self) -> DockerInterface:
        docker_interface = DockerInterface()

        try:
            docker_interface.initialize(self.docker_session_config)
            yield docker_interface
        finally:
            docker_interface.destroy(silent=True)

    def run(self, function_name: str, function_params: dict) -> str:
        pass

    def get_tools(self) -> list[str]:
        pass
