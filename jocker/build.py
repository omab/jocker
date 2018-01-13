"""
Build the given Jail base
"""
import os
import tempfile
import shutil

from .parser import parse, build_command
from .archive import compress, copy_tree
from .commands import base_name
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

    with tempfile.TemporaryDirectory() as tmp:
        for command in commands:
            command.build(jail_backend, tmp, commands)
        if build:
            destpath = os.path.join(build, base_name(commands))
            copy_tree(tmp, destpath)
            os.chmod(destpath, 0o755)
        if install:
            destpath = os.path.join(jail_backend.BASE_DIR, base_name(commands))
            copy_tree(tmp, destpath)
            os.chmod(destpath, 0o755)
        return compress(tmp)
