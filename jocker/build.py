"""
Build the given Jail base
"""
from .parser import parse, build_command
from .archive import compress
from .backends.utils import get_backend


def build(jockerfile='Jockerfile', build=None, install=False):
    """
    Build the base from the given Jockerfile.
    """
    jail_backend = get_backend()

    commands = [
        # ensure the Jockerfile is copied into the new jail
        build_command('ADD {path} /etc/'.format(path=jockerfile))
    ] + parse(jockerfile)

    path = jail_backend.build(commands, build, install)

    return compress(path)
