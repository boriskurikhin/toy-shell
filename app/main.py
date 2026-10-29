from contextlib import ExitStack
from functools import partial
import sys

from .auto_complete import complete
from .executor import execute
from .parser import ParsingError, parse
from .lexer import TokenizationError, tokenize
from .terminal import read_line
from .builtins import Shell

def run_main_loop():
    shell = Shell()
    completer = partial(complete, shell=shell)

    while True:
        for job in [j for j in shell.jobs if j.status != 'Running']:
            print(shell.jobs.format(job))

        shell.jobs.reap()

        line = read_line(completer, shell.history)
        shell.history.add(line)

        try:
            tokens = tokenize(line)
            if (pipeline := parse(tokens)):
                execute(pipeline, shell, line)
        except (TokenizationError, ParsingError) as e: 
            print(e, file=sys.stderr)
        except SystemExit:
            break


if __name__ == "__main__":
    run_main_loop()
