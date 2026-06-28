"""Modèle de données pour un planning (Schedule) — solution complète d’un JSSP."""

from __future__ import annotations

import csv
import io
from typing import Dict, List, Optional

from models.job import Job
from models.machine import Machine
from models.operation import Operation


class Schedule:
    """Solution complète d’une instance JSSP.

    Agrège les jobs et machines après simulation et fournit des métriques
    ainsi que des utilitaires d’export.

    Attributs:
        instance_name: Nom de l’instance (ex: 'la01').
        heuristic_name: Nom de l’heuristique utilisée pour générer le planning.
        jobs: Liste des jobs de l’instance.
        machines: Liste des machines de l’instance.
    """

    def __init__(
        self,
        instance_name: str,
        heuristic_name: str,
        jobs: List[Job],
        machines: List[Machine],
    ) -> None:
        self.instance_name: str = instance_name
        self.heuristic_name: str = heuristic_name
        self.jobs: List[Job] = jobs
        self.machines: List[Machine] = machines

    # ------------------------------------------------------------------
    # Métriques principales
    # ------------------------------------------------------------------

    @property
    def makespan(self) -> int:
        """Cmax — temps de fin de la dernière opération exécutée."""
        finish_times: List[int] = []
        for machine in self.machines:
            for _, op in machine.schedule:
                finish_times.append(op.finish_time)
        return max(finish_times) if finish_times else 0

    @property
    def machine_utilisations(self) -> Dict[int, float]:
        """Retourne un mapping machine_id → taux d’utilisation sur le makespan."""
        cmax = self.makespan
        return {m.machine_id: m.utilisation(cmax) for m in self.machines}

    @property
    def average_utilisation(self) -> float:
        """Taux d’utilisation moyen des machines."""
        utils = list(self.machine_utilisations.values())
        return sum(utils) / len(utils) if utils else 0.0

    # ------------------------------------------------------------------
    # Liste plate des opérations
    # ------------------------------------------------------------------

    def all_operations(self) -> List[Operation]:
        """Retourne toutes les opérations triées par temps de début."""
        ops: List[Operation] = []
        for job in self.jobs:
            ops.extend(job.operations)
        return sorted(ops, key=lambda o: o.start_time)

    # ------------------------------------------------------------------
    # Export des données
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        """Sérialise le planning sous forme de dictionnaire."""
        ops_data = []
        for op in self.all_operations():
            ops_data.append({
                "job_id": op.job_id,
                "op_index": op.op_index,
                "machine_id": op.machine_id,
                "processing_time": op.processing_time,
                "start_time": op.start_time,
                "finish_time": op.finish_time,
            })

        utils = self.machine_utilisations
        machines_data = [
            {
                "machine_id": mid,
                "utilisation": round(u, 4),
            }
            for mid, u in sorted(utils.items())
        ]

        return {
            "instance": self.instance_name,
            "heuristic": self.heuristic_name,
            "makespan": self.makespan,
            "average_utilisation": round(self.average_utilisation, 4),
            "operations": ops_data,
            "machines": machines_data,
        }

    def to_csv(self) -> str:
        """Retourne les opérations sous forme de chaîne CSV."""
        output = io.StringIO()
        fieldnames = [
            "job_id", "op_index", "machine_id",
            "processing_time", "start_time", "finish_time",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for op in self.all_operations():
            writer.writerow({
                "job_id": op.job_id,
                "op_index": op.op_index,
                "machine_id": op.machine_id,
                "processing_time": op.processing_time,
                "start_time": op.start_time,
                "finish_time": op.finish_time,
            })

        return output.getvalue()

    def save_csv(self, path: str) -> None:
        """Enregistre le planning dans un fichier CSV.

        Args:
            path: Chemin du fichier de sortie.
        """
        with open(path, "w", newline="", encoding="utf-8") as fh:
            fh.write(self.to_csv())

    # ------------------------------------------------------------------
    # Résumé
    # ------------------------------------------------------------------

    def summary(self) -> str:
        """Retourne un résumé compact du planning."""
        return (
            f"[{self.heuristic_name}] {self.instance_name} — "
            f"Cmax={self.makespan}, "
            f"avg_util={self.average_utilisation:.2%}"
        )

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Représentation lisible du planning."""
        return (
            f"Schedule(instance={self.instance_name!r}, "
            f"heuristic={self.heuristic_name!r}, "
            f"makespan={self.makespan})"
        )