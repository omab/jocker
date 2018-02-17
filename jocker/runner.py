"""
Run the a command in a jail
"""
from .backends.utils import get_backend


def run(name, command=None, args=None):
    """
    Run the given command or the default ENTRYPOINT call in the jail
    """
    jail_backend = get_backend(jailname=name)

    if command and args:
        command = '{command} {args}'.format(command=command,
                                            args=' '.join(args))
    jail_backend.run(command)
