

from dataclasses import dataclass, field
import os
from subprocess import Popen
from typing import Protocol


class Process(Protocol):
    pid: int
    def poll(self) -> int | None: ...


class ForkedProcess(Process):
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.returncode: int | None = None

    def poll(self) -> int | None:
        if self.returncode is None:
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid != 0:
                self.returncode = os.waitstatus_to_exitcode(status)
        return self.returncode


@dataclass(frozen=True)
class Job:
    id: int
    proc: Popen
    cmdline: str

    @property
    def status(self):
        code = self.proc.poll()
        if code is None:
            return 'Running'
        return 'Done' if code == 0 else f'Exit {code}'


@dataclass
class JobTable:
    _jobs: dict[int, Job] = field(default_factory=dict)

    def add(self, proc: Popen, cmdline: str) -> Job:
        job = Job(max(self._jobs, default=0) + 1, proc, cmdline)
        self._jobs[job.id] = job
        return job

    def __iter__(self):
        return iter(self._jobs.values())

    def reap(self) -> list[Job]:
        finished = [job for job in self._jobs.values() if job.proc.poll() is not None]
        for job in finished:
            del self._jobs[job.id]
        return finished

    def marker(self, job_id: int) -> str:
        ids = list(self._jobs)
        if ids and job_id == ids[-1]: return '+'
        if len(ids) > 1 and job_id == ids[-2]: return '-'
        return ' '
