"""
Create a jail from the flavour
"""

import os
import uuid
import subprocess

from .parser import parse
from .commands import flavour_name


def create(jailfile='Jailfile', name=None, network=None):
    """
    Build the flavour from the given Jailfile.
    """
    commands = parse(jailfile)
    flavour = flavour_name(commands)
    name = name or '{flavour}_{id}'.format(flavour=flavour, id=uuid.uuid4())
    network = network or 'lo1|127.1.1.5'
    subprocess.run('ezjail-admin create -f {flavour} {name} \'{network}\''.format(
        flavour=flavour,
        name=name,
        network=network
    ), shell=True)
