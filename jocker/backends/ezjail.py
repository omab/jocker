"""
ezjail wrapper
"""
import os
from subprocess import Popen, PIPE, STDOUT

from .base import Backend


class EZJailBackend(Backend):
    """EZJail backend"""
    BASE_DIR = os.environ.get('JOCKER_BASE_DIR', '/usr/jails/flavours/')

    def create(self, base, network=None):
        """Run ezjail create"""
        # TODO: select a correct default
        network = network or 'lo1|127.1.1.5'

        self.ezjail('create',
                    '-f {base}'.format(base=base),
                    self.jailname,
                    '\'{network}\''.format(network=network))
        self.logger.info('Created jail: {name}'.format(name=self.jailname))

    def start(self):
        """Start jail"""
        return self.ezjail('start', self.jailname)

    def stop(self):
        """Stop jail"""
        return self.ezjail('stop', self.jailname)

    def exec(self, command, env=None):
        """Exec the given command in the jail"""
        return self.ezjail('console',
                           '-e \'{command}\''.format(command=command),
                           self.jailname)

    def ezjail(self, command, env=None, *args):
        """
        Run ezjail-admin command with args
        """
        cmd = 'ezjail-admin {command} {args}'.format(command=command,
                                                     args=' '.join(args))

        try:
            with Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT) as proc:
                self.logger.info(proc.stdout.read())
        except KeyboardInterrupt:  # Ctrl + c
            pass
