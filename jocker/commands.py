"""
Jailfile commands
"""

import os
import shutil

from jinja2 import Environment, PackageLoader, select_autoescape

from .archive import copy_tree, copy_file


JINJA_ENV = Environment(
    loader=PackageLoader('jocker', 'templates'),
    autoescape=select_autoescape(['sh'])
)


FLAVOURS_DIR = os.path.join('/usr', 'jails', 'flavours')


def flavour_commands(commands, command_type):
    """Return commands of the given type"""
    return [command for command in commands
            if isinstance(command, command_type)]


def flavour_env(commands, index):
    """
    Return flavour env values defined by the ENV command that are
    before the given index
    """
    return [command.get_value()
            for command in flavour_commands(commands[:index], CommandEnv)]


def flavour_name(commands):
    """Return flavour name defined by the NAME command"""
    return flavour_commands(commands, CommandName)[0].get_value()


def flavour_entrypoint(commands):
    """Return flavour entrypoint defined by the ENTRYPOINT command"""
    return flavour_commands(commands, CommandEntrypoint)[0].get_value()


def flavour_entrypoint_script_path(commands):
    """Return the script path for the default entrypoint command"""
    name = flavour_name(commands)
    return os.path.join('usr', 'local', 'bin',
                        'flavour_{name}'.format(name=name))


class CommandBase(object):
    """
    Base class for commands that can be ran from a Jailfile.
    """
    def __init__(self, value):
        """
        Init method, value is the whole content without the command.
        """
        self.value = value

    def get_value(self):
        """
        Return stored value, override if value needs further processing.
        """
        return self.value

    def build(self, destdir, commands):
        """
        Build this command into the jail flavour being built at destdir.
        """
        print("{command} => {destdir}".format(command=self.command_name(),
                                              destdir=destdir))
        # raise NotImplementedError('Implement in subclass')

    def command_name(self):
        """
        Command name, this is derived from the class name, override if needed.
        """
        return self.__class__.__name__.replace('Command', '').upper()

    def ensure_dir(self, destdir, path):
        """Ensure that a directory exists inside the destination"""
        dest = os.path.join(destdir, path)
        os.makedirs(dest, exist_ok=True)
        return dest

    def write_to_jocker(self, destdir, content):
        """Write content to etc/jocker file"""
        dest = self.ensure_dir(destdir, 'etc')
        with open(os.path.join(dest, 'jocker'), 'w') as file:
            file.write(content)

    def render_script(self, destdir, destpath, template_name, context=None):
        """
        Render script from templates dir into the destination path
        inside the jail flavour.
        """
        self.ensure_dir(destdir, os.path.dirname(destpath))
        absolute_destpath = os.path.join(destdir, destpath)
        with open(absolute_destpath, 'w') as file:
            context = context or {}
            template = JINJA_ENV.get_template(template_name)
            script = template.render(**context)
            file.write(script)
        os.chmod(absolute_destpath, 0o755)
        return absolute_destpath

    def __str__(self):
        """
        Str method, output should be close to the Jailfile content.
        """
        return '{command} {value}'.format(command=self.command_name(),
                                          value=self.get_value())


class CommandAuthor(CommandBase):
    """
    AUTHOR command class.
    """
    def build(self, destdir, commands):
        """Write AUTHOR details into etc/jocker file"""
        self.write_to_jocker(
            destdir,
            'AUTHOR {value}'.format(value=self.get_value())
        )


class CommandName(CommandBase):
    """
    NAME command class.
    """
    def build(self, destdir, commands):
        """Write NAME details into etc/jocker file"""
        self.write_to_jocker(
            destdir,
            'NAME {value}'.format(value=self.get_value())
        )


class CommandVersion(CommandBase):
    """
    VERSION command class.
    """
    def build(self, destdir, commands):
        """Write VERSION details into etc/jocker file"""
        self.write_to_jocker(
            destdir,
            'VERSION {value}'.format(value=self.get_value())
        )


class CommandFrom(CommandBase):
    """
    FROM command class.
    """
    def get_value(self):
        """
        Split values since many base flavours can be specified.
        """
        return self.value.split()

    def flavour_dir(self, name):
        """Return an absolute path to an installed flavour"""
        return os.path.join(FLAVOURS_DIR, name)

    def build(self, destdir, commands):
        """
        Copy the content of the different base flavours into destdir
        """
        for flavour in self.get_value():
            if ':' in flavour:
                # TODO: deal with flavour versioning
                flavour, version = flavour.split(':', 1)
            copy_tree(self.flavour_dir(flavour), destdir)


class CommandEnv(CommandBase):
    """
    ENV command class.
    """
    def get_value(self):
        """
        Split entry in key, value pair.
        """
        return self.value.split(' ', 1)

    def build(self, destdir, commands):
        """
        Store environment values in scripts at /usr/local/etc/jail_env/
        """
        name = flavour_name(commands)
        index = commands.index(self)
        key, value = self.get_value()
        destpath = os.path.join(
            'usr', 'local', 'etc', 'jail_env',
            '{index:02d}_flavour_{name}.env'.format(index=index, name=name)
        )
        self.render_script(destdir, destpath, 'environment_script.sh.jinja2', {
            'flavour': {
                'name': name,
                'env': {
                    'key': key,
                    'value': value
                }
            }
        })


class CommandRun(CommandBase):
    """
    RUN command class.
    """
    def build(self, destdir, commands, template_name='setup_script.sh.jinja2'):
        name = flavour_name(commands)
        index = commands.index(self)
        filename = '{index:02d}_ezjail.flavour.{name}'.format(index=index,
                                                              name=name)
        destpath = os.path.join('etc', 'rc.d', filename)
        self.render_script(destdir, destpath, template_name, {
            'flavour': {
                'filename': filename,
                'name': name,
                'command': self.get_value()
            }
        })


class CommandAdd(CommandBase):
    """
    ADD command class.
    """
    def get_value(self):
        return self.value.split(' ', 2)

    def build(self, destdir, commands):
        """Copy the content from value into dest inside the jail"""
        orig, dest = self.get_value()
        dest = self.ensure_dir(destdir, dest.strip('/'))
        orig = os.path.abspath(orig)
        if os.path.isdir(orig):
            copy_tree(orig, dest)
        else:
            copy_file(orig, dest)


class CommandEntrypoint(CommandRun):
    """
    ENTRYPOINT command class.
    """
    def build(self, destdir, commands):
        """Save entrypoint into a script at /usr/local/bin"""
        name = flavour_name(commands)
        destpath = flavour_entrypoint_script_path(commands)
        self.render_script(destdir, destpath, 'entrypoint_script.sh.jinja2', {
            'flavour': {
                'name': name,
                'command': self.get_value()
            }
        })


COMMANDS = {
    'author': CommandAuthor,
    'name': CommandName,
    'version': CommandVersion,
    'from': CommandFrom,
    'env': CommandEnv,
    'run': CommandRun,
    'add': CommandAdd,
    'entrypoint': CommandEntrypoint
}
