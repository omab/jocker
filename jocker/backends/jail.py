"""
jail wrapper
"""
import os

from .base import Backend
from ..utils import run_command


class JailBackend(Backend):
    """Jail backend"""
    JAILS_DIR = os.environ.get('JOCKER_JAILS_BASE_DIR', '/usr/jails/')

    def exec(self, command, **kwargs):
        """Exec the given command in the jail"""
        return self.jail(
            'jexec {jid} sh -c \'{command}\''.format(
                jid=self.jid(),
                command=command
            ),
            env=kwargs
        )

    def jid(self):
        """
        Return jail JID for current jail
        """
        cmd = '/usr/sbin/jls -j {jailname}'.format(jailname=self.jailname)
        stdout = run_command(cmd, check=True)
        line = stdout.split('\n')[1]
        if not line:
            raise ValueError(
                'No jail {jailname} present'.format(jailname=self.jailname)
            )
        return line.strip().split(' ', 1)[0]

    def jail(self, command, args=None, env=None):
        """
        Run a jail command with args
        """
        return run_command(command, args=args, env=env)
