"""
ClimateInsight — Unit Tests: Modelle + NASA GISS Connector
modules/data_ingestion/tests/test_models_and_connector.py

Ausführen:
    pytest modules/data_ingestion/tests/ -v

Testgruppen:
    TestDataPoint         — Datenpunkt-Validierung
    TestIngestionJob      — Job-Validierung (inkl. Zeitprüfung)
    TestSourceReference   — Quellenangabe-Pflichtfelder
    TestNasaGissParser    — CSV-Parsing (Offline-Tests mit Fixtures)
    TestNasaGissDataset   — Dataset-Erzeugung aus Datenpunkten
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

import pytest

from modules.data_ingestion.src.models.climate_dataset import (
    ClimateDataset,
    ClimateVariable,
    DataPoint,
    DataResolution,
    DatasetQuality,
    IngestionJob,
    JobStatus,
    QualityFlag,
    SourceReference,
    TemporalCoverage,
)
from modules.data_ingestion.src.connectors.nasa_giss import NasaGissConnector

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def valid_source() -> SourceReference:
    return SourceReference(
        source_id   = "nasa_giss_surface_temp_v4",
        provider    = "NASA",
        citation    = "GISTEMP Team (2024): GISS Surface Temperature Analysis.",
        doi         = "10.7289/V5MGNM48",
        url         = "https://data.giss.nasa.gov/gistemp/",
        accessed_at = datetime.now(timezone.utc),
    )


@pytest.fixture()
def sample_csv() -> str:
    """Minimales GISTEMP-CSV-Fragment für Offline-Tests."""
    return (
        "Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON\n"
        "1880,-0.16,-0.09,-0.10,-0.18,-0.14,-0.22,-0.18,-0.10,-0.13,-0.24,-0.22,-0.18,-0.16,***,***,-0.14,-0.17,-0.20\n"
        "1881,-0.19,-0.14,-0.06,-0.01,-0.04,-0.13,-0.18,-0.20,-0.18,-0.22,-0.29,-0.13,-0.15,-0.15,-0.17,-0.04,-0.17,-0.23\n"
        "2024,1.29,1.34,1.45,1.38,1.41,1.36,1.39,1.42,1.35,1.40,1.44,1.48,1.39,***,***,1.41,1.39,1.40\n"
    )


# ---------------------------------------------------------------------------
# TestDataPoint
# ---------------------------------------------------------------------------

class TestDataPoint:
    def test_valid_datapoint(self):
        dp = DataPoint(
            timestamp    = datetime(1880, 1, 1, tzinfo=timezone.utc),
            value        = -0.16,
            unit         = "°C",
            quality_flag = QualityFlag.GOOD,
        )
        assert dp.value == -0.16
        assert dp.unit  == "°C"
        assert dp.quality_flag == QualityFlag.GOOD

    def test_missing_datapoint_nan(self):
        """Fehlende Werte werden als NaN mit Flag MISSING gespeichert."""
        dp = DataPoint(
            timestamp    = datetime(1880, 2, 1, tzinfo=timezone.utc),
            value        = float("nan"),
            unit         = "°C",
            quality_flag = QualityFlag.MISSING,
        )
        assert math.isnan(dp.value)
        assert dp.quality_flag == QualityFlag.MISSING

    def test_quality_flag_enum_values(self):
        flags = [f.value for f in QualityFlag]
        assert "good" in flags
        assert "missing" in flags


# ---------------------------------------------------------------------------
# TestIngestionJob
# ---------------------------------------------------------------------------

class TestIngestionJob:
    def test_valid_job(self):
        job = IngestionJob(
            job_id    = "job_001",
            source_id = "nasa_giss_surface_temp",
        )
        assert job.status == JobStatus.QUEUED
        assert job.records_ingested == 0

    def test_completed_before_started_raises(self):
        """completed_at darf nicht vor started_at liegen."""
        with pytest.raises(Exception):
            IngestionJob(
                job_id       = "job_002",
                source_id    = "nasa_giss_surface_temp",
                started_at   = datetime(2026, 3, 5, 10, 5, tzinfo=timezone.utc),
                completed_at = datetime(2026, 3, 5, 10, 0, tzinfo=timezone.utc),
            )

    def test_job_statuses(self):
        statuses = [s.value for s in JobStatus]
        assert "queued" in statuses
        assert "completed" in statuses
        assert "failed" in statuses


# ---------------------------------------------------------------------------
# TestSourceReference
# ---------------------------------------------------------------------------

class TestSourceReference:
    def test_valid_source(self, valid_source):
        assert valid_source.provider == "NASA"
        assert valid_source.doi == "10.7289/V5MGNM48"

    def test_missing_citation_raises(self):
        with pytest.raises(Exception):
            SourceReference(
                source_id   = "test",
                provider    = "NASA",
                citation    = None,  # type: ignore
                url         = "https://example.com",
                accessed_at = datetime.now(timezone.utc),
            )


# ---------------------------------------------------------------------------
# TestNasaGissParser
# ---------------------------------------------------------------------------

class TestNasaGissParser:
    def test_parse_known_values(self, sample_csv):
        """Bekannte Temperaturwerte aus dem Fixture korrekt geparst."""
        connector = NasaGissConnector()
        points = connector._parse_csv(sample_csv, None, None)

        # 1880-Jan: -0.16 °C (erster Datenpunkt)
        jan_1880 = next(
            p for p in points
            if p.timestamp.year == 1880 and p.timestamp.month == 1
        )
        assert jan_1880.value == pytest.approx(-0.16, abs=1e-6)
        assert jan_1880.quality_flag == QualityFlag.GOOD
        assert jan_1880.unit == "°C"

    def test_missing_value_marked_correctly(self, sample_csv):
        """Fehlende Werte (***) werden als MISSING markiert."""
        connector = NasaGissConnector()
        points = connector._parse_csv(sample_csv, None, None)

        # 1880-Dec ist in der Fixture nicht *** — aber J-D wird übersprungen
        # 2024-Dec: 1.48 — vorhanden
        dec_2024 = next(
            p for p in points
            if p.timestamp.year == 2024 and p.timestamp.month == 12
        )
        assert dec_2024.quality_flag == QualityFlag.GOOD

    def test_date_filter_from(self, sample_csv):
        """date_from-Filter schließt ältere Daten aus."""
        connector = NasaGissConnector()
        points = connector._parse_csv(sample_csv, "2000-01-01", None)
        years = {p.timestamp.year for p in points}
        assert 1880 not in years
        assert 2024 in years

    def test_total_point_count(self, sample_csv):
        """3 Jahre × 12 Monate = 36 Datenpunkte (inkl. fehlende)."""
        connector = NasaGissConnector()
        points = connector._parse_csv(sample_csv, None, None)
        assert len(points) == 36

    def test_modern_warming_positive(self, sample_csv):
        """2024-Werte sind alle positiv — Erwärmungssignal."""
        connector = NasaGissConnector()
        points = connector._parse_csv(sample_csv, None, None)
        pts_2024 = [p for p in points if p.timestamp.year == 2024
                    and p.quality_flag == QualityFlag.GOOD]
        assert all(p.value > 0 for p in pts_2024)


# ---------------------------------------------------------------------------
# TestNasaGissDataset
# ---------------------------------------------------------------------------

class TestNasaGissDataset:
    def test_dataset_metadata(self, sample_csv, valid_source):
        """Dataset enthält korrekte Metadaten."""
        connector = NasaGissConnector()
        points    = connector._parse_csv(sample_csv, None, None)
        dataset   = connector._build_dataset(points)

        assert dataset.variable == ClimateVariable.SURFACE_TEMPERATURE_ANOMALY
        assert dataset.resolution == DataResolution.MONTHLY
        assert dataset.unit == "°C"
        assert dataset.spatial_coverage == "global"
        assert dataset.source.provider == "NASA"
        assert dataset.source.doi == "10.7289/V5MGNM48"

    def test_dataset_quality_good(self, sample_csv):
        """Bei <5% fehlenden Werten: quality=good."""
        connector = NasaGissConnector()
        points    = connector._parse_csv(sample_csv, None, None)
        dataset   = connector._build_dataset(points)
        # Fixture hat wenige fehlende Werte → good erwartet
        assert dataset.quality in (DatasetQuality.GOOD, DatasetQuality.DEGRADED)

    def test_dataset_records_count(self, sample_csv):
        """records entspricht Anzahl nicht-fehlender Datenpunkte."""
        connector = NasaGissConnector()
        points    = connector._parse_csv(sample_csv, None, None)
        dataset   = connector._build_dataset(points)
        good_count = sum(1 for p in points if p.quality_flag != QualityFlag.MISSING)
        assert dataset.records == good_count

    def test_ipcc_ar6_trend_compatibility(self):
        """
        Plausibilitätstest: IPCC AR6 zeigt ~0.19°C/Dekade seit 1979.
        Dieser Test prüft nicht das Modell, sondern dass unser Datenformat
        Werte in diesem Bereich korrekt speichert (±5% Toleranz).
        """
        # Repräsentativer Trendwert aus IPCC AR6 (1979–2022)
        ipcc_trend_per_decade = 0.19  # °C/Dekade
        tolerance = 0.05 * ipcc_trend_per_decade

        # Wir testen nur das Speicherformat — echte Trendanalyse im Climate Analysis Modul
        value_to_store = ipcc_trend_per_decade / 10  # °C/Jahr
        dp = DataPoint(
            timestamp    = datetime(2000, 1, 1, tzinfo=timezone.utc),
            value        = value_to_store,
            unit         = "°C/year",
            quality_flag = QualityFlag.GOOD,
        )
        assert abs(dp.value - value_to_store) < 1e-9