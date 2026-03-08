"""
DP-02: NOAA Global Monitoring Laboratory – Mauna Loa CO₂ Client.

Ruft monatliche atmosphärische CO₂-Konzentrationen ab.
Quelle: https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv
Lizenz: Public Domain
Zitierung: Dr. Pieter Tans, NOAA/GML und Dr. Ralph Keeling,
           Scripps Institution of Oceanography.
"""

import logging
from io import StringIO

import pandas as pd

from .base_client import BaseClient, DatasetDict

logger = logging.getLogger(__name__)

_NOAA_URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"

# Erwartete Spaltennamen nach dem Kommentar-Header
_COLUMN_NAMES = [
    "year", "month", "decimal_date",
    "co2_avg", "deseasonalized", "ndays", "sdev", "unc"
]

# Fehlwert-Kennzeichnung in der NOAA-CSV
_MISSING_VALUE = -99.99


class NoaaClient(BaseClient):
    """
    Client für die NOAA GML Mauna Loa CO₂-Messungen.

    Gibt monatliche atmosphärische CO₂-Konzentrationen in ppm zurück.
    Die Mauna-Loa-Reihe ist die älteste kontinuierliche CO₂-Messreihe (ab 1958).
    """

    SOURCE_ID = "noaa"
    SOURCE_NAME = "NOAA GML Mauna Loa CO₂ Messungen"
    SOURCE_URL = _NOAA_URL
    LICENSE = "Public Domain"

    def fetch(self, start: str, end: str) -> DatasetDict:
        """
        Ruft NOAA Mauna Loa CO₂-Daten ab und filtert auf den gewünschten Zeitraum.

        Args:
            start: Startdatum im Format 'YYYY-MM-DD'.
            end:   Enddatum im Format 'YYYY-MM-DD'.

        Returns:
            Normalisiertes Dataset-Dict mit monatlichen CO₂-Werten in ppm.

        Raises:
            requests.exceptions.RequestException: Bei Netzwerkfehlern.
            ValueError: Wenn die CSV-Struktur unbekannt ist.
        """
        response = self._get(_NOAA_URL)
        raw_data = self._parse(response.text)
        filtered = self._filter_by_date(raw_data, start, end)
        logger.info(f"[noaa] {len(filtered)} Datenpunkte nach Filterung ({start} – {end})")
        return self._build_dataset(
            variable="co2",
            unit="ppm",
            data=filtered,
        )

    def _parse(self, csv_text: str) -> list[dict]:
        """
        Parst den CSV-Rohdatei-Text der NOAA GML.

        Die NOAA-CSV enthält Kommentarzeilen beginnend mit '#'.
        Fehlende Werte sind mit -99.99 gekennzeichnet.
        Verwendet wird die Spalte 'co2_avg' (monatlicher Durchschnitt).

        Args:
            csv_text: Inhalt der heruntergeladenen CSV-Datei als String.

        Returns:
            Liste von {'date': 'YYYY-MM-DD', 'value': float | None} Dicts,
            chronologisch sortiert. Fehlende Messungen werden als None übernommen.
        """
        df = pd.read_csv(
            StringIO(csv_text),
            comment="#",
            names=_COLUMN_NAMES,
            skipinitialspace=True,
        )

        # Sicherstellen, dass Pflichtfelder vorhanden sind
        required = {"year", "month", "co2_avg"}
        if not required.issubset(df.columns):
            raise ValueError(
                f"[noaa] Unbekannte CSV-Struktur – fehlende Spalten: {required - set(df.columns)}"
            )

        records = []
        for _, row in df.iterrows():
            year = int(row["year"])
            month = int(row["month"])
            raw_val = float(row["co2_avg"])

            # Fehlende Messung (Kennwert -99.99) als None übernehmen
            value = None if raw_val <= _MISSING_VALUE else raw_val
            date_str = f"{year}-{month:02d}-01"
            records.append({"date": date_str, "value": value})

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