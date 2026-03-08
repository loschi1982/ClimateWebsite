"""
DP-05: Lokaler Datei-Cache für Klimadatensätze.

Speichert abgerufene Rohdaten in data/raw/ und normalisierte
Datensätze in data/processed/ als JSON-Dateien.

Verzeichnisstruktur:
    data/raw/<source>_<variable>_raw_<retrieved_at>.json
    data/processed/<source>_<variable>.json
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Standard-Basispfad (relativ zum backend/-Ordner)
# Kann über Umgebungsvariablen überschrieben werden
_DEFAULT_RAW_PATH = Path(os.getenv("DATA_RAW_PATH", "../data/raw"))
_DEFAULT_PROCESSED_PATH = Path(os.getenv("DATA_PROCESSED_PATH", "../data/processed"))


class DataCache:
    """
    Verwaltet das lokale Zwischenspeichern von Klimadatensätzen.

    Rohdaten (unveränderlich): data/raw/
    Verarbeitete Daten:        data/processed/

    Die Rohdaten werden nach Quelle, Variable und Abrufzeitpunkt benannt,
    sodass mehrere Versionen erhalten bleiben.
    Die verarbeiteten Daten werden bei jedem Abruf überschrieben.
    """

    def __init__(
        self,
        raw_path: Path = _DEFAULT_RAW_PATH,
        processed_path: Path = _DEFAULT_PROCESSED_PATH,
    ):
        """
        Initialisiert den Cache und stellt sicher, dass die Verzeichnisse existieren.

        Args:
            raw_path:       Pfad für Rohdaten-Dateien.
            processed_path: Pfad für verarbeitete Datensätze.
        """
        self.raw_path = raw_path
        self.processed_path = processed_path
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Erstellt die Cache-Verzeichnisse, falls sie noch nicht existieren."""
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def save_raw(self, source: str, variable: str, content: str) -> Path:
        """
        Speichert Rohdaten (als unveränderlichen Text) in data/raw/.

        Dateiname: <source>_<variable>_raw_<YYYYMMDD_HHMMSS>.txt
        Rohdaten werden nie überschrieben – jeder Abruf erzeugt eine neue Datei.

        Args:
            source:   Quellen-ID (z.B. 'nasa').
            variable: Variablenname (z.B. 'temperature').
            content:  Rohdaten als String (CSV-Text).

        Returns:
            Pfad zur gespeicherten Datei.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{source}_{variable}_raw_{timestamp}.txt"
        file_path = self.raw_path / filename
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"[cache] Rohdaten gespeichert: {file_path}")
        return file_path

    def save_processed(self, dataset: dict) -> Path:
        """
        Speichert einen normalisierten Datensatz als JSON in data/processed/.

        Dateiname: <source>_<variable>.json
        Wird bei jedem Abruf überschrieben (neueste Version).

        Args:
            dataset: Dataset-Dict im Plattformformat.

        Returns:
            Pfad zur gespeicherten Datei.
        """
        source = dataset["source"]
        variable = dataset["variable"]
        filename = f"{source}_{variable}.json"
        file_path = self.processed_path / filename
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        logger.info(f"[cache] Verarbeitete Daten gespeichert: {file_path}")
        return file_path

    def load_processed(self, source: str, variable: str) -> dict | None:
        """
        Lädt einen gespeicherten, verarbeiteten Datensatz aus data/processed/.

        Args:
            source:   Quellen-ID (z.B. 'nasa').
            variable: Variablenname (z.B. 'temperature').

        Returns:
            Dataset-Dict, falls vorhanden. None, wenn kein Cache-Eintrag existiert.
        """
        filename = f"{source}_{variable}.json"
        file_path = self.processed_path / filename
        if not file_path.exists():
            logger.debug(f"[cache] Kein Cache-Eintrag für {source}/{variable}.")
            return None
        with file_path.open("r", encoding="utf-8") as f:
            dataset = json.load(f)
        logger.info(f"[cache] Cache geladen: {file_path}")
        return dataset

    def is_cached(self, source: str, variable: str) -> bool:
        """
        Prüft, ob ein verarbeiteter Datensatz im Cache vorhanden ist.

        Args:
            source:   Quellen-ID.
            variable: Variablenname.

        Returns:
            True, wenn ein Cache-Eintrag existiert.
        """
        filename = f"{source}_{variable}.json"
        return (self.processed_path / filename).exists()

    def list_cached(self) -> list[dict]:
        """
        Gibt eine Liste aller gecachten Datensätze zurück.

        Returns:
            Liste von {'source': str, 'variable': str, 'file': str} Dicts.
        """
        entries = []
        for file_path in self.processed_path.glob("*.json"):
            # Dateiname: <source>_<variable>.json
            parts = file_path.stem.split("_", 1)
            if len(parts) == 2:
                entries.append({
                    "source": parts[0],
                    "variable": parts[1],
                    "file": str(file_path),
                })
        return entries