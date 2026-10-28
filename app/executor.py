
from contextlib import ExitStack
import subprocess
import sys

from .builtins import BUILTINS, IO, Shell
from .parser import Command

def _open_io(cmd: Command, stack: ExitStack) -> IO:
    streams = {1: sys.stdout, 2: sys.stderr}
    for r in cmd.redirects:
        streams[r.fd] = stack.enter_context(
            open(r.path, 'a' if r.append else 'w')
        )
    return IO(sys.stdin, streams[1], streams[2])


def execute(cmd: Command, shell: Shell) -> int:
    with ExitStack() as stack:
        try:
            io = _open_io(cmd, stack)
        except OSError as e:
            print(f'{e.filename}: {e.strerror}', file=sys.stderr)
            return 1

        if (builtin := BUILTINS.get(cmd.name)):
            return builtin(cmd.argv[1:], shell, io)

        try:
            io.stdout.flush()
            proc = subprocess.Popen(
                cmd.argv, 
                stdin=io.stdin, stderr=io.stderr, stdout=io.stdout
            )
        except FileNotFoundError:
            print(f'{cmd.name}: command not found', file=io.stderr)
            return 127

        return proc.wait()
