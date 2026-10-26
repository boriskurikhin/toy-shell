import os
from pathlib import Path
import re
import sys

def sys_out(arg: str, new_line=True):
    sys.stdout.write(arg + ("\n" if new_line else ""))
    sys.stdout.flush()

def sys_in():
    return sys.stdin.readline().strip()

class ComamndNotFound(Exception):
    pass

def find_command_in_path(cmd, access=os.X_OK):
    path = os.environ.get('PATH', '')
    dirs_to_check = [
        d for d in path.split(':') 
        if Path(d).exists() and Path(d).is_dir()
    ]
    for dir in dirs_to_check:
        for file_name in (files_in_dir := os.listdir(dir)):
            full_path = os.path.join(dir, file_name)
            if os.access(full_path, access) and file_name == cmd:
                return full_path
    raise ComamndNotFound

def read_command():
    line = sys_in()

    args = []
    current_arg = ""
    in_quote = False
    in_double_quote = False
    N = len(line)

    special_index = float('-inf')
    special_rules = None

    for i in range(N):
        char = line[i]
        if special_index == i:
            if re.match(special_rules, char):
                current_arg += char
            else:
                current_arg += f'\\{char}'
            continue
        if char == '"':
            if in_quote:
                current_arg += char
                continue
            in_double_quote ^= 1
            continue
        if char == "'":
            if in_double_quote:
                current_arg += char
                continue
            in_quote ^= 1
            continue
        if char == ' ':
            if in_double_quote or in_quote:
                current_arg += char
            elif current_arg:
                args.append(current_arg)
                current_arg = ''
            continue
        if char == '\\':
            if in_quote:
                current_arg += char
                continue
            special_rules = r'["\\\$\`\n]' if in_double_quote else r'.'
            special_index = i + 1
            continue

        current_arg += char

    if current_arg:
        args.append(current_arg)

    # TODO: don't check if the quote is closed
    return args[0], args[1:]
