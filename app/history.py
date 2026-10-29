from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class History:
    _entries: list[dict] = field(default_factory=list)
    _appended: int = 0

    def add(self, item: str) -> None:
        if item.strip():
            self._entries.append(item)

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __getitem__(self, key):
        return self._entries[key]

    def read(self, path: str):
        with open(path, 'r') as hf:
            lines = [line.rstrip('\n') for line in hf.readlines()]
            self._entries.extend(lines)

    def write(self, path: str):
        with open(path, 'w') as hf:
            hf.write('\n'.join(self._entries) + '\n')

    def append(self, path: str):
        if self._appended < len(self):
            with open(path, 'a') as hf:
                hf.write('\n'.join(self._entries[self._appended:]) + '\n')
            self._appended = len(self)
