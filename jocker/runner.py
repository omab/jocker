"""
Run the a command in a jail
"""
from .parser import parse, Jockerfile, build_command
from .backends.utils import get_backend


def run(name, command=None, args=None):
    """
    Run the given command or the default jexec calls in the jail
    """
    jail_backend = get_backend(jailname=name)
    jockerfile = Jockerfile(jail_backend.jail_jockerfile())

    if command and args:
        command = '{command} {args}'.format(command=command,
                                            args=' '.join(args))
    jail_backend.run(jockerfile, command)
