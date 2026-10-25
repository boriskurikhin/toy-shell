import sys

__BULTIN_COMAMNDS = {"echo", "exit", "type"}

def _out(arg: str, new_line=True):
    sys.stdout.write(arg + ("\n" if new_line else ""))
    sys.stdout.flush()

def _in():
    return sys.stdin.readline().strip()

def read_command():
    line = _in()
    inputs = line.split()
    command = inputs[0]
    return command, line[len(command) + 1:]

def run_main_loop():
    while 1:
        _out("$ ", False)
        cmd, args = read_command()

        if cmd == 'exit':
            break
        elif cmd == 'echo':
            _out(args)
        elif cmd == 'type':
            bult_in = args in __BULTIN_COMAMNDS
            _out(
                f'{args} is a shell builtin' 
                if bult_in 
                else f'{args}: not found'
            )
        else:
            _out(f'{cmd}: command not found')


def main():
    run_main_loop()

if __name__ == "__main__":
    main()
