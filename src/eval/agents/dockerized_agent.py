from abc import abstractmethod, ABC
from contextlib import contextmanager
from typing import Union

from src.docker.docker_session import DockerInterface, docker_session
from src.eval.agents.agent import Agent


class DockerizedAgent(Agent):
    _docker_session: DockerInterface = None

    def __init__(self, image: str = None, command: Union[str, list[str]] = None,
                 working_dir: str = None, ports: dict[int, int] = None,
                 volumes: Union[dict[Union[str, str], dict], list[str]] = None,
                 interactive: bool = False, interactive_interpreter: str = None):
        self.image: str = image
        self.command: Union[str, list[str]] = command
        self.working_dir: str = working_dir
        self.ports: dict[int, int] = ports
        self.volumes: Union[dict[Union[str, str], dict], list[str]] = volumes
        self.interactive: bool = interactive
        self.interactive_interpreter: str = interactive_interpreter

    @contextmanager
    def docker_session(self):
        return docker_session(
            image=self.image,
            command=self.command,
            ports=self.ports,
            working_dir=self.working_dir,
            volumes=self.volumes,
            interactive=self.interactive,
            interactive_interpreter=self.interactive_interpreter,
        )
