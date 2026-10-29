

from contextlib import contextmanager
import os
import sys
import termios
import tty
from typing import Callable, Sequence

from .builtins import Shell


Completer = Callable[[str], tuple[str, list[str]]]

_BELL = '\x07'

@contextmanager
def raw_mode(fd: int):
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def read_line(completer: Completer, history: Sequence[str] = (), prompt: str = '$ ') -> str:
    draft: str | None = None
    cursor = len(history)

    with raw_mode(sys.stdin.fileno()):
        print(prompt, end='', flush=True)

        tab_pressed = False
        buffer = []

        def write(s: str) -> None:
            print(s, end='', flush=True)

        def write_history(s: str) -> None:
            write('\r' + '\x1b[K' + prompt + s)

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
                case '\x1b':
                    suf = sys.stdin.read(2)
                    tab_pressed = False

                    match suf:
                        case '[A':
                            if cursor > 0:
                                cursor -= 1
                                if draft is None:
                                    draft = ''.join(buffer)
                                buffer = list(history[cursor])
                                write_history(''.join(buffer))
                        case '[B':
                            if cursor < len(history):
                                cursor += 1
                                if cursor < len(history):
                                    buffer = list(history[cursor])
                                else:
                                    buffer = list(draft)
                                    draft = None
                                write_history(''.join(buffer))
                case _:
                    continue
