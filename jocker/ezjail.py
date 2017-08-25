"""
ezjail wrapper
"""
import uuid
import subprocess


def ezjail(command, *args):
    """
    Run ezjail-admin command with args
    """
    try:
        return subprocess.run(
            'ezjail-admin {command} {args}'.format(command=command,
                                                   args=' '.join(args)),
            shell=True
        )
    except KeyboardInterrupt:  # Ctrl + c
        pass


def create(flavour, jail_name=None, network=None):
    """
    Run ezjail create
    """
    jail_name = jail_name or '{flavour}_{id}'.format(flavour=flavour,
                                                     id=uuid.uuid4())
    # TODO: select a correct default
    network = network or 'lo1|127.1.1.5'

    return ezjail('create',
        '-f {flavour}'.format(flavour=flavour),
        jail_name,
        '\'{network}\''.format(network=network)
    )


def start(jail_name):
    """Start jail"""
    return ezjail('start', jail_name)


def stop(jail_name):
    """Stop jail"""
    return ezjail('stop', jail_name)


def exec(jail_name, command):
    """Exec the given command in the jail"""
    return ezjail('console',
                  '-e \'{command}\''.format(command=command),
                  jail_name)


class Runner(object):
    """Runner context manager"""
    def __init__(self, jail_name):
        """Initialize context manager, jailname is needed"""
        self.jail_name = jail_name

    def exec(self, command):
        """Exec given command on current jail context"""
        return exec(self.jail_name, command)

    def __enter__(self):
        """Start jail upon enter"""
        start(self.jail_name)
        return self

    def __exit__(self, *args):
        """Stop jail upon leave"""
        stop(self.jail_name)
