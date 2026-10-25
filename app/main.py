import sys

def _out(arg: str, new_line=True):
    sys.stdout.write(arg + ("\n" if new_line else ""))

def _in():
    return sys.stdin.readline().rstrip()

def run_main_loop():
    while 1:
        _out("$ ", False)
        user_input = _in()

        if user_input == 'exit':
            break
        elif user_input == 'echo':
            _out(user_input[5:])
        else:
            _out(f'{user_input}: command not found')


def main():
    run_main_loop()

if __name__ == "__main__":
    main()
