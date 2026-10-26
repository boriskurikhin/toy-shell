from abc import ABC, abstractmethod
import os
from pathlib import Path
import subprocess
import sys

from .helpers import ComamndNotFound, find_command_in_path

def sys_out(arg: str, new_line=True):
    sys.stdout.write(arg + ("\n" if new_line else ""))
    sys.stdout.flush()

def sys_in():
    return sys.stdin.readline().strip()

class Command(ABC):
    name: str
    @abstractmethod
    def __call__(self, *args, **kwds):
        pass

class CommandEcho(Command):
    name = "echo"
    def __call__(self, to_echo):
        sys_out(to_echo)

class CommandPwd(Command):
    name = "pwd"
    def __call__(self, *args, **kwds):
        sys_out(os.getcwd())

class CommandCd(Command):
    name = "cd"
    def __call__(self, new_dir):
        home_dir = os.environ.get('HOME')
        try:
            os.chdir(new_dir.replace('~', home_dir))
        except:
            sys_out(f'{self.name}: {new_dir}: No such file or directory')
            pass

class CommandExit(Command):
    name = "exit"
    def __call__(self, *args, **kwds):
        sys.exit(0)

class CommandExec(Command):
    name = "__internal_exec__"

    def __call__(self, cmd, args):
        cmd_path = find_command_in_path(cmd)
        result = subprocess.run(
            [cmd] + args.split(),
            stdout=sys.stdout,
            stderr=sys.stderr
        )

class CommandType(Command):
    name = "type"

    def __call__(self, cmd):
        cmd = cmd.strip()
        if cmd in BUILTIN_COMMANDS:
            sys_out(f'{cmd} is a shell builtin')
            return
        try:
            cmd_path = find_command_in_path(cmd)
            sys_out(f'{cmd} is {cmd_path}')
        except ComamndNotFound:
            sys_out(f'{cmd}: not found')

ALL_COMMANDS = [
    CommandExit(),
    CommandEcho(),
    CommandType(),
    CommandPwd(),
    CommandCd()
]

BUILTIN_COMMANDS = {cmd.name: cmd for cmd in ALL_COMMANDS}