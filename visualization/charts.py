"""Graphiques de comparaison pour plusieurs solutions JSSP.

Ce module fournit des visualisations permettant de comparer
les performances des heuristiques sur plusieurs instances,
notamment via le makespan et l’utilisation des machines.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from models.schedule import Schedule


# ---------------------------------------------------------------------------
# Comparaison du makespan
# ---------------------------------------------------------------------------

def plot_makespan_comparison(
    results: Dict[str, Dict[str, Schedule]],
    title: str = "Comparaison du Makespan par Heuristique",
    save_path: Optional[str] = None,
    show: bool = True,
    figsize: tuple = (16, 6),
) -> plt.Figure:
    """Bar chart comparant le makespan entre heuristiques et instances.

    Args:
        results: Dictionnaire imbriqué
                 {instance_name: {heuristic_name: Schedule}}.
        title: Titre du graphique.
        save_path: Chemin de sauvegarde de l’image (optionnel).
        show: Afficher le graphique si True.
        figsize: Taille de la figure matplotlib.

    Returns:
        Figure matplotlib générée.
    """
    instances = sorted(results.keys())
    heuristics = sorted({h for inst in results.values() for h in inst})
    x = np.arange(len(instances))
    width = 0.8 / max(len(heuristics), 1)
    colours = plt.cm.Set2(np.linspace(0, 1, len(heuristics)))

    fig, ax = plt.subplots(figsize=figsize)

    for idx, heuristic in enumerate(heuristics):
        makespans = [
            results[inst].get(heuristic, None)
            for inst in instances
        ]
        values = [s.makespan if s else 0 for s in makespans]
        offset = (idx - len(heuristics) / 2 + 0.5) * width

        bars = ax.bar(
            x + offset,
            values,
            width=width * 0.9,
            label=heuristic,
            color=colours[idx],
            edgecolor="black",
            linewidth=0.5,
        )

        # Ajout des valeurs sur les barres
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.5,
                    str(val),
                    ha="center",
                    va="bottom",
                    fontsize=6,
                    rotation=90,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(instances, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Makespan (Cmax)", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(title="Heuristique", fontsize=9)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()

    return fig


# ---------------------------------------------------------------------------
# Comparaison de l’utilisation des machines
# ---------------------------------------------------------------------------

def plot_utilisation_comparison(
    results: Dict[str, Dict[str, Schedule]],
    title: str = "Utilisation moyenne des machines par heuristique",
    save_path: Optional[str] = None,
    show: bool = True,
    figsize: tuple = (16, 5),
) -> plt.Figure:
    """Courbe comparant l’utilisation moyenne des machines.

    Args:
        results: {instance_name: {heuristic_name: Schedule}}.
        title: Titre du graphique.
        save_path: Chemin de sauvegarde (optionnel).
        show: Afficher le graphique si True.
        figsize: Taille de la figure.

    Returns:
        Figure matplotlib générée.
    """
    instances = sorted(results.keys())
    heuristics = sorted({h for inst in results.values() for h in inst})
    x = np.arange(len(instances))
    colours = plt.cm.Set1(np.linspace(0, 1, len(heuristics)))

    fig, ax = plt.subplots(figsize=figsize)

    for idx, heuristic in enumerate(heuristics):
        utils = []
        for inst in instances:
            sched = results[inst].get(heuristic)
            utils.append(sched.average_utilisation * 100 if sched else 0.0)

        ax.plot(
            x,
            utils,
            marker="o",
            label=heuristic,
            color=colours[idx],
            linewidth=2,
            markersize=5,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(instances, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Utilisation moyenne (%)", fontsize=11)
    ax.set_ylim(0, 105)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.legend(title="Heuristique", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()

    return fig


# ---------------------------------------------------------------------------
# Classement des heuristiques
# ---------------------------------------------------------------------------

def plot_ranking_summary(
    results: Dict[str, Dict[str, Schedule]],
    title: str = "Classement des heuristiques (meilleur Cmax)",
    save_path: Optional[str] = None,
    show: bool = True,
    figsize: tuple = (8, 5),
) -> plt.Figure:
    """Barres horizontales montrant le nombre de victoires par heuristique.

    Une heuristique gagne une instance si elle obtient le plus petit makespan.

    Args:
        results: {instance_name: {heuristic_name: Schedule}}.
        title: Titre du graphique.
        save_path: Chemin de sauvegarde (optionnel).
        show: Afficher le graphique si True.
        figsize: Taille de la figure.

    Returns:
        Figure matplotlib générée.
    """
    heuristics = sorted({h for inst in results.values() for h in inst})
    win_counts: Dict[str, int] = {h: 0 for h in heuristics}

    for inst_results in results.values():
        if not inst_results:
            continue

        best_makespan = min(s.makespan for s in inst_results.values())

        for h, sched in inst_results.items():
            if sched.makespan == best_makespan:
                win_counts[h] += 1

    sorted_heuristics = sorted(
        heuristics,
        key=lambda h: win_counts[h],
        reverse=True,
    )

    counts = [win_counts[h] for h in sorted_heuristics]
    colours = plt.cm.Accent(np.linspace(0.1, 0.9, len(sorted_heuristics)))

    fig, ax = plt.subplots(figsize=figsize)

    bars = ax.barh(
        sorted_heuristics,
        counts,
        color=colours,
        edgecolor="black",
    )

    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_width() + 0.1,
            bar.get_y() + bar.get_height() / 2,
            str(count),
            va="center",
            fontsize=10,
        )

    ax.set_xlabel("Nombre d’instances gagnées (meilleur Cmax)", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlim(0, max(counts) * 1.2 + 1)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()

    return fig