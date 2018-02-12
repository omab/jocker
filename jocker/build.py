"""
Build the given Jail base
"""
from .parser import Jockerfile
from .backends.utils import get_backend


def build(jockerfile='Jockerfile', build=None, install=False):
    """
    Build the base from the given Jockerfile.
    """
    jail_backend = get_backend()
    jockerfile = Jockerfile(jockerfile)
    jail_backend.build(jockerfile, build=build, install=install)
