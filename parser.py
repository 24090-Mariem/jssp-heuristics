"""Parseur pour le format standard des benchmarks JSSP (série LA — Lawrence).

Format du fichier
-----------------
Ligne 1 : <n_jobs> <n_machines>

Lignes suivantes :
Chaque ligne représente un job sous forme de paires :
    <machine_id> <processing_time>

Chaque job contient exactement n_machines opérations ordonnées.

Exemple (3 jobs, 2 machines) :

    3 2
    0 5 1 3
    1 4 0 6
    0 2 1 8
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from models.job import Job
from models.machine import Machine
from models.operation import Operation


class JSSPParser:
    """Parse les instances JSSP au format texte de la série LA.

    Utilisation :
        parser = JSSPParser()
        jobs, machines = parser.parse("data/la01.txt")
    """

    def parse(
        self,
        filepath: str,
    ) -> Tuple[List[Job], List[Machine]]:
        """Charge une instance JSSP et retourne les jobs et machines.

        Args:
            filepath: Chemin vers le fichier .txt de benchmark.

        Returns:
            Tuple (jobs, machines) sans information de planification.

        Raises:
            FileNotFoundError: si le fichier n'existe pas.
            ValueError: si le format du fichier est invalide.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Fichier introuvable : {filepath!r}")

        with open(filepath, "r", encoding="utf-8") as fh:
            lines = [
                ln.strip()
                for ln in fh
                if ln.strip() and not ln.strip().startswith("#")
            ]

        if not lines:
            raise ValueError(f"Fichier vide : {filepath!r}")

        # ------------------------------------------------------------------
        # Lecture de l’en-tête
        # ------------------------------------------------------------------
        header = lines[0].split()

        if len(header) < 2:
            raise ValueError(
                f"L’en-tête doit contenir '<n_jobs> <n_machines>', obtenu : {lines[0]!r}"
            )

        n_jobs = int(header[0])
        n_machines = int(header[1])

        data_lines = lines[1:]

        if len(data_lines) < n_jobs:
            raise ValueError(
                f"Nombre de lignes insuffisant : attendu {n_jobs}, trouvé {len(data_lines)}."
            )

        # ------------------------------------------------------------------
        # Création des machines (état initial vide)
        # ------------------------------------------------------------------
        machines: List[Machine] = [Machine(mid) for mid in range(n_machines)]

        # ------------------------------------------------------------------
        # Construction des jobs + opérations
        # ------------------------------------------------------------------
        jobs: List[Job] = []

        for job_id, line in enumerate(data_lines[:n_jobs]):
            tokens = line.split()

            if len(tokens) != n_machines * 2:
                raise ValueError(
                    f"Job {job_id} : attendu {n_machines * 2} valeurs, "
                    f"obtenu {len(tokens)} : {line!r}"
                )

            operations: List[Operation] = []

            for op_index in range(n_machines):
                machine_id = int(tokens[op_index * 2])
                processing_time = int(tokens[op_index * 2 + 1])

                # Validation machine
                if machine_id < 0 or machine_id >= n_machines:
                    raise ValueError(
                        f"Job {job_id}, opération {op_index} : "
                        f"machine_id invalide {machine_id}."
                    )

                # Validation durée
                if processing_time <= 0:
                    raise ValueError(
                        f"Job {job_id}, opération {op_index} : "
                        f"temps de traitement invalide {processing_time}."
                    )

                operations.append(
                    Operation(
                        job_id=job_id,
                        op_index=op_index,
                        machine_id=machine_id,
                        processing_time=processing_time,
                    )
                )

            jobs.append(Job(job_id=job_id, operations=operations))

        return jobs, machines

    def parse_all(
        self,
        directory: str,
        prefix: str = "la",
    ) -> Dict[str, Tuple[List[Job], List[Machine]]]:
        """Charge toutes les instances JSSP d’un répertoire donné.

        Args:
            directory: Dossier contenant les fichiers .txt.
            prefix: Préfixe des fichiers à charger (ex: 'la').

        Returns:
            Dictionnaire :
            {instance_name: (jobs, machines)}.
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Dossier introuvable : {directory!r}")

        results: Dict[str, Tuple[List[Job], List[Machine]]] = {}

        filenames = sorted(
            f for f in os.listdir(directory)
            if f.startswith(prefix) and f.endswith(".txt")
        )

        for filename in filenames:
            name = filename[:-4]  # suppression de .txt
            path = os.path.join(directory, filename)
            results[name] = self.parse(path)

        return results