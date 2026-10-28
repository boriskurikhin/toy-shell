

from contextlib import contextmanager
import os
import sys
import termios
import tty
from typing import Callable

from .builtins import Shell


Completer = Callable[[str, Shell], tuple[str, list[str]]]

_BELL = '\x07'

@contextmanager
def raw_mode(fd: int):
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_line(completer: Completer, prompt: str = '$ ') -> str:
    with raw_mode(sys.stdin.fileno()):
        print(prompt, end='', flush=True)

        tab_pressed = False
        buffer = []

        def write(s: str) -> None:
            print(s, end='', flush=True)


        def insert(s: str) -> None:
            buffer.extend(s)
            write(s)


        while True:
            char = sys.stdin.read(1)
            match char:
                case '\n' | '\r':
                    print('')
                    return ''.join(buffer)
                case '\x7f' | '\b':
                    if buffer:
                        buffer.pop()
                        write('\b \b')
                    tab_pressed = False
                case char if char.isprintable():
                    insert(char)
                    tab_pressed = False
                case '\t':
                    prefix, matches = completer(''.join(buffer))
                    if not matches:
                        write(_BELL)
                    elif len(matches) == 1:
                        suffix = (
                            matches[0][len(prefix):] + 
                            ('' if matches[0].endswith('/') else ' ')
                        )
                        insert(suffix)
                        tab_pressed = False
                    elif (common := os.path.commonprefix(matches)) != prefix:
                        insert(common[len(prefix):])
                        tab_pressed = True
                    elif not tab_pressed:
                        write(_BELL)
                        tab_pressed = True
                    else:
                        write("\n" + " ".join(matches) + "\n" + prompt + ''.join(buffer))
                case _:
                    # TODO: more cases
                    continue
