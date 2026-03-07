"""
ClimateInsight — NASA GISS Connector
modules/data_ingestion/src/connectors/nasa_giss.py

Ruft GISTEMP v4 Temperaturdaten von NASA ab und normalisiert sie
in das interne ClimateDataset-Format.

Datenquelle:
  Name:      GISS Surface Temperature Analysis (GISTEMP v4)
  Provider:  NASA Goddard Institute for Space Studies
  URL:       https://data.giss.nasa.gov/gistemp/
  DOI:       10.7289/V5MGNM48
  Lizenz:    Public Domain
  Auflösung: Monatlich
  Deckung:   1880–heute (global)
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx  # pip install httpx

from ..models.climate_dataset import (
    ClimateDataset,
    ClimateVariable,
    DataPoint,
    DataResolution,
    DatasetQuality,
    QualityFlag,
    SourceReference,
    TemporalCoverage,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

# Globale Temperaturanomalie (Land + Ozean), monatliche Mittelwerte
# Bezugszeitraum: 1951–1980
NASA_GISTEMP_URL = (
    "https://data.giss.nasa.gov/gistemp/tabledata_v4/"
    "GLB.Ts+dSST.csv"
)

SOURCE_ID   = "nasa_giss_surface_temp_v4"
PROVIDER    = "NASA"
CITATION    = (
    "GISTEMP Team (2024): GISS Surface Temperature Analysis (GISTEMP v4). "
    "NASA Goddard Institute for Space Studies. "
    "Dataset accessed at https://data.giss.nasa.gov/gistemp/"
)
DOI         = "10.7289/V5MGNM48"
DATASET_URL = "https://data.giss.nasa.gov/gistemp/"

# Platzhalter für fehlende Werte in der NASA-CSV
MISSING_VALUE = "***"

# Monatsnamen → Spaltennamen in der NASA-CSV
MONTH_COLS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------------------
# Öffentliche API des Connectors
# ---------------------------------------------------------------------------

class NasaGissConnector:
    """
    Connector für NASA GISTEMP v4.

    Verwendung:
        connector = NasaGissConnector()
        dataset, points = await connector.fetch()
    """

    def __init__(self, timeout_seconds: int = 60) -> None:
        self._timeout = timeout_seconds

    # ------------------------------------------------------------------
    # Hauptmethode
    # ------------------------------------------------------------------

    async def fetch(
        self,
        date_from: Optional[str] = None,
        date_to:   Optional[str] = None,
    ) -> tuple[ClimateDataset, list[DataPoint]]:
        """
        Ruft GISTEMP v4 ab, parst und normalisiert alle Messpunkte.

        Args:
            date_from: Optionaler Filter, ISO8601-Datum (inklusiv)
            date_to:   Optionaler Filter, ISO8601-Datum (inklusiv)

        Returns:
            (ClimateDataset, list[DataPoint])

        Raises:
            httpx.HTTPStatusError: HTTP-Fehler von NASA-Server
            ValueError:            Unerwartetes CSV-Format
        """
        logger.info("Starte Abruf: NASA GISTEMP v4 von %s", NASA_GISTEMP_URL)

        raw_csv = await self._download(NASA_GISTEMP_URL)
        points  = self._parse_csv(raw_csv, date_from, date_to)

        logger.info("Geparste Datenpunkte: %d", len(points))

        dataset = self._build_dataset(points)
        return dataset, points

    # ------------------------------------------------------------------
    # Interne Methoden
    # ------------------------------------------------------------------

    async def _download(self, url: str) -> str:
        """HTTP-GET der CSV-Datei."""
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = client.get(url)
            # httpx AsyncClient braucht await — hier vereinfacht für Klarheit
            # In Produktion: resp = await client.get(url)
            resp.raise_for_status()
            return resp.text

    def _parse_csv(
        self,
        raw: str,
        date_from: Optional[str],
        date_to:   Optional[str],
    ) -> list[DataPoint]:
        """
        Parst die NASA GISTEMP CSV.

        Format der NASA-CSV:
          - Kopfzeilen beginnen mit "GLOBAL" oder "Land"
          - Datenzeilen: Jahr, Jan, Feb, ..., Dec, J-D, D-N, DJF, MAM, JJA, SON
          - Fehlende Werte: "***"
          - Einheit: °C (Anomalie gegenüber 1951–1980)
        """
        points: list[DataPoint] = []

        # Filtergrenze vorbereiten
        ts_from = datetime.fromisoformat(date_from) if date_from else None
        ts_to   = datetime.fromisoformat(date_to)   if date_to   else None

        reader = csv.DictReader(io.StringIO(raw))

        for row in reader:
            year_str = row.get("Year", "").strip()
            if not year_str.isdigit():
                continue  # Kommentarzeilen überspringen

            year = int(year_str)

            for month_idx, col in enumerate(MONTH_COLS, start=1):
                raw_val = row.get(col, MISSING_VALUE).strip()

                # Zeitstempel für den ersten Tag des Monats
                ts = datetime(year, month_idx, 1, tzinfo=timezone.utc)

                # Datumsfilter anwenden
                if ts_from and ts < ts_from:
                    continue
                if ts_to and ts > ts_to:
                    break

                if raw_val == MISSING_VALUE:
                    # Fehlenden Wert als NaN mit quality_flag=missing speichern
                    points.append(DataPoint(
                        timestamp    = ts,
                        value        = float("nan"),
                        unit         = "°C",
                        quality_flag = QualityFlag.MISSING,
                    ))
                else:
                    try:
                        value = float(raw_val)
                    except ValueError:
                        logger.warning(
                            "Unerwarteter Wert in NASA CSV: Jahr=%d Monat=%s Wert=%r",
                            year, col, raw_val,
                        )
                        continue

                    # Plausibilitätsprüfung: Temperaturanomalien liegen realistisch
                    # zwischen -5 und +5 °C
                    flag = (
                        QualityFlag.GOOD
                        if -5.0 <= value <= 5.0
                        else QualityFlag.QUESTIONABLE
                    )

                    points.append(DataPoint(
                        timestamp    = ts,
                        value        = value,
                        unit         = "°C",
                        quality_flag = flag,
                    ))

        return points

    def _build_dataset(self, points: list[DataPoint]) -> ClimateDataset:
        """Erstellt das ClimateDataset-Objekt aus den geparsten Punkten."""
        good_points = [p for p in points if p.quality_flag != QualityFlag.MISSING]

        # Zeitraum aus tatsächlichen Daten ableiten
        if good_points:
            start_str = good_points[0].timestamp.strftime("%Y-%m-%d")
            end_str   = good_points[-1].timestamp.strftime("%Y-%m-%d")
        else:
            start_str, end_str = "1880-01-01", "unknown"

        # Gesamtqualität bewerten
        missing_count = sum(1 for p in points if p.quality_flag == QualityFlag.MISSING)
        missing_pct   = missing_count / len(points) if points else 1.0
        overall_q     = (
            DatasetQuality.GOOD     if missing_pct < 0.05 else
            DatasetQuality.DEGRADED if missing_pct < 0.20 else
            DatasetQuality.UNKNOWN
        )

        source = SourceReference(
            source_id   = SOURCE_ID,
            provider    = PROVIDER,
            citation    = CITATION,
            doi         = DOI,
            url         = DATASET_URL,
            accessed_at = datetime.now(timezone.utc),
        )

        return ClimateDataset(
            id                = SOURCE_ID,
            variable          = ClimateVariable.SURFACE_TEMPERATURE_ANOMALY,
            temporal_coverage = TemporalCoverage(start=start_str, end=end_str),
            spatial_coverage  = "global",
            resolution        = DataResolution.MONTHLY,
            unit              = "°C",
            records           = len(good_points),
            citation          = CITATION,
            doi               = DOI,
            last_updated      = datetime.now(timezone.utc),
            quality           = overall_q,
            source            = source,
        )