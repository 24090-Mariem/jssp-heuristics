"""Module de benchmark — exécute toutes les heuristiques sur les instances LA.

Utilisation :

    from benchmark import Benchmark
    bench = Benchmark(data_dir="data")
    results = bench.run_all()
    bench.print_summary(results)
    bench.export_csv(results, "outputs/benchmark.csv")
"""

from __future__ import annotations

import csv
import os
import time
from typing import Dict, List, Optional, Tuple, Type

from heuristics import ALL_HEURISTICS, BaseHeuristic
from models.job import Job
from models.machine import Machine
from models.schedule import Schedule
from parser import JSSPParser
from simulator.simulator import Simulator


# Type alias : {instance_name: {heuristic_name: Schedule}}
BenchmarkResults = Dict[str, Dict[str, Schedule]]


class Benchmark:
    """Exécute toutes les heuristiques sur toutes les instances LA disponibles.

    Args:
        data_dir: Répertoire contenant les fichiers ``la01.txt`` … ``la20.txt``.
        heuristic_classes: Liste des classes d’heuristiques à tester.
                           Par défaut : ALL_HEURISTICS.
    """

    def __init__(
        self,
        data_dir: str = "data",
        heuristic_classes: Optional[List[Type[BaseHeuristic]]] = None,
    ) -> None:
        self.data_dir: str = data_dir
        self.heuristic_classes: List[Type[BaseHeuristic]] = (
            heuristic_classes or list(ALL_HEURISTICS)
        )
        self._parser: JSSPParser = JSSPParser()
        self._simulator: Simulator = Simulator(self._parser)

    # ------------------------------------------------------------------
    # Point d’entrée principal
    # ------------------------------------------------------------------

    def run_all(self, verbose: bool = True) -> BenchmarkResults:
        """Exécute toutes les heuristiques sur toutes les instances.

        Args:
            verbose: Affiche la progression si True.

        Returns:
            Dictionnaire imbriqué :
            {instance_name: {heuristic_name: Schedule}}.
        """
        instances = self._load_instances()

        if not instances:
            raise FileNotFoundError(
                f"Aucune instance LA trouvée dans '{self.data_dir}'. "
                "Exécutez d'abord data/generate_la.py."
            )

        results: BenchmarkResults = {}

        for instance_name, (jobs, machines) in sorted(instances.items()):
            results[instance_name] = {}

            for heuristic_cls in self.heuristic_classes:
                heuristic = heuristic_cls()

                t0 = time.perf_counter()

                schedule = self._simulator.run_from_parsed(
                    jobs, machines, heuristic, instance_name
                )

                elapsed = time.perf_counter() - t0

                results[instance_name][heuristic.name] = schedule

                if verbose:
                    print(
                        f"  {instance_name:6s} | {heuristic.name:6s} | "
                        f"Cmax={schedule.makespan:5d} | "
                        f"util={schedule.average_utilisation:.1%} | "
                        f"{elapsed*1000:.1f}ms"
                    )

        return results

    # ------------------------------------------------------------------
    # Rapport texte
    # ------------------------------------------------------------------

    def print_summary(self, results: BenchmarkResults) -> None:
        """Affiche un tableau récapitulatif des résultats.

        Args:
            results: Résultat de :meth:`run_all`.
        """
        heuristics = sorted({h for inst in results.values() for h in inst})

        header = f"{'Instance':8s}" + "".join(f"  {h:>10s}" for h in heuristics)
        sep = "-" * len(header)

        print("\n" + sep)
        print("RÉSUMÉ DU BENCHMARK — Makespan (Cmax)")
        print(sep)
        print(header)
        print(sep)

        for inst in sorted(results.keys()):
            row = f"{inst:8s}"

            best = min(
                results[inst][h].makespan
                for h in heuristics
                if h in results[inst]
            )

            for h in heuristics:
                sched = results[inst].get(h)
                val = sched.makespan if sched else "-"
                marker = " *" if isinstance(val, int) and val == best else "  "
                row += f"{marker}{str(val):>8s}"

            print(row)

        print(sep)
        print("* = meilleur Cmax (plus faible) pour cette instance")
        print(sep + "\n")

    # ------------------------------------------------------------------
    # Export CSV
    # ------------------------------------------------------------------

    def export_csv(
        self,
        results: BenchmarkResults,
        path: str = "outputs/benchmark.csv",
    ) -> None:
        """Exporte tous les résultats dans un fichier CSV.

        Args:
            results: Résultat de :meth:`run_all`.
            path: Chemin de sortie du fichier CSV.
        """
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        fieldnames = ["instance", "heuristic", "makespan", "avg_utilisation"]

        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()

            for inst in sorted(results.keys()):
                for heuristic_name, sched in sorted(results[inst].items()):
                    writer.writerow({
                        "instance": inst,
                        "heuristic": heuristic_name,
                        "makespan": sched.makespan,
                        "avg_utilisation": round(sched.average_utilisation, 4),
                    })

        print(f"Fichier CSV de benchmark enregistré : {path}")

    # ------------------------------------------------------------------
    # Format plat
    # ------------------------------------------------------------------

    def to_flat_list(
        self,
        results: BenchmarkResults,
    ) -> List[Dict]:
        """Convertit les résultats en liste plate de dictionnaires.

        Args:
            results: Résultat de :meth:`run_all`.

        Returns:
            Liste de dictionnaires :
            {instance, heuristic, makespan, avg_utilisation}.
        """
        rows = []

        for inst in sorted(results.keys()):
            for heuristic_name, sched in sorted(results[inst].items()):
                rows.append({
                    "instance": inst,
                    "heuristic": heuristic_name,
                    "makespan": sched.makespan,
                    "avg_utilisation": sched.average_utilisation,
                })

        return rows

    # ------------------------------------------------------------------
    # Chargement interne
    # ------------------------------------------------------------------

    def _load_instances(
        self,
    ) -> Dict[str, Tuple[List[Job], List[Machine]]]:
        """Charge toutes les instances LA disponibles dans le dossier."""
        if not os.path.isdir(self.data_dir):
            return {}

        return self._parser.parse_all(self.data_dir, prefix="la")