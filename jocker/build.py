"""
Build the given jail flavour
"""
import os
import tempfile
import shutil

from .parser import parse
from .archive import compress, copy_tree
from .commands import FLAVOURS_DIR, flavour_name


def build(jailfile='Jailfile', build=None, install=False):
    """
    Build the flavour from the given Jailfile.
    """
    commands = parse(jailfile)
    with tempfile.TemporaryDirectory() as tmp:
        for command in commands:
            command.build(tmp, commands)
        if build:
            destpath = os.path.join(build, flavour_name(commands))
            copy_tree(tmp, destpath)
            os.chmod(destpath, 0o755)
        if install:
            destpath = os.path.join(FLAVOURS_DIR, flavour_name(commands))
            copy_tree(tmp, destpath)
            os.chmod(destpath, 0o755)
        return compress(tmp)
