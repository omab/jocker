"""
Create a jail from the flavour
"""
from .parser import parse
from .commands import flavour_name
from .ezjail import create as ezjail_create


def create(jailfile='Jailfile', name=None, network=None):
    """
    Build the flavour from the given Jailfile.
    """
    commands = parse(jailfile)
    flavour = flavour_name(commands)
    return ezjail_create(flavour, name, network)
