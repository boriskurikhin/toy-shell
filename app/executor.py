
from contextlib import ExitStack
import os
import subprocess
import sys
from typing import TextIO

from .jobs import ForkedProcess, Process
from .builtins import BUILTINS, IO, Shell
from .parser import Command, Pipeline

def _run_builtin_bg(builtin, cmd: Command, shell: Shell, io: IO) -> Process:
    io.stdout.flush()
    io.stderr.flush()

    sys.stdout.flush()
    sys.stderr.flush()

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


def _open_io(cmd: Command, stdin: TextIO, stdout: TextIO, stack: ExitStack) -> IO:
    streams = {0: stdin, 1: stdout, 2: sys.stderr}
    for r in cmd.redirects:
        streams[r.fd] = stack.enter_context(
            open(r.path, 'a' if r.append else 'w')
        )
    return IO(streams[0], streams[1], streams[2])


def _start(cmd: Command, shell: Shell, io: IO, in_process_ok: bool) -> Process | int:
    if (builtin := BUILTINS.get(cmd.name)):
        if in_process_ok:
            return builtin(cmd.argv[1:], shell, io)
        return _run_builtin_bg(builtin, cmd, shell, io)
    io.stdout.flush()
    try:
        return subprocess.Popen(
            cmd.argv, stdin=io.stdin, stdout=io.stdout, stderr=io.stderr
        )
    except FileNotFoundError:
        print(f'{cmd.name}: command not found', file=io.stderr)
        return 127

def execute(pipeline: Pipeline, shell: Shell, source_command: str) -> int:
    single = len(pipeline.commands) == 1 and not pipeline.background
    procs: list[Process] = []
    status = 0

    with ExitStack() as stack:
        stdin: TextIO = (
            sys.stdin if not pipeline.background 
            else stack.enter_context(open(os.devnull))
        )

        for i, cmd in enumerate(pipeline.commands):
            last = i == len(pipeline.commands) - 1
            if last:
                stdout, next_stdin = sys.stdout, None
            else:
                r, w = os.pipe()
                stdout, next_stdin = os.fdopen(w, 'w'), os.fdopen(r, 'r')

            try:
                io = _open_io(cmd, stdin, stdout, stack)
            except OSError as e:
                print(f'{e.filename}: {e.strerror}', file=sys.stderr)
                status = 1
            else:
                result = _start(cmd, shell, io, in_process_ok=single)
                if isinstance(result, int):
                    status = result
                else:
                    procs.append(result)

            if i > 0:
                stdin.close()

            if not last:
                stdout.close()

            stdin = next_stdin

        if pipeline.background:
            job = shell.jobs.add(procs, source_command)
            print(f'[{job.id}] {procs[-1].pid}', file=sys.stderr)
            return 0

        for p in procs:
            code = p.wait()

        return code if procs else status
