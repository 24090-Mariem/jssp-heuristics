"""Modèle d'événement discret pour le simulateur JSSP.

Un Event représente une décision de planification :
quelle opération démarre sur quelle machine et à quel instant.

Le simulateur génère un événement par opération planifiée,
et les stocke dans l’ordre chronologique.
"""

from __future__ import annotations

from dataclasses import dataclass

from models.operation import Operation


@dataclass(order=True)
class Event:
    """Représente un événement de planification produit par le simulateur.

    Attributs:
        time: Temps du système (horloge de simulation) auquel l’événement se produit.
        machine_id: Machine sur laquelle l’opération est exécutée.
        job_id: Identifiant du job associé à l’opération.
        op_index: Position de l’opération dans son job.
        processing_time: Durée d’exécution de l’opération.
        finish_time: Temps de fin de l’opération.
    """

    time: int
    machine_id: int
    job_id: int
    op_index: int
    processing_time: int
    finish_time: int

    # ------------------------------------------------------------------
    # Fabrique (Factory)
    # ------------------------------------------------------------------

    @classmethod
    def from_operation(cls, operation: Operation) -> "Event":
        """Crée un Event à partir d’une Operation déjà planifiée.

        Args:
            operation: Une opération dont les champs start_time et finish_time
                       ont déjà été définis.

        Returns:
            Un Event correspondant à la planification de l’opération.

        Raises:
            ValueError: Si l’opération n’a pas encore été planifiée.
        """
        if not operation.is_scheduled:
            raise ValueError(
                f"Opération {operation} non planifiée : impossible de créer un Event."
            )

        return cls(
            time=operation.start_time,
            machine_id=operation.machine_id,
            job_id=operation.job_id,
            op_index=operation.op_index,
            processing_time=operation.processing_time,
            finish_time=operation.finish_time,
        )

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Représentation lisible de l’événement (log simulation)."""
        return (
            f"t={self.time:4d} | M{self.machine_id} | "
            f"J{self.job_id}[{self.op_index}] | "
            f"pt={self.processing_time} | finish={self.finish_time}"
        )