
from contextlib import ExitStack
import os
import subprocess
import sys

from .jobs import ForkedProcess, Process
from .builtins import BUILTINS, IO, Shell
from .parser import Command

def _run_builtin_bg(builtin, cmd: Command, shell: Shell, io: IO) -> Process:
    io.stdout.flush()
    io.stderr.flush()
    pid = os.fork()

    if pid == 0:
        try:
            status = builtin(cmd.argv[1:], shell, io)
        except SystemExit as e:
            status = e.code if isinstance(e.code, int) else 0
        except BaseException as e:
            print(f'{cmd.name}: {e}', file=io.stderr)
            status = 1
        finally:
            io.stdout.flush()
            io.stderr.flush()
        os._exit(status)

    return ForkedProcess(pid)


def _open_io(cmd: Command, stack: ExitStack) -> IO:
    streams = {1: sys.stdout, 2: sys.stderr}
    for r in cmd.redirects:
        streams[r.fd] = stack.enter_context(
            open(r.path, 'a' if r.append else 'w')
        )
    return IO(sys.stdin, streams[1], streams[2])


def execute(cmd: Command, shell: Shell, source_command: str) -> int:
    with ExitStack() as stack:
        try:
            io = _open_io(cmd, stack)
        except OSError as e:
            print(f'{e.filename}: {e.strerror}', file=sys.stderr)
            return 1

        if (builtin := BUILTINS.get(cmd.name)):
            if not cmd.background:
                return builtin(cmd.argv[1:], shell, io)
            proc = _run_builtin_bg(builtin, cmd, shell, io)
        else:
            io.stdout.flush()

            try:
                null = subprocess.DEVNULL
                proc = subprocess.Popen(
                    cmd.argv, 
                    stdin=null if cmd.background else io.stdin,
                    stderr=io.stderr, stdout=io.stdout
                )
            except FileNotFoundError:
                print(f'{cmd.name}: command not found', file=io.stderr)
                return 127

            if not cmd.background:
                return proc.wait()

        job = shell.jobs.add(proc, source_command)
        print(f'[{job.id}] {proc.pid}', file=io.stderr)
        return 0
