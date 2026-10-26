from .helpers import read_command
from .commands import ALL_COMMANDS, CommandExec, sys_out

def run_main_loop():
    exec_cmd = CommandExec()

    while 1:
        sys_out("$ ", False)
        cmd_name, args = read_command()
        command_found = False

        for cmd in ALL_COMMANDS:
            if cmd_name == cmd.name:
                command_found = True
                cmd(args)
                break

        if command_found:
            continue

        try:
            exec_cmd(cmd_name, args)
        except:
            sys_out(f'{cmd_name}: command not found')

if __name__ == "__main__":
    run_main_loop()
