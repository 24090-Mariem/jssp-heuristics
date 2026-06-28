"""Orchestrateur principal de simulation pour le JSSP.

La classe Simulator relie le parseur, l’heuristique, le scheduler
et le modèle de solution (Schedule).

Elle constitue le point d’entrée principal pour exécuter une simulation
complète et obtenir un résultat exploitable.
"""

from __future__ import annotations

import copy
from typing import List, Tuple

from heuristics.base import BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.schedule import Schedule
from parser import JSSPParser
from simulator.scheduler import Scheduler


class Simulator:
    """Exécute une simulation JSSP pour une instance donnée et une heuristique.

    Le simulateur travaille toujours sur des copies profondes des données
    (jobs et machines), ce qui permet de réutiliser la même instance
    avec plusieurs heuristiques sans interférence.

    Args:
        parser: Instance du parseur JSSP (partagée ou dédiée).
    """

    def __init__(self, parser: JSSPParser | None = None) -> None:
        self._parser: JSSPParser = parser or JSSPParser()

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def run(
        self,
        filepath: str,
        heuristic: BaseHeuristic,
        instance_name: str = "",
    ) -> Schedule:
        """Parse un fichier d’instance et exécute la simulation.

        Args:
            filepath: Chemin vers le fichier d’instance (.txt).
            heuristic: Heuristique utilisée pour la prise de décision.
            instance_name: Nom optionnel de l’instance (sinon dérivé du fichier).

        Returns:
            Une instance complète de Schedule contenant la solution.
        """
        if not instance_name:
            import os
            instance_name = os.path.splitext(os.path.basename(filepath))[0]

        jobs_orig, machines_orig = self._parser.parse(filepath)
        return self._simulate(jobs_orig, machines_orig, heuristic, instance_name)

    def run_from_parsed(
        self,
        jobs: List[Job],
        machines: List[Machine],
        heuristic: BaseHeuristic,
        instance_name: str,
    ) -> Schedule:
        """Exécute une simulation à partir de données déjà parsées.

        Une copie profonde est effectuée afin de préserver les données
        originales pour des exécutions multiples.

        Args:
            jobs: Liste de jobs (copiée en interne).
            machines: Liste de machines (copiée en interne).
            heuristic: Heuristique de dispatching.
            instance_name: Nom associé au résultat final.

        Returns:
            Une instance complète de Schedule.
        """
        return self._simulate(jobs, machines, heuristic, instance_name)

    # ------------------------------------------------------------------
    # Méthode interne
    # ------------------------------------------------------------------

    def _simulate(
        self,
        jobs: List[Job],
        machines: List[Machine],
        heuristic: BaseHeuristic,
        instance_name: str,
    ) -> Schedule:
        """Cœur de la simulation : copie + exécution + construction du résultat."""
        jobs_copy = copy.deepcopy(jobs)
        machines_copy = copy.deepcopy(machines)

        scheduler = Scheduler(heuristic)
        scheduler.run(jobs_copy, machines_copy)

        return Schedule(
            instance_name=instance_name,
            heuristic_name=heuristic.name,
            jobs=jobs_copy,
            machines=machines_copy,
        )