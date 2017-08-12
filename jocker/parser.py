"""
Jailfile file format parser
"""
import re

from .commands import COMMANDS


# Join lines split by \
LINE_SPLITS = re.compile(r'\\\n')

def clean_lines(content):
    """
    Take a jailfile content and clean each lines.
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


def parse(path='Jailfile'):
    """
    Parse the content and outputs an array for the parsed commands.
    """
    # TODO: validate Jailfile, like unique name entry, unique author, etc
    with open(path, 'r') as jailfile:
        lines = clean_lines(jailfile.read().strip())
        return [build_command(line) for line in lines]
