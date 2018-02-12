"""
Jockerfile file format parser
"""
import re

from .commands import COMMANDS, CommandEnv, CommandName, CommandJExec


# Join lines split by \
LINE_SPLITS = re.compile(r'\\\n')


def clean_lines(content):
    """
    Take a Jockerfile content and clean each lines.
    """
    return LINE_SPLITS.sub(
        '',
        '\n'.join(line.strip() for line in content.split('\n'))
    ).split('\n')


def build_command(line):
    """
    Take a line and build the corresponding command class.
    """
    command, rest = line.split(' ', 1)
    command = command.lower()
    command_class = COMMANDS.get(command)
    if not command_class:
        raise RuntimeError('Invalid command {command}'.format(command=command))
    return command_class(rest)


def parse(path='Jockerfile'):
    """
    Parse the content and outputs an array for the parsed commands.
    """
    # TODO: validate Jockerfile, like unique name entry, unique author, etc
    with open(path, 'r') as jockerfile:
        lines = clean_lines(jockerfile.read().strip())
        return [build_command(line) for line in lines]


class Jockerfile(object):
    def __init__(self, jockerfile='Jockerfile'):
        """
        Init parsed Jockerfile
        """
        self.path = jockerfile
        self.commands = parse(jockerfile)

    def name(self):
        """
        Return base name defined by the NAME command
        """
        return self.filter_commands(CommandName)[0].get_value()

    def jexec(self):
        """
        Return base runtime commands defined by the JEXEC command
        """
        return self.filter_commands(CommandJExec)

    def index_of(self, command):
        """
        Return index of command in the commands list
        """
        try:
            return self.commands.index(command)
        except ValueError:
            return None

    def env(self, index=None):
        """
        Return base env values defined by the ENV command that are
        before the given index
        """
        return dict([command.get_value()
                     for command in self.filter_commands(CommandEnv, index)])

    def filter_commands(self, command_type, index=None):
        """Return commands of the given type and max index"""
        return [command for command in self.commands[:index]
                if isinstance(command, command_type)]

    def __iter__(self):
        """Iterate over commands"""
        for item in self.commands:
            yield item
