"""Ordonnanceur glouton (greedy dispatching) pour le JSSP.

La classe Scheduler exécute une simulation pas à pas :
à chaque instant, elle collecte les opérations prêtes à être exécutées
et délègue la décision de sélection à une heuristique injectée.

Contraintes respectées :
- Une machine ne peut exécuter qu’une seule opération à la fois.
- Les opérations d’un même job doivent être exécutées dans l’ordre.
"""

from __future__ import annotations

import copy
from typing import List, Optional

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.operation import Operation
from simulator.event import Event


class Scheduler:
    """Moteur d’ordonnancement glouton pilotant la simulation.

    Le scheduler maintient une horloge globale (clock) et sélectionne
    itérativement les opérations exécutables via une heuristique.
    Lorsque aucune opération n’est disponible, il avance le temps.

    Args:
        heuristic: Instance d’une heuristique (BaseHeuristic).
    """

    def __init__(self, heuristic: BaseHeuristic) -> None:
        self.heuristic: BaseHeuristic = heuristic
        self.events: List[Event] = []

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def run(self, jobs: List[Job], machines: List[Machine]) -> List[Event]:
        """Exécute la simulation et retourne la liste des événements.

        Cette méthode modifie directement les objets jobs et machines :
        chaque opération obtient un start_time et un finish_time.

        Args:
            jobs: Liste des jobs à ordonnancer.
            machines: Liste des machines disponibles.

        Returns:
            Liste chronologique des événements de planification.
        """
        self.events = []
        machine_map = {m.machine_id: m for m in machines}
        clock: int = 0

        while not self._all_done(jobs):
            ready = self._collect_ready(jobs, machine_map, clock)

            if not ready:
                # Avancer l’horloge jusqu’au prochain événement pertinent
                clock = self._next_interesting_time(jobs, machine_map, clock)
                continue

            chosen: Operation = self.heuristic.select_operation(
                ready, jobs, machines, clock
            )

            machine = machine_map[chosen.machine_id]

            start = machine.earliest_start_for(
                self._job_ready_time(chosen, jobs)
            )

            machine.assign(chosen, start)
            self.events.append(Event.from_operation(chosen))

        self.events.sort(key=lambda e: (e.time, e.machine_id))
        return self.events

    # ------------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------------

    def _all_done(self, jobs: List[Job]) -> bool:
        """Retourne True si toutes les opérations de tous les jobs sont terminées."""
        return all(job.is_complete for job in jobs)

    def _job_ready_time(self, operation: Operation, jobs: List[Job]) -> int:
        """Retourne le temps minimal imposé par la contrainte de précédence du job."""
        job = jobs[operation.job_id]

        if operation.op_index == 0:
            return 0

        predecessor = job.operations[operation.op_index - 1]

        return predecessor.finish_time if predecessor.is_scheduled else 0

    def _collect_ready(
        self,
        jobs: List[Job],
        machine_map: dict,
        clock: int,
    ) -> List[Operation]:
        """Collecte toutes les opérations pouvant être exécutées à l’instant *clock*.

        Une opération est considérée prête si :
        1. Son opération précédente dans le job est terminée.
        2. La machine correspondante est disponible.
        3. Les contraintes temporelles sont satisfaites.
        """
        ready: List[Operation] = []

        for job in jobs:
            next_op: Optional[Operation] = job.next_operation()
            if next_op is None:
                continue

            machine = machine_map[next_op.machine_id]

            job_ready = self._job_ready_time(next_op, jobs)
            machine_ready = machine.available_at

            if max(job_ready, machine_ready) <= clock:
                ready.append(next_op)

        return ready

    def _next_interesting_time(
        self,
        jobs: List[Job],
        machine_map: dict,
        clock: int,
    ) -> int:
        """Calcule le prochain instant où une opération pourra être planifiée.

        On considère :
        - les disponibilités futures des machines
        - les fins des opérations précédentes dans les jobs
        """
        candidates: List[int] = []

        for job in jobs:
            next_op = job.next_operation()
            if next_op is None:
                continue

            machine = machine_map[next_op.machine_id]

            candidates.append(machine.available_at)

            job_ready = self._job_ready_time(next_op, jobs)
            if job_ready > clock:
                candidates.append(job_ready)

        future = [t for t in candidates if t > clock]

        return min(future) if future else clock + 1