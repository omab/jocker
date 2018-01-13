"""
Jail wrapper backend definition
"""
import os
import uuid
import logging


class Backend(object):
    """Base backend definition"""
    BASE_DIR = os.environ.get('JOCKER_BASE_DIR', '/usr/jails/')

    def __init__(self, jailname):
        """Backend initialization"""
        self.jailname = jailname or str(uuid.uuid4())
        self.logger = logging.getLogger('jocker:' + self.jailname)
        self.logger.setLevel(logging.INFO)

    def base_jockerfile(self, base):
        """Return the Jockerfile used to define base"""
        return os.path.join(self.BASE_DIR, 'etc', 'Jockerfile')

    def create(self, network=None):
        """Create jail"""
        raise NotImplementedError('Implement in subclass')

    def start(self):
        """Start jail"""
        raise NotImplementedError('Implement in subclass')

    def stop(self):
        """Stop jail"""
        raise NotImplementedError('Implement in subclass')

    def exec(self, command, env=None):
        """Exec command in jail"""
        raise NotImplementedError('Implement in subclass')

    def runner(self):
        """Return context runner"""
        return Runner(self, self.jailname)


class Runner(object):
    """Runner context manager"""
    def __init__(self, backend, jailname):
        """Initialize context manager, jailname is needed"""
        self.jailname = jailname
        self.backend = backend

    def exec(self, command, env=None):
        """Exec given command on current jail context"""
        return self.backend.exec(self.jailname, command, env or {})

    def __enter__(self):
        """Start jail upon enter"""
        self.backend.start(self.jailname)
        return self

    def __exit__(self, *args):
        """Stop jail upon leave"""
        self.backend.stop(self.jailname)
