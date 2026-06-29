"""
Interface Web Streamlit pour le framework de simulation JSSP.

Lancement :
    streamlit run app.py
"""

import io
import os
import sys

import matplotlib
matplotlib.use("Agg")  # backend non interactif (compatible Streamlit)

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Ajout du répertoire racine au PYTHONPATH
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from benchmark import Benchmark
from heuristics import ALL_HEURISTICS, FIFOHeuristic, LPTHeuristic, SPTHeuristic
from models.schedule import Schedule
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

# Mapping UI → classes d’heuristiques
HEURISTIC_MAP = {
    "FIFO — First In, First Out": FIFOHeuristic,
    "SPT  — Shortest Processing Time": SPTHeuristic,
    "LPT  — Longest Processing Time": LPTHeuristic,
}

# Instances LA disponibles
ALL_INSTANCES = [f"la{i:02d}" for i in range(1, 21)] + ["abs25"]


# ---------------------------------------------------------------------------
# Cache parsing (optimisation Streamlit)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def parse_instance(instance_name: str):
    """Charge une instance JSSP depuis disque."""
    parser = JSSPParser()
    filepath = os.path.join(DATA_DIR, f"{instance_name}.txt")
    return parser.parse(filepath)


def fig_to_bytes(fig: plt.Figure) -> bytes:
    """Convertit une figure matplotlib en bytes PNG (download Streamlit)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return buf.read()


def run_simulation(instance_name: str, heuristic_label: str) -> Schedule:
    """Exécute une simulation JSSP pour une instance et une heuristique."""
    heuristic_cls = HEURISTIC_MAP[heuristic_label]
    heuristic = heuristic_cls()

    jobs, machines = parse_instance(instance_name)

    simulator = Simulator()
    return simulator.run_from_parsed(jobs, machines, heuristic, instance_name)


@st.cache_data(show_spinner=False)
def run_full_benchmark():
    """Exécute le benchmark complet (60 simulations)."""
    bench = Benchmark(data_dir=DATA_DIR)
    results = bench.run_all(verbose=False)

    rows = bench.to_flat_list(results)
    df = pd.DataFrame(rows)

    # conversion lisible pour UI
    df["avg_utilisation"] = (df["avg_utilisation"] * 100).round(2)
    df.columns = ["Instance", "Heuristic", "Makespan", "Avg Utilisation (%)"]

    return df, results


# ---------------------------------------------------------------------------
# Configuration Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="JSSP Simulator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)
tab_sim, tab_bench, tab_ai = st.tabs(
    ["🔬 Simulation unique", "📊 Benchmark complet", "🤖 AI Assistant"]
)
with st.sidebar:
    st.title("⚙️ JSSP Simulator")
    st.caption("Job Shop Scheduling Problem — Framework heuristique")

    st.divider()

    mode = st.radio(
        "Mode d’exécution",
        ["🔬 Simulation unique", "📊 Benchmark complet"],
        index=0,
    )

    st.divider()

    st.markdown("**À propos**")
    st.caption(
        "Simulation du problème JSSP sur les instances LA01–LA20 "
        "avec heuristiques FIFO, SPT et LPT."
    )


# ======================================================================
# MODE 1 — Simulation unique
# ======================================================================
with tab_sim:
 if mode == "🔬 Simulation unique":
    st.title("🔬 Simulation unique")

    col_left, col_right = st.columns([1, 2])

    # ------------------------------------------------------------------
    # Panneau de configuration
    # ------------------------------------------------------------------
    with col_left:
        st.subheader("Configuration")

        instance_name = st.selectbox(
            "Instance (LA)",
            ALL_INSTANCES,
            index=0,
        )

        heuristic_label = st.selectbox(
            "Heuristique",
            list(HEURISTIC_MAP.keys()),
            index=0,
        )

        run_btn = st.button(
            "▶ Lancer la simulation",
            use_container_width=True,
            type="primary",
        )

    # ------------------------------------------------------------------
    # Informations instance
    # ------------------------------------------------------------------
    with col_right:
        jobs_raw, machines_raw = parse_instance(instance_name)

        st.subheader("Informations instance")

        m1, m2, m3 = st.columns(3)
        m1.metric("Jobs", len(jobs_raw))
        m2.metric("Machines", len(machines_raw))
        m3.metric("Opérations totales", sum(len(j) for j in jobs_raw))

    st.divider()

    # ------------------------------------------------------------------
    # Exécution simulation
    # ------------------------------------------------------------------
    if run_btn:
        with st.spinner("Simulation en cours..."):
            schedule = run_simulation(instance_name, heuristic_label)

        st.subheader("📈 Résultats")

        c1, c2, c3 = st.columns(3)
        c1.metric("Makespan (Cmax)", schedule.makespan)
        c2.metric("Utilisation moyenne", f"{schedule.average_utilisation:.1%}")
        c3.metric("Heuristique", heuristic_label.split("—")[0].strip())

        # --------------------------------------------------------------
        # Utilisation machines
        # --------------------------------------------------------------
        st.subheader("Utilisation des machines")

        util_data = [
            {
                "Machine": f"M{mid}",
                "Utilisation (%)": f"{u*100:.1f}%",
                "Temps occupé": m.total_busy_time,
            }
            for (mid, u), m in zip(
                sorted(schedule.machine_utilisations.items()),
                sorted(schedule.machines, key=lambda x: x.machine_id),
            )
        ]

        st.dataframe(pd.DataFrame(util_data), use_container_width=True, hide_index=True)

        # --------------------------------------------------------------
        # Gantt chart
        # --------------------------------------------------------------
        st.subheader("Diagramme de Gantt")

        fig = plot_gantt(schedule, show=False)
        st.pyplot(fig)

        st.download_button(
            "⬇ Télécharger Gantt (PNG)",
            data=fig_to_bytes(fig),
            file_name=f"gantt_{instance_name}.png",
            mime="image/png",
        )

        plt.close("all")

        # --------------------------------------------------------------
        # Détail opérations
        # --------------------------------------------------------------
        with st.expander("Détail des opérations"):
            ops_df = pd.DataFrame([{
                "Job": f"J{op.job_id}",
                "Index": op.op_index,
                "Machine": f"M{op.machine_id}",
                "Durée": op.processing_time,
                "Début": op.start_time,
                "Fin": op.finish_time,
            } for op in schedule.all_operations()])

            st.dataframe(ops_df, use_container_width=True, hide_index=True)

            st.download_button(
                "⬇ Export CSV",
                data=schedule.to_csv().encode("utf-8"),
                file_name=f"schedule_{instance_name}.csv",
                mime="text/csv",
            )


# ======================================================================
# MODE 2 — Benchmark complet
# ======================================================================
 with tab_bench:
    st.title("Benchmark complet")
    st.caption("3 heuristiques × 20 instances = 60 simulations")

    if st.button("▶ Lancer benchmark", type="primary"):
        with st.spinner("Exécution de 60 simulations..."):
            df, results = run_full_benchmark()

        st.success("Benchmark terminé")

        st.divider()

        # --------------------------------------------------------------
        # Tableau résumé
        # --------------------------------------------------------------
        st.subheader("Résultats")

        pivot = df.pivot(index="Instance", columns="Heuristic", values="Makespan")
        pivot["Best"] = pivot.min(axis=1)
        pivot["Best Heuristic"] = pivot.drop(columns="Best").idxmin(axis=1)

        st.dataframe(pivot, use_container_width=True)

        st.download_button(
            "⬇ Télécharger CSV global",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="benchmark_results.csv",
            mime="text/csv",
        )

        st.divider()

        # --------------------------------------------------------------
        # Graphiques
        # --------------------------------------------------------------
        st.subheader("Makespan")
        fig1 = plot_makespan_comparison(results, show=False)
        st.pyplot(fig1)
        st.download_button("⬇ PNG", fig_to_bytes(fig1), "makespan.png", "image/png")
        plt.close("all")

        st.subheader("Utilisation moyenne")
        fig2 = plot_utilisation_comparison(results, show=False)
        st.pyplot(fig2)
        st.download_button("⬇ PNG", fig_to_bytes(fig2), "utilisation.png", "image/png")
        plt.close("all")

        st.subheader("🏆 Ranking heuristiques")
        fig3 = plot_ranking_summary(results, show=False)
        st.pyplot(fig3)
        st.download_button("⬇ PNG", fig_to_bytes(fig3), "ranking.png", "image/png")
        plt.close("all")

        st.divider()

        # --------------------------------------------------------------
        # Gantt viewer interactif
        # --------------------------------------------------------------
        st.subheader("Visualisation Gantt")

        col_a, col_b = st.columns(2)

        with col_a:
            gantt_instance = st.selectbox("Instance", ALL_INSTANCES)

        with col_b:
            gantt_heuristic = st.selectbox("Heuristique", list(HEURISTIC_MAP.keys()))

        if st.button("Afficher Gantt"):
            with st.spinner("Génération..."):
                sched = run_simulation(gantt_instance, gantt_heuristic)

            fig_g = plot_gantt(sched, show=False)
            st.pyplot(fig_g)

            st.download_button(
                "⬇ Télécharger",
                fig_to_bytes(fig_g),
                f"gantt_{gantt_instance}.png",
                "image/png",
            )

            plt.close("all")


