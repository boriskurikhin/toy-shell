from contextlib import ExitStack
import sys

from .helpers import get_output_files, read_command
from .commands import ALL_COMMANDS, CommandExec, complete_command

def run_main_loop():
    exec_cmd = CommandExec()

    while 1:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        cmd_name, args = read_command(complete_command)

        if not cmd_name:
            continue

        with ExitStack() as stack:
            stdout, stderr, args = get_output_files(args, stack)

            for cmd in ALL_COMMANDS:
                if cmd_name == cmd.name:
                    cmd(args, stdout=stdout, stderr=stderr)
                    break
            else:
                try:
                    exec_cmd(
                        [cmd_name] + args,
                        stdout=stdout,
                        stderr=stderr
                    )
                except:
                    stderr.write(f'{cmd_name}: command not found\n')

if __name__ == "__main__":
    run_main_loop()
