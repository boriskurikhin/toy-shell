

import os
import subprocess

from .builtins import BUILTINS, Shell, programs_in_path
from .lexer import TokenizationError, tokenize


def _get_dir_items(dirname: str) -> list[str]:
    try:
        with os.scandir(dirname or '.') as entries:
            return [
                os.path.join(dirname, e.name) + ('/' if e.is_dir() else '')
                for e in entries
            ]
    except OSError:
        return []


def complete(line: str, shell: Shell) -> tuple[str, list[str]]:
    try:
        words = [tok.text for tok in tokenize(line)]
    except TokenizationError:
        return "", []

    if not words:
        return '', []

    is_new_word = line.endswith(' ')
    prefix = '' if is_new_word else words[-1]
    candidates = []

    if words[0] in shell.completions and (is_new_word or len(words) > 1):
        path = shell.completions[words[0]]
        env = dict(os.environ, COMP_LINE=line, COMP_POINT=str(len(line)))
        previous = words[-1] if is_new_word else words[-2]
        proc = subprocess.run(
            [path, words[0], prefix, previous],
            env=env,
            capture_output=True,
            text=True
        )
        candidates = proc.stdout.splitlines()

    elif not is_new_word and len(words) == 1:
        candidates = {*BUILTINS, *programs_in_path()}

    else:
        candidates = _get_dir_items(os.path.dirname(prefix))

    candidates = [c for c in candidates if c.startswith(prefix)]
    return prefix, sorted(candidates)
