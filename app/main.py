from .commands import ALL_COMMANDS, CommandExec, sys_in, sys_out

def read_command():
    line = sys_in()
    inputs = line.split()
    command = inputs[0]
    return command, line[len(command) + 1:]

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


def main():
    run_main_loop()

if __name__ == "__main__":
    main()
