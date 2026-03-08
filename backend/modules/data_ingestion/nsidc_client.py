"""
DP-03: NSIDC Sea Ice Index Client.

Ruft monatliche Meereisausdehnung für Arktis und Antarktis ab.
Quelle: https://nsidc.org/data/seaice_index/
Lizenz: Public Domain
Zitierung: Fetterer, F., K. Knowles, W. N. Meier, M. Savoie, and A. K. Windnagel.
           2017, updated daily. Sea Ice Index, Version 3. NSIDC.
"""

import logging
from io import StringIO

import pandas as pd

from .base_client import BaseClient, DatasetDict

logger = logging.getLogger(__name__)

# Direkte CSV-Download-URLs für Arktis und Antarktis
_NSIDC_URL_ARCTIC = (
    "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/"
    "N_seaice_extent_monthly_v3.0.csv"
)
_NSIDC_URL_ANTARCTIC = (
    "https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/data/"
    "S_seaice_extent_monthly_v3.0.csv"
)

# Gültige Wertebereiche für Meereisausdehnung in Millionen km²
_MIN_EXTENT = 0.0
_MAX_EXTENT = 20.0  # Physikalisches Maximum der Meereisausdehnung


class NsidcClient(BaseClient):
    """
    Client für den NSIDC Sea Ice Index (Version 3).

    Unterstützt zwei Variablen:
    - 'sea_ice_arctic':     Arktis-Meereisausdehnung (ab Oktober 1978)
    - 'sea_ice_antarctic':  Antarktis-Meereisausdehnung (ab November 1978)

    Einheit: Millionen km²
    """

    SOURCE_ID = "nsidc"
    SOURCE_NAME = "NSIDC Sea Ice Index, Version 3"
    SOURCE_URL = "https://nsidc.org/data/seaice_index/"
    LICENSE = "Public Domain"

    # Mapping: Variable → Download-URL
    _VARIABLE_URLS = {
        "sea_ice_arctic": _NSIDC_URL_ARCTIC,
        "sea_ice_antarctic": _NSIDC_URL_ANTARCTIC,
    }

    def fetch(self, start: str, end: str, variable: str = "sea_ice_arctic") -> DatasetDict:
        """
        Ruft NSIDC Meereisausdehnung für Arktis oder Antarktis ab.

        Args:
            start:    Startdatum im Format 'YYYY-MM-DD'.
            end:      Enddatum im Format 'YYYY-MM-DD'.
            variable: 'sea_ice_arctic' oder 'sea_ice_antarctic'.

        Returns:
            Normalisiertes Dataset-Dict mit monatlicher Meereisausdehnung in Mio. km².

        Raises:
            ValueError: Wenn eine unbekannte Variable angegeben wird.
            requests.exceptions.RequestException: Bei Netzwerkfehlern.
        """
        if variable not in self._VARIABLE_URLS:
            raise ValueError(
                f"[nsidc] Unbekannte Variable '{variable}'. "
                f"Erlaubt: {list(self._VARIABLE_URLS.keys())}"
            )

        url = self._VARIABLE_URLS[variable]
        response = self._get(url)
        raw_data = self._parse(response.text)
        filtered = self._filter_by_date(raw_data, start, end)
        logger.info(
            f"[nsidc/{variable}] {len(filtered)} Datenpunkte "
            f"nach Filterung ({start} – {end})"
        )
        return self._build_dataset(
            variable=variable,
            unit="Millionen km²",
            data=filtered,
        )

    def _parse(self, csv_text: str) -> list[dict]:
        """
        Parst den CSV-Rohdatei-Text des NSIDC Sea Ice Index.

        Die NSIDC-CSV hat Leerzeichen in Spaltennamen, die bereinigt werden.
        Fehlwerte und physikalisch unmögliche Werte werden als None markiert.

        Args:
            csv_text: Inhalt der heruntergeladenen CSV-Datei als String.

        Returns:
            Liste von {'date': 'YYYY-MM-DD', 'value': float | None} Dicts,
            chronologisch sortiert.
        """
        df = pd.read_csv(StringIO(csv_text), skipinitialspace=True)

        # Leerzeichen aus Spaltennamen entfernen (häufiges Problem bei NSIDC-CSVs)
        df.columns = df.columns.str.strip()

        required = {"Year", "Mo", "Extent"}
        if not required.issubset(df.columns):
            raise ValueError(
                f"[nsidc] Unbekannte CSV-Struktur – fehlende Spalten: "
                f"{required - set(df.columns)}"
            )

        records = []
        for _, row in df.iterrows():
            year = int(row["Year"])
            month = int(row["Mo"])

            try:
                extent = float(row["Extent"])
            except (ValueError, TypeError):
                extent = None

            # Physikalisch unmögliche Werte als None markieren
            if extent is not None and not (_MIN_EXTENT <= extent <= _MAX_EXTENT):
                logger.warning(
                    f"[nsidc] Unplausibler Wert {extent} für {year}-{month:02d} – "
                    f"wird als None gespeichert."
                )
                extent = None

            date_str = f"{year}-{month:02d}-01"
            records.append({"date": date_str, "value": extent})

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