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
        """Sélectionne l’opération ayant le temps de traitement le plus élevé.

        Args:
            ready_operations: Opérations actuellement disponibles.
            jobs: Contexte global des jobs (non utilisé ici).
            machines: Contexte global des machines (non utilisé ici).
            current_time: Temps courant de la simulation (non utilisé ici).

        Returns:
            L’opération avec le plus grand ``processing_time``.

        Note:
            En cas d’égalité, on privilégie une règle déterministe basée sur
            (job_id, op_index) pour éviter les comportements non reproductibles.
        """
        return max(
            ready_operations,
            key=lambda op: (op.processing_time, -op.job_id, -op.op_index),
        )