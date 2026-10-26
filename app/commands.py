from abc import ABC, abstractmethod
import os
from pathlib import Path
import subprocess
import sys

from .helpers import ComamndNotFound, find_command_in_path

class Command(ABC):
    name: str

    @abstractmethod
    def __call__(self, *args, **kwds):
        pass

class CommandEcho(Command):
    name = "echo"

    def __call__(self, args, *, stdout, stderr):
        stdout.write(' '.join(args) + '\n')

class CommandPwd(Command):
    name = "pwd"

    def __call__(self, args, *, stdout, stderr):
        stdout.write(os.getcwd() + '\n')

class CommandCd(Command):
    name = "cd"

    def __call__(self, args, *, stdout, stderr):
        new_dir = args[0]
        home_dir = os.environ.get('HOME')

        try:
            os.chdir(new_dir.replace('~', home_dir))
        except:
            stderr.write(f'{self.name}: {new_dir}: No such file or directory\n')

class CommandExit(Command):
    name = "exit"

    def __call__(self, *args, **kwargs):
        sys.exit(0)

class CommandExec(Command):
    name = "__internal_exec__"

    def __call__(self, args, *, stdout, stderr):
        cmd_path = find_command_in_path(args[0])

        result = subprocess.run(
            args, stdout=stdout, stderr=stderr
        )

class CommandType(Command):
    name = "type"

    def __call__(self, args, *, stdout, stderr):
        cmd = args[0].strip()
        if cmd in BUILTIN_COMMANDS:
            stdout.write(f'{cmd} is a shell builtin\n')
            return
        try:
            cmd_path = find_command_in_path(cmd)
            stdout.write(f'{cmd} is {cmd_path}\n')
        except ComamndNotFound:
            stderr.write(f'{cmd}: not found\n')

ALL_COMMANDS = [CommandExit(), CommandEcho(), CommandType(), CommandPwd(), CommandCd()]
BUILTIN_COMMANDS = {cmd.name: cmd for cmd in ALL_COMMANDS}