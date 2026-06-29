"""First In, First Out (FIFO) scheduling heuristic.

Priority rule:
    Select the ready operation belonging to the job that entered the
    system first (smallest job_id).

Tie-breaking:
    1. job_id
    2. operation index
    3. machine_id
"""

from __future__ import annotations

from typing import List

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.operation import Operation


class FIFOHeuristic(BaseHeuristic):
    """Classical First In, First Out (FIFO).

    Jobs are served according to their arrival order.
    In benchmark JSSP instances, where all jobs arrive at time 0,
    the job_id represents the arrival order.
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
        """Select the first arrived job.

        Args:
            ready_operations: Operations eligible for scheduling.
            jobs: Unused (kept for interface compatibility).
            machines: Unused.
            current_time: Unused.

        Returns:
            Selected operation according to FIFO.
        """

        return min(
            ready_operations,
            key=lambda op: (
                op.job_id,
                op.op_index,
                op.machine_id,
            ),
        )