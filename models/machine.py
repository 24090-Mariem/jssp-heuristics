"""Modèle de données pour une machine dans le JSSP."""

from __future__ import annotations

from typing import List, Tuple

from models.operation import Operation


class Machine:
    """Représente une machine qui exécute les opérations une par une.

    Attributs:
        machine_id: Identifiant unique de la machine.
        schedule: Liste ordonnée de tuples (start_time, operation)
                  représentant la timeline de la machine.
    """

    def __init__(self, machine_id: int) -> None:
        """Initialise une Machine.

        Args:
            machine_id: Identifiant unique entier de la machine.
        """
        self.machine_id: int = machine_id
        self.schedule: List[Tuple[int, Operation]] = []

    # ------------------------------------------------------------------
    # Interface de planification
    # ------------------------------------------------------------------

    @property
    def available_at(self) -> int:
        """Retourne le moment où la machine devient libre.

        Retourne 0 si aucune opération n’a encore été assignée.
        """
        if not self.schedule:
            return 0
        return max(op.finish_time for _, op in self.schedule)

    def earliest_start_for(self, ready_time: int) -> int:
        """Retourne le plus tôt moment possible pour démarrer une opération.

        Ce temps est le maximum entre :
        - la disponibilité de la machine
        - le temps de fin de l’opération précédente (ready_time)

        Args:
            ready_time: Moment où l’opération devient prête.

        Returns:
            Le temps de début valide le plus tôt.
        """
        return max(self.available_at, ready_time)

    def assign(self, operation: Operation, start: int) -> None:
        """Assigne une opération à la machine à partir d’un temps donné.

        Args:
            operation: L’opération à planifier.
            start: Temps de début (doit être >= available_at).

        Raises:
            ValueError: Si le temps de début est avant la disponibilité de la machine.
        """
        if start < self.available_at:
            raise ValueError(
                f"Machine {self.machine_id} occupée jusqu'à {self.available_at}; "
                f"démarrage impossible à {start}."
            )
        operation.schedule(start)
        self.schedule.append((start, operation))

    def reset(self) -> None:
        """Réinitialise le planning de la machine."""
        self.schedule.clear()

    # ------------------------------------------------------------------
    # Métriques d’utilisation
    # ------------------------------------------------------------------

    @property
    def total_busy_time(self) -> int:
        """Somme des temps de traitement des opérations affectées à la machine."""
        return sum(op.processing_time for _, op in self.schedule)

    def utilisation(self, makespan: int) -> float:
        """Calcule le taux d’utilisation de la machine sur la durée totale.

        Args:
            makespan: Durée totale du planning (Cmax).

        Returns:
            Un float entre 0.0 et 1.0.
            Retourne 0.0 si makespan vaut 0.
        """
        if makespan == 0:
            return 0.0
        return self.total_busy_time / makespan

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Représentation lisible de la machine."""
        return (
            f"Machine(id={self.machine_id}, "
            f"ops={len(self.schedule)}, "
            f"available_at={self.available_at})"
        )