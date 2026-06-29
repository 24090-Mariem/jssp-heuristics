"""First In, First Out (FIFO) scheduling heuristic.

Priority rule: schedule the operation whose job arrived first, i.e.,
the operation with the smallest job_id.  Ties are broken by operation
index within the job, then by machine_id.
"""

from __future__ import annotations

from typing import List

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.operation import Operation


class FIFOHeuristic(BaseHeuristic):
    """First In, First Out — prefer operations belonging to lower-numbered jobs.

    This is the simplest priority rule and serves as a baseline.
    """

    @property
    def name(self) -> str:
        return "FIFO"

    def select_operation(
        self,
        ready_operations: List[Operation],
        jobs: List[Job],
        machines: List[Machine],
        current_time: int,
    ) -> Operation:
        """FIFO محسّن — يختار بناءً على وقت تحرر الـ Job الفعلي.

        Args:
            ready_operations: Eligible operations to choose from.
            jobs: Used to compute job release time.
            machines: Unused — present for interface compatibility.
            current_time: Unused — present for interface compatibility.

        Returns:
            Operation whose job became ready earliest; ties broken by
            ``job_id``, then ``op_index``.
        """
        def fifo_key(op: Operation) -> tuple:
            release_time = jobs[op.job_id].earliest_start()
            return (release_time, op.job_id, op.op_index)

        return min(ready_operations, key=fifo_key)