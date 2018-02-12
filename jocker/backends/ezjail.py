"""
ezjail wrapper
"""
import os

from ..utils import run_command
from .jail import JailBackend


class EZJailBackend(JailBackend):
    """EZJail backend"""
    JAILS_DIR = os.environ.get('JOCKER_JAILS_BASE_DIR', '/usr/jails/')
    BASE_DIR = os.environ.get('JOCKER_BASE_DIR', '/usr/jails/flavours/')
    DEFAULT_NETWORK = os.environ.get('JOCKER_DEFAULT_NETWORK', 'lo1|127.1.1.5')

    def create_jail(self, jockerfile, base=None, network=None):
        """Run ezjail create"""
        base = base or jockerfile.name()
        self.ezjail(
            'create',
            args='-f {base} {jailname} \'{network}\''.format(
                base=base,
                jailname=self.jailname,
                network=network or self.DEFAULT_NETWORK
            )
        )
        self.logger.info('Created jail: {name}'.format(name=self.jailname))

    def start(self):
        """Start jail"""
        return self.ezjail('start', args=self.jailname)

    def stop(self):
        """Stop jail"""
        return self.ezjail('stop', args=self.jailname)

    def ezjail(self, command, args=None, env=None):
        """
        Run ezjail-admin command with args
        """
        return run_command(
            'ezjail-admin {command}'.format(command=command),
            args=args,
            env=env
        )
