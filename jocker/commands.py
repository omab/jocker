"""
Jockerfile commands
"""

import os
import shutil

from jinja2 import Environment, PackageLoader, select_autoescape

from .archive import copy_tree, copy_file


JINJA_ENV = Environment(
    loader=PackageLoader('jocker', 'templates'),
    autoescape=select_autoescape(['sh'])
)


def base_name(commands):
    """Return base name defined by the NAME command"""
    commands = [command for command in commands
                if isinstance(command, CommandName)]
    return commands[0].get_value()


class CommandBase(object):
    """
    Base class for commands that can be executed from a Jockerfile.
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

    def run(self, backend, destdir, commands):
        """
        Run this command into the started jail.
        """
        pass

    def build(self, backend, destdir, commands):
        """
        Build this command into the jail base being built at destdir.
        """
        pass

    def create(self, backend, commands):
        """
        Create this command into the jail currently running.
        """
        pass

    def command_name(self):
        """
        Command name, this is derived from the class name, override if needed.
        """
        return self.__class__.__name__.replace('Command', '').upper()

    def ensure_dir(self, destdir, path):
        """Ensure that a directory exists inside the destination"""
        path = path.strip('/')
        destdir = destdir.rstrip('/')
        dest = os.path.join(destdir, path)
        os.makedirs(dest, exist_ok=True)
        return dest

    def render_script(self, destdir, destpath, template_name, context=None):
        """
        Render script from templates dir into the destination path
        inside the jail base.
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
        Str method, output should be close to the Jockerfile content.
        """
        return '{command} {value}'.format(command=self.command_name(),
                                          value=self.get_value())


class CommandNop(CommandBase):
    """
    NOP (no operation) command.
    """
    pass


class CommandName(CommandNop):
    """
    NAME command class.
    """
    pass


class CommandFrom(CommandBase):
    """
    FROM command class.
    """
    def get_value(self):
        """
        Split values since many bases can be specified.
        """
        return super(CommandFrom, self).get_value().split()

    def base_dir(self, backend, name):
        """Return an absolute path to an installed base"""
        return os.path.join(backend.BASE_DIR, name)

    def build(self, backend, destdir, commands):
        """
        Copy the content of the different bases into destdir
        """
        for base in self.get_value():
            if ':' in base:
                # TODO: deal with base versioning
                base, version = base.split(':', 1)
            copy_tree(self.base_dir(backend, base), destdir)


class CommandEnv(CommandBase):
    """
    ENV command class.
    """
    def get_value(self):
        """
        Split entry in key, value pair.
        """
        return super(CommandEnv, self).get_value().split(' ', 1)

    def run(self, backend, destdir, commands):
        """
        Run Env command
        """
        self.load_value()

    def build(self, backend, destdir, commands):
        """
        Build Env command
        """
        self.load_value()

    def create(self, backend, commands):
        """
        Create Env command
        """
        self.load_value()

    def load_value(self):
        """
        Load value and set it in the environment, don't write if key
        already there.
        """
        name, value = self.get_value()
        if name not in os.environ:
            os.environ[name] = value


class CommandRun(CommandBase):
    """
    RUN command class.
    """
    def create(self, backend, commands):
        """
        Run the command in the jail being created
        """
        backend.exec(self.get_value(), **commands.env(commands.index_of(self)))


class CommandAdd(CommandBase):
    """
    ADD command class.
    """
    def get_value(self):
        """
        Return stored value, splits value in src and dest pair.
        """
        return super(CommandAdd, self).get_value().split(' ', 2)

    def build(self, backend, destdir, commands):
        """
        Copy the content from value into dest inside the jail
        """
        orig, dest = self.get_value()
        dest = self.ensure_dir(destdir, dest)
        orig = os.path.abspath(orig)
        if os.path.isfile(orig):
            copy_file(orig, dest)
        elif os.path.isdir(orig):
            copy_tree(orig, dest)


class CommandEntrypoint(CommandRun):
    """
    ENTRYPOINT command class.
    """
    pass


class CommandVolume(CommandBase):
    """
    VOLUME command class.
    """
    def get_value(self):
        """
        Return stored value, splits value in src and dest pair.
        """
        return super(CommandVolume, self).get_value().split(' ', 2)

    def create(self, backend, commands):
        """
        Define nullfs mount
        """
        pass

    def build(self, backend, destdir, commands):
        """Save volume definition"""
        # mount_nullfs  with nullfs, how is it setup?
        orig, dest = self.get_value()
        return 'mount_nullfs {orig} {dest}'.format(
            orig=orig,
            dest=dest
        )


COMMANDS = {
    'author': CommandNop,
    'name': CommandName,
    'version': CommandNop,
    'from': CommandFrom,
    'env': CommandEnv,
    'run': CommandRun,
    'add': CommandAdd,
    'entrypoint': CommandEntrypoint,
    'volume': CommandVolume
}
