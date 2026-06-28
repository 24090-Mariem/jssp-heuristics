"""Modèle de données pour une opération dans le JSSP."""

from dataclasses import dataclass, field


@dataclass
class Operation:
    """Représente une opération unique dans un job.

    Chaque opération doit être exécutée sur une machine spécifique
    pendant une durée donnée.

    Attributs:
        job_id: Identifiant du job parent (indexé à partir de 0).
        op_index: Position de l’opération dans le job (indexé à partir de 0).
        machine_id: Identifiant de la machine requise.
        processing_time: Durée nécessaire pour exécuter l’opération.
        start_time: Temps de début planifié (défini après scheduling).
        finish_time: Temps de fin planifié (défini après scheduling).
    """

    job_id: int
    op_index: int
    machine_id: int
    processing_time: int
    start_time: int = field(default=-1)
    finish_time: int = field(default=-1)

    # ------------------------------------------------------------------
    # Propriétés
    # ------------------------------------------------------------------

    @property
    def is_scheduled(self) -> bool:
        """Retourne True si l’opération a été planifiée."""
        return self.start_time >= 0

    @property
    def duration(self) -> int:
        """Alias du temps de traitement (processing_time)."""
        return self.processing_time

    # ------------------------------------------------------------------
    # Méthodes de planification
    # ------------------------------------------------------------------

    def schedule(self, start: int) -> None:
        """Assigne un temps de début et calcule le temps de fin.

        Args:
            start: Temps de début de l’opération.

        Raises:
            ValueError: Si le temps de début est négatif.
        """
        if start < 0:
            raise ValueError(f"Le temps de début doit être positif, reçu {start}.")
        self.start_time = start
        self.finish_time = start + self.processing_time

    def reset(self) -> None:
        """Réinitialise l’opération (non planifiée)."""
        self.start_time = -1
        self.finish_time = -1

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Représentation lisible de l’opération."""
        return (
            f"Operation(job={self.job_id}, idx={self.op_index}, "
            f"machine={self.machine_id}, pt={self.processing_time}, "
            f"start={self.start_time}, finish={self.finish_time})"
        )