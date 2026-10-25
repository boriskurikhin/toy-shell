import os
from pathlib import Path
import sys

def sys_out(arg: str, new_line=True):
    sys.stdout.write(arg + ("\n" if new_line else ""))
    sys.stdout.flush()

def sys_in():
    return sys.stdin.readline().strip()

__BULTIN_COMAMNDS = {"echo", "exit", "type"}

class Command:
    def __int__(self, name: str, function):
        self.name = name
        self.function = function

    def __call__(self, *args, **kwds):
        self.function(args, kwds)

class CommandEcho(Command):
    def __int__(self, name, function):
        return super().__int__("echo", self.fn)

    def fn(self, echo_string):
        sys_out(echo_string)

class CommandExit(Command):
    def __int__(self, name, function):
        sys_exit = lambda: sys.exit(0)
        return super().__int__('exit', sys_exit)

class CommandType(Command):
    def __int__(self, name, function):
        return super().__int__("type", self.fn)

    def _find_in_path(cmd):
        path = os.environ.get('PATH', '')
        dirs_to_check = path.split(':')
        dirs_to_check = [
            d for d in dirs_to_check 
            if Path(d).exists() and Path(d).is_dir()
        ]
        for dir in dirs_to_check:
            files_in_dir = os.listdir(dir)
            for file_name in files_in_dir:
                full_path = os.path.join(dir, file_name)
                if os.access(full_path, os.X_OK) and file_name == cmd:
                    return full_path

    def fn(self, cmd):
        cmd_trimmed = cmd.strip()
        if cmd in __BULTIN_COMAMNDS:
            sys_out(f'{cmd} is a shell builtin')
        elif (cmd_path := self._find_in_path(cmd)):
            sys_out(f'{cmd} is {cmd_path}')
        else:
            sys_out(f'{cmd}: not found')

ALL_COMMANDS = [
    CommandExit(),
    CommandEcho(),
    CommandType()
]