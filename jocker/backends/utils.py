"""Jail backend utilities"""
from .ezjail import EZJailBackend


BACKENDS = {
    'ezjail': EZJailBackend
}


def get_backend(backend='ezjail', jailname=None):
    """Return an instance of a given backend"""
    return BACKENDS[backend](jailname)
