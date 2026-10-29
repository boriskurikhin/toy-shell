from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class History:
    _entries: list[dict] = field(default_factory=list)

    def add(self, item: str) -> None:
        if item.strip():
            self._entries.append(item)

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def __getitem__(self, key):
        return self._entries[key]

    def read(self, path: Path):
        with open(path, 'r') as hf:
            lines = [line.rstrip('\n') for line in hf.readlines()]
            self._entries.extend(lines)

