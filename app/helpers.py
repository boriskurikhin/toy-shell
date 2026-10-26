import os
from pathlib import Path
import re
import sys
import contextlib
import termios
import tty

def process_input(autocomplete_fn):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    buffer = []

    try:
        # disables echo
        tty.setcbreak(fd)

        while 1:
            ch = sys.stdin.read(1)
            if ch == '\t':
                line = ''.join(buffer)

                if (tokens := line.split()):
                    prefix = tokens[-1]
                    suffix = autocomplete_fn(prefix)[len(prefix):]

                    if suffix:
                        suffix += ' '

                    buffer.extend(suffix)
                    sys.stdout.write(suffix)
                    sys.stdout.flush()
            elif ch in ('\n', '\r'):
                sys.stdout.write('\n')
                return ''.join(buffer)
            elif ch in ('\x7f', '\b'):
                if buffer:
                    buffer.pop()
                    sys.stdout.write('\b \b')
                sys.stdout.flush()
            elif ch.isprintable():
                buffer.append(ch)
                sys.stdout.write(ch)
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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

def read_command(autocomplete_fn):
    line = process_input(autocomplete_fn)

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

    if not args:
        return None, []

    # TODO: don't check if the quote is closed
    return args[0], args[1:]

def get_output_files(args, stack: contextlib.ExitStack):
    stdout = sys.stdout
    stderr = sys.stderr
    clean_args = []
    arg_index = 0

    while arg_index < len(args):
        arg = args[arg_index]
        if arg in ('>', '1>', '2>', '>>', '1>>', '2>>'):
            if arg_index + 1 >= len(args):
                raise ValueError('Missing arg. target!')

            mode = 'w' if arg in ('>', '1>', '2>') else 'a'
            file = stack.enter_context(open(args[arg_index + 1], mode))
            if arg in ('2>', '2>>'): stderr = file
            else: stdout = file

            arg_index += 2
        else:
            clean_args.append(arg)
            arg_index += 1

    return stdout, stderr, clean_args