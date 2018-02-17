"""
Jail wrapper backend definition
"""
import os
import sys
import uuid
import tempfile
import logging

from ..commands import CommandEntrypoint
from ..parser import build_command, Jockerfile
from ..archive import copy_tree

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger('jocker')
logger.setLevel(logging.DEBUG)


class Backend(object):
    """Base backend definition"""
    BASE_DIR = os.environ.get('JOCKER_BASE_DIR', '/usr/jails/')
    JAILS_DIR = BASE_DIR

    def __init__(self, jailname, base=None):
        """Backend initialization"""
        self.jailname = jailname or str(uuid.uuid4())
        self.logger = logger

    def base_jockerfile(self, base):
        """Return the Jockerfile used to define base"""
        return Jockerfile(
            os.path.join(self.BASE_DIR, base, 'etc', 'Jockerfile')
        )

    @property
    def jockerfile(self):
        """Return the Jockerfile used to define base"""
        if not hasattr(self, '_jockerfile'):
            self._jockerfile = Jockerfile(
                os.path.join(self.JAILS_DIR, self.jailname, 'etc', 'Jockerfile')
            )
        return self._jockerfile

    def jaildir(self):
        """Return the jail base directory"""
        return os.path.join(self.JAILS_DIR, self.jailname)

    def create_jail(self, jockerfile, base=None, network=None):
        """Create jail"""
        raise NotImplementedError('Implement in subclass')

    def create(self, jockerfile, base=None, network=None):
        """Create jail and run create commands to bootstrap on it"""
        self.create_jail(jockerfile, base=base, network=network)
        with self.runner(create=True) as runner:
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

    def bootstrap_jail(self, runner):
        """Run any bootstraping command needed to run the jail"""
        commands = [command for command in self.jockerfile.commands
                    if not isinstance(command, CommandEntrypoint)]
        returncode = 0

        for command in commands:
            if returncode:
                break
            returncode = command.run(runner, self.jockerfile)

    def unbootstrap_jail(self, runner):
        """Roll-back any bootstraping command needed to run the jail"""
        commands = [command for command in self.jockerfile.commands
                    if not isinstance(command, CommandEntrypoint)]
        returncode = 0

        for command in reversed(commands):
            if returncode:
                break
            returncode = command.unrun(runner, self.jockerfile)

    def run(self, command=None):
        """Run default commands or given one in started jail"""
        if command:
            command = build_command(
                'ENTRYPOINT {command}'.format(command=command)
            )
        else:
            command = self.jockerfile.entrypoint()

        with self.runner() as runner:
            command.run(runner, self.jockerfile)

    def runner(self, create=False):
        """Return context runner"""
        if create:
            return CreateRunner(self, self.jailname)
        else:
            return RunRunner(self, self.jailname)


class BaseRunner(object):
    """Base runner context manager"""
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


class RunRunner(BaseRunner):
    """Run runner context manager"""
    def __enter__(self):
        """Start jail upon enter"""
        super(RunRunner, self).__enter__()
        self.backend.bootstrap_jail(self)
        return self

    def __exit__(self, *args):
        """Stop jail upon leave"""
        self.backend.unbootstrap_jail(self)
        super(RunRunner, self).__exit__()


class CreateRunner(BaseRunner):
    """Creation runner context manager"""
    def __exit__(self, *args):
        """Stop jail upon leave"""
        self.backend.unbootstrap_jail(self)
        super(CreateRunner, self).__exit__()
