"""Heuristique LPT (Longest Processing Time) pour JSSP.

Principe :
On privilégie les opérations les plus longues en premier afin de réduire
les déséquilibres entre machines et améliorer le makespan dans plusieurs cas pratiques.

Les égalités sont résolues de manière déterministe.
"""

from __future__ import annotations

from typing import List

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.operation import Operation


class LPTHeuristic(BaseHeuristic):
    """Heuristique LPT — priorité aux opérations les plus coûteuses en temps."""

    @property
    def name(self) -> str:
        """Nom de l’heuristique utilisé dans les logs et benchmarks."""
        return "LPT"

    def select_operation(
        self,
        ready_operations: List[Operation],
        jobs: List[Job],
        machines: List[Machine],
        current_time: int,
    ) -> Operation:
        """LPT محسّن — عند التعادل يختار الماكينة الأقل ازدحاماً.

        Args:
            ready_operations: Eligible operations to choose from.
            jobs: Unused — present for interface compatibility.
            machines: Used to evaluate current machine load.
            current_time: Unused — present for interface compatibility.

        Returns:
            Operation with largest ``processing_time``; ties broken by
            machine availability, then ``job_id``, then ``op_index``.
        """
        machine_map = {m.machine_id: m for m in machines}

        def lpt_key(op: Operation) -> tuple:
            machine_load = machine_map[op.machine_id].available_at
            return (-op.processing_time, machine_load, op.job_id, op.op_index)

        return min(ready_operations, key=lpt_key)