
from dataclasses import dataclass, field
from functools import cache
import os
import shutil
from typing import NamedTuple, TextIO


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

def echo(args: list[str], shell: Shell, io: IO) -> int:
    print(*args, file=io.stdout)
    return 0


def pwd(args: list[str], shell: Shell, io: IO) -> int:
    print(os.getcwd(), file=io.stdout)
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


def jobs(args: list[str], shell: Shell, io: IO) -> int:
    pass

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

BUILTINS = {'echo': echo, 'cd': cd, 'pwd': pwd, 'type': type_, 'exit': exit_, 'complete': complete, 'jobs': jobs}
