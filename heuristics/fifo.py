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
        """Return the ready operation with the lowest (job_id, op_index).

        Args:
            ready_operations: Eligible operations to choose from.
            jobs: Unused — present for interface compatibility.
            machines: Unused — present for interface compatibility.
            current_time: Unused — present for interface compatibility.

        Returns:
            Operation with the smallest ``job_id``; ties broken by
            ``op_index``, then ``machine_id``.
        """
        return min(
            ready_operations,
            key=lambda op: (op.job_id, op.op_index, op.machine_id),
        )
