"""
DP-01: NASA GISS Surface Temperature Analysis (GISTEMP v4) Client.

Ruft die globalen monatlichen Temperaturanomalien ab.
Quelle: https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv
Lizenz: Public Domain
Zitierung: GISTEMP Team, 2024: GISS Surface Temperature Analysis (GISTEMP), version 4.
           NASA Goddard Institute for Space Studies.
"""

import logging
from io import StringIO

import pandas as pd

from .base_client import BaseClient, DatasetDict

logger = logging.getLogger(__name__)

# NASA GISS GISTEMP v4 – Globale Monats-Anomalien
_NASA_URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"

# Monatsspalten in der CSV-Rohdatei
_MONTH_COLS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Kennzeichnung fehlender Werte in der NASA-CSV
_MISSING_VALUE = "***"

# Referenzzeitraum laut NASA-Dokumentation
_REFERENCE_PERIOD = "1951-1980"


class NasaGissClient(BaseClient):
    """
    Client für die NASA GISS GISTEMP v4 Temperaturdaten.

    Gibt monatliche globale Oberflächentemperaturanomalien
    in °C relativ zum Referenzzeitraum 1951–1980 zurück.
    """

    SOURCE_ID = "nasa"
    SOURCE_NAME = "NASA GISS Surface Temperature Analysis (GISTEMP v4)"
    SOURCE_URL = _NASA_URL
    LICENSE = "Public Domain"

    def fetch(self, start: str, end: str) -> DatasetDict:
        """
        Ruft NASA GISS Temperaturdaten ab und filtert auf den gewünschten Zeitraum.

        Args:
            start: Startdatum im Format 'YYYY-MM-DD'.
            end:   Enddatum im Format 'YYYY-MM-DD'.

        Returns:
            Normalisiertes Dataset-Dict mit monatlichen Temperaturanomalien in °C.

        Raises:
            requests.exceptions.RequestException: Bei Netzwerkfehlern.
            ValueError: Wenn die CSV-Struktur unbekannt ist.
        """
        response = self._get(_NASA_URL)
        raw_data = self._parse(response.text)
        filtered = self._filter_by_date(raw_data, start, end)
        logger.info(f"[nasa] {len(filtered)} Datenpunkte nach Filterung ({start} – {end})")
        return self._build_dataset(
            variable="temperature",
            unit="°C",
            data=filtered,
            reference_period=_REFERENCE_PERIOD,
        )

    def _parse(self, csv_text: str) -> list[dict]:
        """
        Parst den CSV-Rohdatei-Text der NASA GISS und gibt normalisierte
        Datenpunkte als Liste zurück.

        Die NASA-CSV hat eine Kopfzeile und nutzt '***' für fehlende Werte.
        Jede Zeile enthält Jahresdaten mit 12 Monatsspalten.

        Args:
            csv_text: Inhalt der heruntergeladenen CSV-Datei als String.

        Returns:
            Liste von {'date': 'YYYY-MM-DD', 'value': float | None} Dicts,
            chronologisch sortiert.
        """
        # Erste Zeile der NASA-CSV ist ein Metadaten-Header → überspringen
        df = pd.read_csv(
            StringIO(csv_text),
            skiprows=1,
            na_values=_MISSING_VALUE,
        )

        # Sicherstellen, dass die erwarteten Spalten vorhanden sind
        missing_cols = [c for c in ["Year"] + _MONTH_COLS if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"[nasa] Unbekannte CSV-Struktur – fehlende Spalten: {missing_cols}"
            )

        records = []
        for _, row in df.iterrows():
            year = int(row["Year"])
            for month_idx, col in enumerate(_MONTH_COLS, start=1):
                raw_val = row.get(col)
                # Fehlende Werte als None übernehmen (keine Interpolation)
                value = None if pd.isna(raw_val) else float(raw_val)
                date_str = f"{year}-{month_idx:02d}-01"
                records.append({"date": date_str, "value": value})

        # Chronologisch sortieren (NASA-CSV ist bereits sortiert, aber zur Sicherheit)
        records.sort(key=lambda r: r["date"])
        return records

    def _filter_by_date(self, records: list[dict], start: str, end: str) -> list[dict]:
        """
        Filtert eine Liste von Datenpunkten auf einen Datumsbereich.

        Args:
            records: Liste von {'date': 'YYYY-MM-DD', 'value': ...} Dicts.
            start:   Startdatum inklusiv (Format 'YYYY-MM-DD').
            end:     Enddatum inklusiv (Format 'YYYY-MM-DD').

        Returns:
            Gefilterte Liste, nur Einträge im Bereich [start, end].
        """
        return [r for r in records if start <= r["date"] <= end]