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
        """Sélectionne l’opération ayant le plus petit temps de traitement.

        Args:
            ready_operations: Liste des opérations disponibles à l’instant courant.
            jobs: Contexte global des jobs (non utilisé ici).
            machines: Contexte global des machines (non utilisé ici).
            current_time: Temps courant de simulation (non utilisé ici).

        Returns:
            L’opération avec le plus petit ``processing_time``.

        Note:
            En cas d’égalité, la sélection est déterministe via
            (job_id, op_index) afin d’éviter des résultats non reproductibles.
        """
        return min(
            ready_operations,
            key=lambda op: (op.processing_time, op.job_id, op.op_index),
        )