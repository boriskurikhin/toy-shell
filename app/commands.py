from abc import ABC, abstractmethod
import functools
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from .helpers import ComamndNotFound, find_command_in_path

class AutoCompleteNode:
    def __init__(self):
        self.words = []
        self.children = {}

class AutoCompleter:
    def __init__(self, options: set[str]):
        self.cmd_root = AutoCompleteNode()
        self.file_roots = {}
        self.dir_hashes = {}
        self._build_trie(self.cmd_root, options)

    def _build_trie(self, root, options: set[str]):
        for option_name in options:
            current_node = root
            for char in option_name:
                if char not in current_node.children:
                    current_node.children[char] = AutoCompleteNode()
                current_node = current_node.children[char]
                current_node.words.append(option_name)

    def complete(self, prefix, is_file_autocomplete):
        if is_file_autocomplete:
            cwd = os.getcwd()
            files = {file for file in os.listdir(cwd)}
            file_hash = hashlib.sha1(functools.reduce(lambda a, b: f'{a}#{b}', files, '').encode()).hexdigest()

            if self.dir_hashes.get(cwd) != file_hash:
                self.file_roots[cwd] = AutoCompleteNode()
                self.dir_hashes[cwd] = file_hash
                self._build_trie(self.file_roots[cwd], files)

            current_node = self.file_roots[cwd]
        else:
            current_node = self.cmd_root

        for c in prefix:
            current_node = current_node.children.get(c, None)
            if not current_node:
                raise ValueError('No results found')
            if len(current_node.words) == 1:
                return [current_node.words[0]], False
        while (
            current_node 
            and len(current_node.words) > 1
            and (keys := list(current_node.children.keys()))
            and len(keys) == 1
            and len(current_node.words) == len(current_node.children[keys[0]].words)
        ):
            current_node = current_node.children[keys[0]]
    
        if not current_node:
            raise ValueError('Not results found')
    
        if len(current_node.words) == 1:
            return current_node.words, False
    
        sorted_words = sorted(current_node.words)
        return sorted_words, len(current_node.children.keys()) == 1

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
BUILTIN_COMMANDS = {c.name: c for c in ALL_COMMANDS}
