import random
import re
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from typing import List

import docker
from docker import DockerClient
from docker.models.containers import Container

from src.utils.docker.docker_session_config import DockerSessionConfig


@dataclass
class ShelOutput:
    """Represents the output of a shell command execution.

    :param output: The output of the shell command.
    :type output: str
    :param exit_code: The exit code of the shell command.
    :type exit_code: int
    """
    output: str
    exit_code: int

    # make class behave like a string
    def __getattr__(self, attr):
        return getattr(self.output, attr)

    def __str__(self):
        return self.output


class DockerInterface:
    """ Docker interface to execute commands in a container"""
    _node_regex: re.Pattern = re.compile(r'@.*:')

    container: Container = None
    container_create_configuration: DockerSessionConfig = None

    _interactive_session_name: str = None

    def __init__(self, docker_client: DockerClient = None):
        """ Docker interface to execute commands in a container

        :param docker_client: An optional Docker client instance to use. If not provided, a new client will be
        created using the default configuration.
        """
        self.container = None
        self.container_create_configuration = None
        self._interactive_session_name = None

        self.docker_client = docker_client or docker.from_env()

    def initialize(self, config: DockerSessionConfig, destroy_if_exists: bool = False):
        """
        Initializes the container for the DockerManager.
        :param config: Configuration for the docker session
        :param destroy_if_exists: Whether to destroy the existing container if one is already initialized. Defaults
        to False if not provided.
        :return: None
        """

        if self.container is not None and destroy_if_exists:
            self.destroy()
        elif self.container is not None:
            raise Exception('Container is already initialized')

        self.container_create_configuration = config

        # Copy config in order not to change
        create_configuration = self.container_create_configuration.copy()

        copy_volumes = None
        volumes = None
        if create_configuration.volumes:
            # Filter out volumes with mode 'cp'
            # (additional mode that copies the contents of the volume to the container)
            copy_volumes = {k: v for k, v in config.volumes.items() if v.get('mode', 'rw') == 'cp'}
            volumes = {k: v for k, v in config.volumes.items() if v.get('mode', 'rw') != 'cp'}

            # Mount every copy volume to a temporary directory
            for source_path, volume_config in copy_volumes.items():
                temp_dir = Path('/tmp') / str(volume_config['bind']).replace('/', '_')
                new_volume_config = {'bind': str(temp_dir), 'mode': 'ro'}
                volumes[source_path] = new_volume_config

        create_configuration.volumes = volumes

        try:
            # Start a new container with open stdin and tty
            self.container = self.docker_client.containers.run(stdin_open=True, tty=True, detach=True,
                                                               **create_configuration.to_docker_configuration())

            # Copy contents of copy volumes to the actual target directories
            if copy_volumes and len(copy_volumes) > 0:
                self._ensure_installed('rsync')
                for source_path, volume_config in copy_volumes.items():
                    temp_dir = Path('/tmp') / str(volume_config['bind']).replace('/', '_')
                    self.container.exec_run(['ls', '-la', str(temp_dir)])
                    self.container.exec_run(['mkdir', '-p', str(volume_config['bind'])])
                    self.container.exec_run(['rsync', '-a', str(temp_dir) + '/', str(volume_config['bind'])])

            if create_configuration.interactive or self._interactive_session_name is not None:
                self._interactive_session_name = self._ensure_tmux_session(
                    name=f'interactive_session_{random.randint(10000, 99999)}',
                    interpreter=create_configuration.interactive_interpreter)
        except Exception as e:
            # Rethrow exception
            raise e

    def recreate(self):
        """
        Reinitializes and recreates the container.

        :return: None
        :raises Exception: If the container is not initialized or if there are any errors during reinitialization.
        """
        if self.container_create_configuration is None:
            raise Exception('Container is not initialized')

        try:
            self.destroy()
        except Exception:
            pass

        try:
            self.initialize(self.container_create_configuration)
        except Exception:
            # rethrow exception
            raise

    def destroy(self, silent: bool = False):
        """
        Destroy the container.

        :param silent: Flag indicating whether to suppress exception if container is not initialized. Defaults to False.
        :return: None
        """
        if self.container is None and not silent:
            raise Exception('Container is not initialized')
        elif self.container is None:
            return

        try:
            self.container.remove(force=True)
            self.container = None
        except Exception:
            if not silent:
                raise

    def execute_command(self, command: str, force_noninteractive: bool = False):
        """
        Execute a command inside the container.

        :param command: The command to execute inside the container.
        :param force_noninteractive: Flag indicating whether to force non-interactive mode for command execution.
        :return: The output of the executed command.

        :raises Exception: If the container is not initialized or not running.

        """
        # check if container is initialized
        if self.container is None:
            raise Exception('Container is not initialized')
        if self.container.status != 'running' and self.container.status != 'created':
            raise Exception('Container is not running')

        return (self._execute_interactive_command(
            command) if self._interactive_session_name is not None and not force_noninteractive else
                self._execute_noninteractive_command(
                    command))

    def execute_batch(self, commands: List[str]):
        """
        Executes a batch of commands.

        :param commands: A list of strings representing the commands to be executed.
        :type commands: list[str]
        :return: An iterator that yields the results of executing each command.
        :rtype: generator
        """
        for command in commands:
            yield self.execute_command(command)

    def _execute_noninteractive_command(self, command: str):
        """
        Execute a non-interactive command inside a container.

        :param command: The command to be executed.
        :type command: str
        :return: The stdout output and the exit code of the command.
        :rtype: ShelOutput
        :raises Exception: If the command execution fails.
        """
        try:
            exit_code, output = self.container.exec_run(command)
            return ShelOutput(output.decode('utf-8').strip(), exit_code)
        except Exception as e:
            raise Exception(f'Failed to execute command "{command}". {e}')

    def _execute_interactive_command(self, command):
        """
        Execute an interactive command inside the container's interactive session.

        :param command: The command to execute.
        :return: The command's output and exit code.
        """
        # TODO: wonder if there is a better way
        if isinstance(command, list):
            command = ' '.join(command)

        try:
            self.container.exec_run(
                ['tmux', 'send-keys', '-t', f'{self._interactive_session_name}', f"{command} ; echo '##DONE##'", 'C-m'])

            # get output
            for _ in range(60):
                command_output = self.container.exec_run(
                    ['tmux', 'capture-pane', '-p', '-t', f'{self._interactive_session_name}'])

                output = command_output.output.decode('utf-8').strip()
                if '\n##DONE##\n' in output:
                    break
                else:
                    sleep(1.0)

            # scrab node name and the last welcome message
            # output = self._node_regex.sub(':', output)
            # output = '\n'.join(output.split('\n')[:-1])

            # clear screen
            self.container.exec_run(['tmux', 'send-keys', '-t', f'{self._interactive_session_name}', 'clear', 'C-m'])

            return ShelOutput(output, command_output.exit_code)
        except Exception as e:
            raise Exception(f'Failed to execute command "{command}". {e}')

    def _ensure_tmux_session(self, name=None, interpreter=None):
        """
        This method ensures that a tmux session with the specified name exists. If the session does not exist,
        it starts a new session using the specified interpreter. If the session still does
        * not exist after starting, an exception is raised.

        :param name: The name of the tmux session to ensure. Default is 'agent_session'.
        :param interpreter: The interpreter to use when starting a new tmux session. Default is 'sh'.
        :return: The name of the tmux session that was ensured.
        """
        self._ensure_installed("tmux")

        name = name or 'agent_session'
        interpreter = interpreter or 'sh'

        command_result = self.container.exec_run(['tmux', 'has-session', '-t', name])

        # check if tmux session exists
        if command_result.exit_code != 0:
            # start new tmux session
            command_result = self.container.exec_run(['tmux', 'new-session', '-d', '-s', name, interpreter])
            if command_result.exit_code != 0:
                raise Exception(f'Failed to start tmux session {name}. {command_result.output.decode("utf-8")}')

            command_result = self.container.exec_run(['tmux', 'has-session', '-t', name])
            if command_result.exit_code != 0:
                raise Exception(f'Failed to start tmux session {name}. {command_result.output.decode("utf-8")}')

        return name

    def _ensure_installed(self, app_name: str, package_name: str = None):
        """
        Ensures that an app is installed by checking if it is already installed and installing it if necessary.

        :param app_name: The name of the app to be installed.
        :param package_name: The name of the package to be installed. If not provided, the app_name will be used as
        the package_name.
        :return: None

        Raises:
            Exception: If no known package manager is found.
            Exception: If the installation fails.
        """
        # check if app is installed
        if not self._has_app(app_name):
            # install package
            package_name = package_name or app_name
            try:
                if self._has_app('apt'):
                    installation_result = self.container.exec_run(
                        ['sh', '-c', f'apt update -y && apt install -y {package_name}'])
                elif self._has_app('yum'):
                    installation_result = self.container.exec_run(
                        ['sh', '-c', f'yum update -y && yum install -y {package_name}'])
                elif self._has_app('dnf'):
                    installation_result = self.container.exec_run(
                        ['sh', '-c', f'dnf update -y && dnf install -y {package_name}'])
                else:
                    raise Exception('No known package manager found')

                if installation_result.exit_code != 0:
                    raise Exception(f'Installation failed with: {installation_result.output.decode("utf-8")}')
            except Exception as e:
                raise Exception(f'Failed to install {package_name}. {e}')

    def _has_app(self, app_name: str):
        """
        :param app_name: The name of the application to check if it exists.
        :return: Returns True if the application exists, False otherwise.

        """
        try:
            command_result = self.container.exec_run(['which', f'{app_name}'])
            return command_result.exit_code == 0
        except Exception as e:
            return False
