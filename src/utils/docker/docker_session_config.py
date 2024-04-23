import dataclasses
from typing import Union


@dataclasses.dataclass
class DockerSessionConfig:
    """
    :param image: The name or ID of the Docker image to use. Defaults to 'ubuntu' if not provided.
    :param command: The command to execute inside the container. Defaults to '/bin/sh' if not provided.
    :param working_dir: The working directory inside the container. Defaults to '/' if not provided.
    :param ports: A dictionary of ports to expose inside the container. The key is the port inside the container
    and the value is the port on the host machine.
    :param volumes: Either a dictionary of volume configurations or a list of volume names. Defaults to None if
    not provided.
    :param environment: A dictionary of environment variables to set in the container. Defaults to None if not
    provided.
    :param user: The user to run the container as. Defaults to 'root' if not provided.
    :param interactive: Whether to start an interactive session inside the container. Defaults to False if not
    provided.
    :param interactive_interpreter: The interpreter to use in the interactive session. Defaults to None if not
    provided.
    """
    image: str = 'ubuntu'
    working_dir: str = '/'
    command: Union[str, list[str]] = '/bin/sh'
    ports: dict[int, int] = None
    volumes: dict[str, dict[str, str]] = None
    environment: dict[str, str] = None
    user: str = 'root'
    interactive: bool = False
    interactive_interpreter: str = None

    def to_docker_configuration(self) -> dict:
        return {
            'image': self.image,
            'working_dir': self.working_dir,
            'command': self.command,
            'ports': None if not self.ports else self.ports.copy(),
            'volumes': None if not self.volumes else self.volumes.copy(),
            'environment': None if not self.environment else self.environment.copy(),
            'user': self.user,
        }

    def copy(self) -> 'DockerSessionConfig':
        return DockerSessionConfig(
            image=self.image,
            working_dir=self.working_dir,
            command=self.command,
            ports=self.ports,
            volumes=self.volumes,
            environment=self.environment,
            user=self.user,
            interactive=self.interactive,
            interactive_interpreter=self.interactive_interpreter,
        )
