import os
from subprocess import PIPE, STDOUT, run


def run_command(command, args=None, env=None, check=False):
    """
    Exec command with Popen
    """
    if args:
        command = '{command} {args}'.format(command=command, args=args)

    os.environ.update(env or {})

    if check:
        return run(
            command, shell=True, stdout=PIPE, stderr=STDOUT
        ).stdout.decode()
    else:
        return run(command, shell=True, check=True)
