

from dataclasses import dataclass, field
import os
from typing import Protocol


class Process(Protocol):
    pid: int
    def poll(self) -> int | None: ...
    def wait(self) -> int: ...


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


    def wait(self) -> int:
        if self.returncode is None:
            _, status = os.waitpid(self.pid, 0)
            self.returncode = os.waitstatus_to_exitcode(status)
        return self.returncode


@dataclass(frozen=True)
class Job:
    id: int
    procs: list[Process]
    cmdline: str

    @property
    def status(self):
        codes = [p.poll() for p in self.procs]
        if any(c is None for c in codes):
            return 'Running'
        return 'Done' if codes[-1] == 0 else f'Exit {codes[-1]}'


@dataclass
class JobTable:
    _jobs: dict[int, Job] = field(default_factory=dict)

    def add(self, procs: list[Process], cmdline: str) -> Job:
        job = Job(max(self._jobs, default=0) + 1, procs, cmdline)
        self._jobs[job.id] = job
        return job

    def __iter__(self):
        return iter(self._jobs.values())

    def reap(self) -> None:
        finished = [
            job for job 
            in self._jobs.values() 
            if job.status != 'Running'
        ]
        for job in finished:
            del self._jobs[job.id]
        return None

    def _marker(self, job_id: int) -> str:
        ids = list(self._jobs)
        if ids and job_id == ids[-1]: return '+'
        if len(ids) > 1 and job_id == ids[-2]: return '-'
        return ' '

    def format(self, job: Job) -> str:
        text = (
            job.cmdline 
            if job.status == 'Running'
            else job.cmdline.rstrip().removesuffix('&').rstrip()
        )
        return f'[{job.id}]{self._marker(job.id)}  {job.status:<24}{text}'