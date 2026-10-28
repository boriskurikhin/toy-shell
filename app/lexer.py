
from dataclasses import dataclass
import re
from typing import Literal

@dataclass(frozen=True)
class Token:
    type: Literal["WORD", "OP"]
    text: str


class TokenizationError(Exception):
    pass

OP_REDIRECT_TOKENS = {'>', '1>', '2>', '>>', '1>>', '2>>'}
OP_TOKENS = {*OP_REDIRECT_TOKENS, '&'}
_DOUBLE_QUOTE_PATTERN = re.compile(r'["\\\$\`\n]')
_ANY_CHARACTER_PATTERN = re.compile(r'.')


def _token_type(token: str, token_escaped: bool):
    return 'OP' if (
        not token_escaped
        and token in OP_TOKENS
    ) else 'WORD'


def tokenize(line: str) -> list[Token]:
    tokens: list[Token] = []

    if not line.strip():
        return tokens

    current_token = ""
    token_escaped = False
    in_quote = 0
    in_double_quote = 0
    # for escaping
    esc_target_index = -1
    esc_target_rules: re.Pattern = _ANY_CHARACTER_PATTERN

    def flush() -> None:
        nonlocal current_token, token_escaped
        if current_token or token_escaped:
            tokens.append(
                Token(
                    _token_type(current_token, token_escaped), 
                    current_token
                )
            )
            current_token = ''
            token_escaped = False

    for i, char in enumerate(line):
        if esc_target_index == i:
            if esc_target_rules.match(char):
                current_token += char
            else:
                current_token += f'\\{char}'
        elif char == '"':
            if in_quote:
                current_token += char
            else:
                in_double_quote ^= 1
                token_escaped = True
        elif char == '&':
            if in_quote or in_double_quote:
                current_token += char
            else:
                flush()
                tokens.append(Token('OP', '&'))
        elif char == "'":
            if in_double_quote:
                current_token += char
            else:
                token_escaped = True
                in_quote ^= 1
        elif char.isspace():
            if in_double_quote or in_quote:
                current_token += char
            else:
                flush()
        elif char == '\\':
            if in_quote:
                current_token += char
            else:
                esc_target_rules = (
                    _DOUBLE_QUOTE_PATTERN 
                    if in_double_quote 
                    else _ANY_CHARACTER_PATTERN
                )
                esc_target_index = i + 1
                token_escaped = True
        else:
            current_token += char  

    flush()

    if in_quote or in_double_quote:
        raise TokenizationError("Did not close quotes")

    if esc_target_index >= len(line):
        raise TokenizationError("Hanging backslash")

    return tokens
