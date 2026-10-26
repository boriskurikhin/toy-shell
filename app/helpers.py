import os
from pathlib import Path

class ComamndNotFound(Exception):
    pass

def find_command_in_path(cmd, access=os.X_OK):
    path = os.environ.get('PATH', '')
    dirs_to_check = [
        d for d in path.split(':') 
        if Path(d).exists() and Path(d).is_dir()
    ]
    for dir in dirs_to_check:
        for file_name in (files_in_dir := os.listdir(dir)):
            full_path = os.path.join(dir, file_name)
            if os.access(full_path, access) and file_name == cmd:
                return full_path
    raise ComamndNotFound