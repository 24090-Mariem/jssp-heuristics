"""Point d’entrée principal du framework de simulation JSSP.

Utilisation
-----------
Exécution simple (LA01 + FIFO + affichage Gantt) :

    python main.py

Choisir une instance et une heuristique :

    python main.py --dataset la05 --heuristic SPT

Exécuter tout le benchmark :

    python main.py --benchmark

Exporter un Gantt sans affichage :

    python main.py --dataset la03 --heuristic LPT --save-gantt outputs/gantt.png --no-show

Exporter un CSV :

    python main.py --dataset la01 --heuristic FIFO --save-csv outputs/la01_fifo.csv
"""

from __future__ import annotations

import argparse
import os
import sys

# ---------------------------------------------------------------------------
# Ajout du répertoire racine au PYTHONPATH (import stable)
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from benchmark import Benchmark
from heuristics import ALL_HEURISTICS, FIFOHeuristic, LPTHeuristic, SPTHeuristic
from parser import JSSPParser
from simulator.simulator import Simulator
from visualization.charts import (
    plot_makespan_comparison,
    plot_ranking_summary,
    plot_utilisation_comparison,
)
from visualization.gantt import plot_gantt

# ---------------------------------------------------------------------------
# Constantes globales
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(_ROOT, "data")
OUTPUTS_DIR = os.path.join(_ROOT, "outputs")

# Mapping CLI → classes d’heuristiques
_HEURISTIC_MAP = {
    "FIFO": FIFOHeuristic,
    "SPT": SPTHeuristic,
    "LPT": LPTHeuristic,
}


# ---------------------------------------------------------------------------
# Résolution des heuristiques
# ---------------------------------------------------------------------------

def _resolve_heuristic(name: str):
    """Convertit un nom d’heuristique en classe correspondante.

    Args:
        name: Nom de l’heuristique (insensible à la casse).

    Returns:
        Classe d’heuristique correspondante.

    Raises:
        SystemExit: Si le nom n’est pas reconnu.
    """
    key = name.upper()

    if key not in _HEURISTIC_MAP:
        print(
            f"Heuristique inconnue '{name}'. "
            f"Choix possibles : {', '.join(_HEURISTIC_MAP)}",
            file=sys.stderr,
        )
        sys.exit(1)

    return _HEURISTIC_MAP[key]


# ---------------------------------------------------------------------------
# Mode simulation unique
# ---------------------------------------------------------------------------

def run_single(args: argparse.Namespace) -> None:
    """Exécute une simulation unique (une instance + une heuristique)."""
    dataset = args.dataset.lower()
    filepath = os.path.join(DATA_DIR, f"{dataset}.txt")

    if not os.path.isfile(filepath):
        print(f"Erreur : fichier introuvable : {filepath}", file=sys.stderr)
        sys.exit(1)

    heuristic_cls = _resolve_heuristic(args.heuristic)
    heuristic = heuristic_cls()

    print(f"\n{'='*60}")
    print(f" Simulation JSSP")
    print(f" Instance  : {dataset}")
    print(f" Heuristique : {heuristic.name}")
    print(f"{'='*60}\n")

    simulator = Simulator()
    schedule = simulator.run(filepath, heuristic, instance_name=dataset)

    print(schedule.summary())
    print(f"  Makespan (Cmax)     : {schedule.makespan}")
    print(f"  Utilisation moyenne : {schedule.average_utilisation:.2%}")
    print()

    for mid, util in sorted(schedule.machine_utilisations.items()):
        print(f"    Machine {mid:2d} : {util:.2%}")

    # Export CSV
    if args.save_csv:
        os.makedirs(os.path.dirname(args.save_csv) or ".", exist_ok=True)
        schedule.save_csv(args.save_csv)
        print(f"\nCSV exporté vers : {args.save_csv}")

    # Gantt chart
    if args.save_gantt or not args.no_show:
        plot_gantt(
            schedule,
            save_path=args.save_gantt,
            show=not args.no_show,
        )


# ---------------------------------------------------------------------------
# Mode benchmark complet
# ---------------------------------------------------------------------------

def run_benchmark(args: argparse.Namespace) -> None:
    """Exécute le benchmark complet (toutes instances × heuristiques)."""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    print(f"\n{'='*60}")
    print(f" Benchmark JSSP — Toutes instances × heuristiques")
    print(f"{'='*60}\n")

    bench = Benchmark(data_dir=DATA_DIR)
    results = bench.run_all(verbose=True)

    bench.print_summary(results)

    # Export CSV
    csv_path = args.save_csv or os.path.join(OUTPUTS_DIR, "benchmark.csv")
    bench.export_csv(results, csv_path)

    # Graphiques
    show = not args.no_show

    plot_makespan_comparison(
        results,
        save_path=os.path.join(OUTPUTS_DIR, "makespan_comparison.png"),
        show=show,
    )

    plot_utilisation_comparison(
        results,
        save_path=os.path.join(OUTPUTS_DIR, "utilisation_comparison.png"),
        show=show,
    )

    plot_ranking_summary(
        results,
        save_path=os.path.join(OUTPUTS_DIR, "ranking_summary.png"),
        show=show,
    )

    print(f"\nGraphiques sauvegardés dans : {OUTPUTS_DIR}/")


# ---------------------------------------------------------------------------
# Interface CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construit le parser des arguments CLI."""
    parser = argparse.ArgumentParser(
        description="Framework JSSP — simulation d’heuristiques sur benchmarks LA.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="la01",
        metavar="NAME",
        help="Instance LA (ex: la01) — défaut: la01",
    )

    parser.add_argument(
        "--heuristic",
        type=str,
        default="FIFO",
        choices=list(_HEURISTIC_MAP.keys()),
        help="Heuristique de scheduling (défaut: FIFO)",
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Lance le benchmark complet (toutes heuristiques × instances)",
    )

    parser.add_argument(
        "--save-gantt",
        type=str,
        default=None,
        metavar="PATH",
        help="Sauvegarde du diagramme de Gantt",
    )

    parser.add_argument(
        "--save-csv",
        type=str,
        default=None,
        metavar="PATH",
        help="Sauvegarde des résultats en CSV",
    )

    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Désactive l’affichage graphique (mode headless/CI)",
    )

    return parser


def main() -> None:
    """Point d’entrée principal du programme."""
    cli = build_parser()
    args = cli.parse_args()

    if args.benchmark:
        run_benchmark(args)
    else:
        run_single(args)


if __name__ == "__main__":
    main()