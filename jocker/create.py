"""
Create a jail from the given base
"""
from .parser import parse, Jockerfile
from .backends.utils import get_backend


def create_from_base(base, name=None, network=None):
    """
    Build a Jail from the given base.
    """
    jail_backend = get_backend(jailname=name)
    jockerfile = jail_backend.base_jockerfile(base)
    create_from_jockerfile(jockerfile, name, network)


def create_from_jockerfile(jockerfile, name=None, network=None):
    """
    Build a Jail from the given base.
    """
    jockerfile = Jockerfile(jockerfile)
    jail_backend = get_backend(jailname=name)
    jail_backend.create(jockerfile, network=network)
