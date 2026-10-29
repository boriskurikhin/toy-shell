
from dataclasses import dataclass

from .lexer import OP_REDIRECT_TOKENS, Token


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


@dataclass(frozen=True)
class Pipeline:
    commands: list[Command]
    background: bool = False


def parse(tokens: list[Token]) -> Pipeline | None:
    if not tokens:
        return None

    commands: list[Command] = []
    argv: list[str] = []
    redirects: list[Redirect] = []
    background = False

    in_redirect = False
    current_operation = None
    command_expected = True

    for token in tokens:
        if background:
            raise ParsingError("Background job indicator must be last")
        if token.type == 'OP':
            if in_redirect:
                raise ParsingError(f'Parse error near {token}')
            if token.text in OP_REDIRECT_TOKENS:
                in_redirect = True
                current_operation = token
            elif token.text == "&":         
                background = True
            elif token.text == "|":
                if command_expected:
                    raise ParsingError(f'Parse error near {token}')
                commands.append(Command(argv, redirects))
                argv, redirects = [], []
                command_expected = True
            else:
                raise ParsingError('Unexpected operator!')
        elif in_redirect:
            fd, is_append = _REDIRECTS[current_operation.text]
            redirects.append(Redirect(fd, token.text, is_append))
            in_redirect = False
        else:
            argv.append(token.text)
            command_expected = False

    if command_expected:
        raise ParsingError(f'Parse error near \'|\'')

    if in_redirect:
        raise ParsingError('Redirect missing target')

    commands.append(Command(argv, redirects))
    return Pipeline(commands, background)


