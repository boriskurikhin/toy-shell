import sys

def run_main_loop():
    while 1:
        sys.stdout.write("$ ")
        user_input = sys.stdin.readline().rstrip()
        if user_input == 'exit':
            break
        sys.stdout.write(f'{user_input}: command not found\n')


def main():
    run_main_loop()

if __name__ == "__main__":
    main()
