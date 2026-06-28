"""Classe abstraite pour toutes les heuristiques de scheduling JSSP.

Ce module définit l’interface standard que toute heuristique doit respecter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from models.job import Job
from models.machine import Machine
from models.operation import Operation


class BaseHeuristic(ABC):
    """Interface commune à toutes les heuristiques de planification.

    Le simulateur appelle :meth:`select_operation` pour choisir,
    à chaque étape, quelle opération doit être exécutée.

    Chaque implémentation définit une règle de priorité différente.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nom court de l’heuristique (ex: 'FIFO', 'SPT', 'LPT')."""

    @abstractmethod
    def select_operation(
        self,
        ready_operations: List[Operation],
        jobs: List[Job],
        machines: List[Machine],
        current_time: int,
    ) -> Operation:
        """Sélectionne la prochaine opération à exécuter.

        Args:
            ready_operations: Liste des opérations disponibles à l’instant t,
                respectant les contraintes de machine et de précédence.
            jobs: Ensemble des jobs (contexte global, lecture seule).
            machines: Ensemble des machines (contexte global, lecture seule).
            current_time: Temps courant de la simulation.

        Returns:
            L’opération choisie pour être planifiée.
        """