"""
Jail wrapper backend definition
"""
import os
import sys
import uuid
import tempfile
import logging

from ..commands import base_name
from ..parser import build_command
from ..archive import copy_tree

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger('jocker')
logger.setLevel(logging.DEBUG)


class Backend(object):
    """Base backend definition"""
    BASE_DIR = os.environ.get('JOCKER_BASE_DIR', '/usr/jails/')
    JAILS_DIR = BASE_DIR

    def __init__(self, jailname):
        """Backend initialization"""
        self.jailname = jailname or str(uuid.uuid4())
        self.logger = logger

    def base_jockerfile(self, base):
        """Return the Jockerfile used to define base"""
        return os.path.join(self.BASE_DIR, base, 'etc', 'Jockerfile')

    def jail_jockerfile(self):
        """Return the Jockerfile used to define base"""
        return os.path.join(self.JAILS_DIR, self.jailname, 'etc', 'Jockerfile')

    def create_jail(self, jockerfile, base=None, network=None):
        """Create jail"""
        raise NotImplementedError('Implement in subclass')

    def create(self, jockerfile, base=None, network=None):
        """Create jail and run create commands to bootstrap on it"""
        self.create_jail(jockerfile, base=base, network=network)
        with self.runner() as runner:
            for command in jockerfile.commands:
                command.create(runner, jockerfile)

    def start(self):
        """Start jail"""
        raise NotImplementedError('Implement in subclass')

    def stop(self):
        """Stop jail"""
        raise NotImplementedError('Implement in subclass')

    def exec(self, command, **kwargs):
        """Exec command in jail"""
        raise NotImplementedError('Implement in subclass')

    def build(self, jockerfile, build=None, install=False):
        name = jockerfile.name()

        self.logger.info('Building jail base: {name}'.format(name=name))

        commands = [
            # ensure the Jockerfile is copied into the new jail
            build_command('ADD {path} /etc/'.format(path=jockerfile.path))
        ] + jockerfile.commands

        with tempfile.TemporaryDirectory() as tmp:
            for command in commands:
                command.build(self, tmp)
            if build:
                destpath = os.path.join(build, name)
                copy_tree(tmp, destpath)
                os.chmod(destpath, 0o755)
            if install:
                destpath = os.path.join(self.BASE_DIR, name)
                copy_tree(tmp, destpath)
                os.chmod(destpath, 0o755)
            return tmp

    def run(self, jockerfile, command=None):
        """Run default commands or given one in started jail"""
        if command:
            command = build_command('JEXEC {command}'.format(command=command))

        commands = command and [command] or jockerfile.commands
        returncode = 0

        with self.runner() as runner:
            for command in commands:
                if returncode and not getattr(command, 'ignore_errors', False):
                    break
                returncode = command.run(self, jockerfile)

    def runner(self):
        """Return context runner"""
        return Runner(self, self.jailname)


class Runner(object):
    """Runner context manager"""
    def __init__(self, backend, jailname):
        """Initialize context manager, jailname is needed"""
        self.jailname = jailname
        self.backend = backend

    def exec(self, command, **kwargs):
        """Exec given command on current jail context"""
        return self.backend.exec(command, **kwargs)

    def __enter__(self):
        """Start jail upon enter"""
        self.backend.start()
        return self

    def __exit__(self, *args):
        """Stop jail upon leave"""
        self.backend.stop()
