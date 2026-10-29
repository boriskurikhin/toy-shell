
from dataclasses import dataclass, field
from functools import cache
import os
from pathlib import Path
import shutil
from typing import NamedTuple, TextIO

from .history import History
from .jobs import JobTable


class IO(NamedTuple):
    stdin: TextIO
    stdout: TextIO
    stderr: TextIO


@cache
def programs_in_path() -> dict[str, str]:
    programs: dict[str, str] = {}
    for dir in os.environ.get('PATH', os.defpath).split(os.pathsep):
        try:
            entries = os.scandir(dir)
        except OSError:
            continue
        with entries:
            for entry in entries:
                if os.access(entry.path, os.X_OK) and entry.is_file():
                    programs.setdefault(entry.name, entry.path)
    return programs

@dataclass
class Shell:
    completions: dict[str, str] = field(default_factory=dict)
    jobs: JobTable = field(default_factory=JobTable)
    history: History = field(default_factory=History)


def echo(args: list[str], shell: Shell, io: IO) -> int:
    print(*args, file=io.stdout)
    return 0


def pwd(args: list[str], shell: Shell, io: IO) -> int:
    print(os.getcwd(), file=io.stdout)
    return 0


def jobs(args: list[str], shell: Shell, io: IO) -> int:
    for job in shell.jobs:
        print(shell.jobs.format(job), file=io.stdout)
    shell.jobs.reap()
    return 0


def cd(args: list[str], shell: Shell, io: IO) -> int:
    new_path = os.path.expanduser(args[0] if args else '~')

    try:
        os.chdir(new_path)
        return 0
    except OSError:
        print(f'cd: {new_path}: No such file or directory', file=io.stderr)
        return 1


def exit_(args: list[str], shell: Shell, io: IO) -> int:
    raise SystemExit(int(args[0]) if args else 0)


def type_(args: list[str], shell: Shell, io: IO) -> int:
    code = 0
    for arg in args:
        if arg in BUILTINS:
            print(f'{arg} is a shell builtin', file=io.stdout)
        elif path := shutil.which(arg):
            print(f'{arg} is {path}', file=io.stdout)
        else:
            code = 1
            print(f'{arg}: not found', file=io.stderr)
    return code


def history(args: list[str], shell: Shell, io: IO) -> int:
    code = 0
    match args:
        case []:
            for i, item in enumerate(shell.history):
                print(f'{i:>5}  {item}', file=io.stdout)
        case [last] if last.isnumeric():
            length = len(shell.history)
            offset = max(length - int(last), 0)
            for i, item in enumerate(shell.history[offset:], start=offset + 1):
                print(f'{i:>5}  {item}', file=io.stdout)
        case ['-r', path] if Path(path).exists():
            shell.history.read(path)
        case ['-w', path]:
            shell.history.write(path)
        case _:
            code = 1
    return code


def complete(args: list[str], shell: Shell, io: IO) -> int:
    match args:
        case ['-C', path, name]:
            shell.completions[name] = path
            return 0
        case ['-p', name]:
            if (path := shell.completions.get(name)) is None:
                print(f'complete: {name}: no completion specification', file=io.stderr)
                return 1
            print(f"complete -C '{path}' {name}", file=io.stdout)
            return 0
        case ['-r', name]:
            shell.completions.pop(name, None)
            return 0
        case _:
            print('complete: usage: complete [-C command] [-p] [-r] [name]', file=io.stderr)
            return 2

BUILTINS = {
    'echo': echo, 'cd': cd, 'pwd': pwd, 
    'type': type_, 'exit': exit_, 'complete': complete, 
    'jobs': jobs, 'history': history
}
