from dataclasses import dataclass, field
import os


@dataclass
class History:
    _entries: list[str] = field(default_factory=list)
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

    def read(self, path: str | None):
        if path is None or not os.path.exists(path):
            return

        with open(path, 'r') as hf:
            self._entries.extend(line.rstrip('\n') for line in hf)
            self._appended = len(self)

    def write(self, path: str | None):
        if path is None:
            return

        with open(path, 'w') as hf:
            hf.write('\n'.join(self._entries) + '\n')
            self._appended = len(self)

    def append(self, path: str | None):
        if path is None:
            return

        if self._appended < len(self):
            with open(path, 'a') as hf:
                hf.write('\n'.join(self._entries[self._appended:]) + '\n')
            self._appended = len(self)
