import os
from pathlib import Path
import sys

from app.commands import ALL_COMMANDS, sys_in, sys_out


def read_command():
    line = sys_in()
    inputs = line.split()
    command = inputs[0]
    return command, line[len(command) + 1:]

def run_main_loop():
    while 1:
        sys_out("$ ", False)
        cmd, args = read_command()
        command_found = False

        for cmd in ALL_COMMANDS:
            if cmd == cmd.name:
                command_found = True
                cmd(args)
                break

        if not command_found:
            sys_out(f'{cmd}: command not found')


def main():
    run_main_loop()

if __name__ == "__main__":
    main()
