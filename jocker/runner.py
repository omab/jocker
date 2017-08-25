"""
Run the a command in a jail
"""
import os
import tempfile
import shutil

from .parser import parse
from .archive import compress, copy_tree
from .commands import flavour_name, flavour_entrypoint_script_path
from .ezjail import Runner


def run(jailfile='Jailfile', name=None, command=None, args=None):
    """
    Run the given command or the default entrypoint in the jail
    """
    commands = parse(jailfile)
    command = command or flavour_entrypoint_script_path(commands)
    name = name or flavour_name(commands)

    with Runner(name) as runner:
        runner.exec(command)
