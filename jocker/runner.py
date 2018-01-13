"""
Run the a command in a jail
"""
from .parser import parse, Jockerfile
from .backends.utils import get_backend


def run(name, command=None, args=None):
    """
    Run the given command or the default entrypoint in the jail
    """
    commands = Jockerfile(jockerfile)
    command = command or commands.entrypoint()

    jail_backend = get_backend(jailname=name)
    with jail_backend.runner() as runner:
        runner.exec(command, commands.env())
