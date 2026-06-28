"""Modèle de données pour un Job dans le JSSP."""

from __future__ import annotations

from typing import Iterator, List, Optional

from models.operation import Operation


class Job:
    """Représente un job composé d'une séquence ordonnée d'opérations.

    Les opérations doivent être exécutées dans l’ordre :
    une opération i ne peut pas commencer avant la fin de i-1.

    Attributs:
        job_id: Identifiant unique du job.
        operations: Liste ordonnée des opérations.
    """

    def __init__(self, job_id: int, operations: List[Operation]) -> None:
        """Initialise un Job.

        Args:
            job_id: Identifiant unique du job.
            operations: Liste ordonnée d'objets Operation.
        """
        self.job_id: int = job_id
        self.operations: List[Operation] = operations

    # ------------------------------------------------------------------
    # Méthodes de parcours
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Retourne le nombre d'opérations dans le job."""
        return len(self.operations)

    def __iter__(self) -> Iterator[Operation]:
        """Permet d'itérer sur les opérations du job."""
        return iter(self.operations)

    def __getitem__(self, index: int) -> Operation:
        """Accès à une opération par son index."""
        return self.operations[index]

    # ------------------------------------------------------------------
    # Méthodes de requête
    # ------------------------------------------------------------------

    @property
    def n_operations(self) -> int:
        """Nombre total d'opérations dans le job."""
        return len(self.operations)

    @property
    def total_processing_time(self) -> int:
        """Somme des temps de traitement de toutes les opérations."""
        return sum(op.processing_time for op in self.operations)

    @property
    def completion_time(self) -> int:
        """Temps de fin de la dernière opération planifiée (-1 si non planifié)."""
        if not self.operations:
            return -1
        return self.operations[-1].finish_time

    @property
    def is_complete(self) -> bool:
        """Vrai si toutes les opérations sont planifiées."""
        return all(op.is_scheduled for op in self.operations)

    def next_operation(self) -> Optional[Operation]:
        """Retourne la première opération non encore planifiée."""
        for op in self.operations:
            if not op.is_scheduled:
                return op
        return None

    def earliest_start(self) -> int:
        """Retourne le plus tôt moment possible pour commencer la prochaine opération.

        Cela correspond à la fin de la dernière opération planifiée,
        ou 0 si aucune opération n’a encore été planifiée.
        """
        scheduled = [op for op in self.operations if op.is_scheduled]
        if not scheduled:
            return 0
        return max(op.finish_time for op in scheduled)

    def reset(self) -> None:
        """Réinitialise toutes les opérations (non planifiées)."""
        for op in self.operations:
            op.reset()

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Représentation lisible du job."""
        return (
            f"Job(id={self.job_id}, ops={self.n_operations}, "
            f"total_pt={self.total_processing_time})"
        )