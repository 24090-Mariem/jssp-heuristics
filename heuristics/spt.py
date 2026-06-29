"""Heuristique SPT (Shortest Processing Time) pour JSSP.

Principe :
On privilégie les opérations les plus courtes en premier.
Cette stratégie tend à réduire le temps moyen d’exécution des jobs
(flow time) et peut améliorer le makespan dans certains cas.

Les égalités sont résolues de manière déterministe.
"""

from __future__ import annotations

from typing import List

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.operation import Operation


class SPTHeuristic(BaseHeuristic):
    """Heuristique SPT — priorité aux opérations les plus rapides."""

    @property
    def name(self) -> str:
        """Nom utilisé dans les logs et les benchmarks."""
        return "SPT"

    def select_operation(
        self,
        ready_operations: List[Operation],
        jobs: List[Job],
        machines: List[Machine],
        current_time: int,
    ) -> Operation:
        """SPT محسّن — عند التعادل يختار الـ job الأقرب للانتهاء.

        Args:
            ready_operations: Eligible operations to choose from.
            jobs: Used to compute remaining processing time per job.
            machines: Unused — present for interface compatibility.
            current_time: Unused — present for interface compatibility.

        Returns:
            Operation with smallest ``processing_time``; ties broken by
            remaining job time, then ``job_id``, then ``op_index``.
        """
        def spt_key(op: Operation) -> tuple:
            remaining = sum(
                o.processing_time
                for o in jobs[op.job_id].operations
                if not o.is_scheduled
            )
            return (op.processing_time, remaining, op.job_id, op.op_index)

        return min(ready_operations, key=spt_key)