import os
import sys
import argparse

from .build import build
from .create import create


def do_build(args):
    """Run build"""
    build(args.jailfile, build=args.build, install=args.install)


def do_create(args):
    """Run create"""
    create(args.jailfile, name=args.name, network=args.net)


def do_import(args):
    print('IMPORT:', args)


def do_run(args):
    print('RUN:', args)


parser = argparse.ArgumentParser(description='Jocker - jail definition and management tool')
parser.add_argument(
    '--jailfile',
    default='Jailfile',
    help='specify the Jailfile (default Jailfile)'
)
subparsers = parser.add_subparsers()

build_parser = subparsers.add_parser(
    'build',
    description='Build a jail flavour'
)
build_parser.add_argument('--build', help='build directory')
build_parser.add_argument('--install', action='store_true',
                          help='install the built jail flavour')
build_parser.set_defaults(func=do_build)

create_parser = subparsers.add_parser(
    'create',
    description='Create a jail from the created flavour'
)
create_parser.add_argument('--name', help='jail name')
create_parser.add_argument('--net', help='jail network')
create_parser.set_defaults(func=do_create)

import_parser = subparsers.add_parser(
    'import',
    description='Import the named jail flavour'
)
import_parser.add_argument('names', nargs='*', help='jail flavours to import')
import_parser.set_defaults(func=do_import)

run_parser = subparsers.add_parser(
    'run',
    description='Run a command in the given jail'
)
run_parser.add_argument('name', help='jail to run the command on')
run_parser.add_argument('command', nargs='+', help='command to run')
run_parser.add_argument('args', nargs=argparse.REMAINDER,
                        help='command arguments to run')
run_parser.set_defaults(func=do_run)

if __name__ == '__main__':
    args = parser.parse_args()
    if len(sys.argv) > 1:
        args.func(args)
    else:
        parser.print_help()
