"""Génération du diagramme de Gantt pour une solution JSSP.

Ce module produit une visualisation horizontale :
- axe Y : machines
- axe X : temps

Chaque barre représente une opération, colorée selon son job.
"""

from __future__ import annotations

import os
from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import numpy as np

# Backend compatible Streamlit (sans interface graphique native)
import matplotlib
matplotlib.use("Agg")

from models.schedule import Schedule


# ---------------------------------------------------------------------------
# Gestion des couleurs
# ---------------------------------------------------------------------------

def _job_colours(n_jobs: int):
    """Retourne une liste de couleurs distinctes pour chaque job."""
    cmap = cm.get_cmap("tab20" if n_jobs <= 20 else "hsv", n_jobs)
    return [cmap(i) for i in range(n_jobs)]


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def plot_gantt(
    schedule: Schedule,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = True,
    figsize: tuple = (14, 6),
) -> plt.Figure:
    """Génère un diagramme de Gantt pour une solution JSSP.

    Args:
        schedule: Instance de Schedule contenant la solution complète.
        title: Titre personnalisé du graphique (optionnel).
        save_path: Chemin de sauvegarde de l’image (PNG, PDF, SVG).
        show: Affiche le graphique si True.
        figsize: Taille de la figure matplotlib (largeur, hauteur).

    Returns:
        Figure matplotlib générée.
    """
    machines = sorted(schedule.machines, key=lambda m: m.machine_id)
    n_machines = len(machines)
    n_jobs = len(schedule.jobs)
    colours = _job_colours(n_jobs)

    fig, ax = plt.subplots(figsize=figsize)

    # ------------------------------------------------------------------
    # Construction des barres du Gantt
    # ------------------------------------------------------------------
    for row_idx, machine in enumerate(machines):
        for _start, op in machine.schedule:
            bar_start = op.start_time
            bar_width = op.processing_time
            colour = colours[op.job_id]

            ax.barh(
                y=row_idx,
                width=bar_width,
                left=bar_start,
                color=colour,
                edgecolor="black",
                linewidth=0.5,
                height=0.6,
            )

            # Affichage du label si la barre est suffisamment large
            if bar_width >= 3:
                ax.text(
                    bar_start + bar_width / 2,
                    row_idx,
                    f"J{op.job_id}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="white" if _is_dark(colour) else "black",
                    fontweight="bold",
                )

    # ------------------------------------------------------------------
    # Mise en forme des axes
    # ------------------------------------------------------------------
    ax.set_yticks(range(n_machines))
    ax.set_yticklabels([f"M{m.machine_id}" for m in machines])
    ax.set_xlabel("Temps", fontsize=11)
    ax.set_ylabel("Machine", fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, schedule.makespan * 1.02)

    # ------------------------------------------------------------------
    # Titre
    # ------------------------------------------------------------------
    default_title = (
        f"Gantt Chart — {schedule.instance_name} | "
        f"Heuristique: {schedule.heuristic_name} | "
        f"Cmax = {schedule.makespan}"
    )
    ax.set_title(title or default_title, fontsize=12, fontweight="bold")

    # ------------------------------------------------------------------
    # Légende (jobs)
    # ------------------------------------------------------------------
    legend_patches = [
        mpatches.Patch(facecolor=colours[j], edgecolor="black", label=f"Job {j}")
        for j in range(n_jobs)
    ]

    ax.legend(
        handles=legend_patches,
        loc="upper right",
        bbox_to_anchor=(1.15, 1),
        fontsize=8,
        title="Jobs",
        title_fontsize=9,
        ncol=max(1, n_jobs // 10),
    )

    # Ligne verticale du makespan
    ax.axvline(
        schedule.makespan,
        color="red",
        linestyle="--",
        linewidth=1.2,
        label=f"Cmax={schedule.makespan}",
    )

    plt.tight_layout()

    # Sauvegarde du graphique si demandé
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    # Affichage optionnel
    if show:
        plt.show()

    return fig


# ---------------------------------------------------------------------------
# Utilitaire couleur
# ---------------------------------------------------------------------------

def _is_dark(rgba) -> bool:
    """Détermine si une couleur est sombre selon sa luminance."""
    r, g, b = rgba[0], rgba[1], rgba[2]
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < 0.5