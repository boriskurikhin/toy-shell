
from dataclasses import dataclass
from typing import Optional

from .lexer import OP_TOKENS, Token


_REDIRECTS = {
    '>': (1, False), '1>': (1, False), '2>': (2, False),
    '>>': (1, True), '1>>': (1, True), '2>>': (2, True),
}


class ParsingError(Exception):
    pass


@dataclass(frozen=True)
class Redirect:
    fd: int
    path: str
    append: bool


@dataclass(frozen=True)
class Command:
    argv: list[str]
    redirects: list[Redirect]

    @property
    def name(self):
        return self.argv[0]

def parse(tokens: list[Token]) -> Optional[Command]:
    if not tokens:
        return

    argv: list[str] = []
    redirects: list[Redirect] = []

    in_redirect = False
    current_operation = None

    for token in tokens:
        if token.type == 'OP':
            if token.text in OP_TOKENS:
                if in_redirect:
                    raise ParsingError("Missing argv for operator")
                in_redirect = True
            current_operation = token
        elif in_redirect:
            fd, is_append = _REDIRECTS[current_operation.text]
            redirects.append(Redirect(fd, token.text, is_append))
            in_redirect = False
        else:
            argv.append(token.text)

    if not argv:
        raise ParsingError('Empty argv not allowed')

    if in_redirect:
        raise ParsingError('Redirect missing target')

    return Command(argv, redirects)

