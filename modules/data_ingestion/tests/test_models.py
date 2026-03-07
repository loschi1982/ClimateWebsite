# ─────────────────────────────────────────────────────────────────────────────
# Was macht diese Datei?
# Unit Tests für die Pydantic-Datenmodelle aus climate_dataset.py.
# Wir prüfen: Schema-Validierung, Default-Werte, Pflichtfelder,
# und Grenzbedingungen (was passiert bei ungültigen Eingaben?).
#
# Team: Data Pipeline Team | Branch: feature/data-pipeline
# ─────────────────────────────────────────────────────────────────────────────

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

# sys/os: Ermöglicht den Import aus dem src-Verzeichnis
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from models.climate_dataset import (
    DataPoint,
    ClimateDataset,
    IngestionJob,
    SourceReference,
)


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen für Testdaten
# ─────────────────────────────────────────────────────────────────────────────

def _sample_source_reference() -> SourceReference:
    """Erstellt eine gültige SourceReference für Tests."""
    return SourceReference(
        provider="NASA Test Provider",
        dataset_name="Test Dataset v1",
        citation="Test Citation (2024)",
        doi="10.1234/test",
        url="https://test.example.com/data",
        license="Public Domain",
    )


def _sample_data_point() -> DataPoint:
    """Erstellt einen gültigen DataPoint für Tests."""
    return DataPoint(
        timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
        value=1.17,
        unit="°C anomaly",
        quality_flag="good",
    )


def _sample_climate_dataset() -> ClimateDataset:
    """Erstellt ein gültiges ClimateDataset für Tests."""
    return ClimateDataset(
        dataset_id="test_dataset_v1",
        variable="surface_temperature_anomaly",
        description="Testdatensatz",
        source=_sample_source_reference(),
        records=[_sample_data_point()],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tests: DataPoint
# ─────────────────────────────────────────────────────────────────────────────
class TestDataPoint:
    """Tests für das DataPoint-Modell."""

    def test_valid_data_point_creation(self):
        """Ein gültiger DataPoint soll ohne Fehler erstellt werden."""
        dp = _sample_data_point()
        assert dp.value == pytest.approx(1.17)
        assert dp.unit == "°C anomaly"
        assert dp.quality_flag == "good"

    def test_default_quality_flag_is_good(self):
        """quality_flag soll standardmäßig 'good' sein."""
        dp = DataPoint(
            timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
            value=0.5,
            unit="°C",
        )
        assert dp.quality_flag == "good"

    def test_quality_flag_estimated(self):
        """quality_flag='estimated' soll akzeptiert werden."""
        dp = DataPoint(
            timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
            value=0.5,
            unit="°C",
            quality_flag="estimated",
        )
        assert dp.quality_flag == "estimated"

    def test_quality_flag_suspect(self):
        """quality_flag='suspect' soll akzeptiert werden."""
        dp = DataPoint(
            timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
            value=0.5,
            unit="°C",
            quality_flag="suspect",
        )
        assert dp.quality_flag == "suspect"

    def test_invalid_quality_flag_raises_error(self):
        """
        Ein ungültiger quality_flag soll eine ValidationError werfen.
        Pydantic validiert automatisch, dass nur erlaubte Werte verwendet werden.
        """
        with pytest.raises(ValidationError):
            DataPoint(
                timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
                value=0.5,
                unit="°C",
                quality_flag="invalid_value",  # Nicht in Literal["good","estimated","suspect"]
            )

    def test_negative_value_is_valid(self):
        """Negative Werte (Temperaturanomalien können negativ sein) sollen erlaubt sein."""
        dp = DataPoint(
            timestamp=datetime(1900, 1, 1, tzinfo=timezone.utc),
            value=-0.42,
            unit="°C",
        )
        assert dp.value == pytest.approx(-0.42)

    def test_missing_timestamp_raises_error(self):
        """Fehlendes Pflichtfeld 'timestamp' soll ValidationError werfen."""
        with pytest.raises(ValidationError):
            DataPoint(value=1.0, unit="°C")  # timestamp fehlt

    def test_missing_value_raises_error(self):
        """Fehlendes Pflichtfeld 'value' soll ValidationError werfen."""
        with pytest.raises(ValidationError):
            DataPoint(
                timestamp=datetime(2000, 1, 1, tzinfo=timezone.utc),
                unit="°C",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests: SourceReference
# ─────────────────────────────────────────────────────────────────────────────
class TestSourceReference:
    """Tests für das SourceReference-Modell."""

    def test_valid_source_reference(self):
        """Eine gültige SourceReference soll erstellt werden können."""
        src = _sample_source_reference()
        assert src.provider == "NASA Test Provider"
        assert src.doi == "10.1234/test"

    def test_doi_is_optional(self):
        """doi ist optional — kein Fehler wenn es fehlt."""
        src = SourceReference(
            provider="Test",
            dataset_name="Test",
            citation="Test (2024)",
            url="https://example.com",
        )
        assert src.doi is None

    def test_default_license_is_public_domain(self):
        """Standard-Lizenz soll 'Public Domain' sein."""
        src = SourceReference(
            provider="Test",
            dataset_name="Test",
            citation="Test (2024)",
            url="https://example.com",
        )
        assert src.license == "Public Domain"

    def test_invalid_url_raises_error(self):
        """Eine ungültige URL soll ValidationError werfen."""
        with pytest.raises(ValidationError):
            SourceReference(
                provider="Test",
                dataset_name="Test",
                citation="Test",
                url="keine-gueltige-url",  # Kein http:// oder https://
            )

    def test_accessed_at_is_set_automatically(self):
        """accessed_at soll automatisch auf die aktuelle Zeit gesetzt werden."""
        src = _sample_source_reference()
        assert src.accessed_at is not None
        # Die Zeit sollte aktuell sein (innerhalb der letzten Minute)
        diff = abs((datetime.utcnow() - src.accessed_at.replace(tzinfo=None)).total_seconds())
        assert diff < 60, "accessed_at sollte die aktuelle Zeit sein"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: ClimateDataset
# ─────────────────────────────────────────────────────────────────────────────
class TestClimateDataset:
    """Tests für das ClimateDataset-Modell."""

    def test_valid_dataset_creation(self):
        """Ein gültiges ClimateDataset soll erstellt werden können."""
        ds = _sample_climate_dataset()
        assert ds.dataset_id == "test_dataset_v1"
        assert ds.variable == "surface_temperature_anomaly"

    def test_uuid_generated_automatically(self):
        """id (interne UUID) soll automatisch generiert werden."""
        ds = _sample_climate_dataset()
        assert ds.id is not None
        assert len(ds.id) == 36  # UUID hat Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

    def test_two_datasets_have_different_ids(self):
        """Zwei Datensätze sollen unterschiedliche IDs haben."""
        ds1 = _sample_climate_dataset()
        ds2 = _sample_climate_dataset()
        assert ds1.id != ds2.id, "Jede UUID soll einzigartig sein"

    def test_record_count_property(self):
        """record_count soll die Anzahl der records zurückgeben."""
        ds = _sample_climate_dataset()
        assert ds.record_count == 1

    def test_empty_records_by_default(self):
        """Ohne records soll eine leere Liste verwendet werden."""
        ds = ClimateDataset(
            dataset_id="empty",
            variable="test",
            description="Test",
            source=_sample_source_reference(),
        )
        assert ds.records == []
        assert ds.record_count == 0

    def test_multiple_records(self):
        """Mehrere records sollen korrekt gespeichert werden."""
        points = [
            DataPoint(
                timestamp=datetime(y, 1, 1, tzinfo=timezone.utc),
                value=float(y - 2000) * 0.01,
                unit="°C",
            )
            for y in range(2000, 2010)  # 10 Datenpunkte
        ]
        ds = ClimateDataset(
            dataset_id="multi",
            variable="test",
            description="Test",
            source=_sample_source_reference(),
            records=points,
        )
        assert ds.record_count == 10

    def test_temporal_coverage_optional(self):
        """temporal_coverage_start/end sollen optional sein."""
        ds = ClimateDataset(
            dataset_id="t",
            variable="t",
            description="t",
            source=_sample_source_reference(),
        )
        assert ds.temporal_coverage_start is None
        assert ds.temporal_coverage_end is None


# ─────────────────────────────────────────────────────────────────────────────
# Tests: IngestionJob
# ─────────────────────────────────────────────────────────────────────────────
class TestIngestionJob:
    """Tests für das IngestionJob-Modell."""

    def test_valid_job_creation(self):
        """Ein gültiger Job soll erstellt werden können."""
        job = IngestionJob(source_id="nasa_giss")
        assert job.source_id == "nasa_giss"
        assert job.status == "pending"

    def test_default_status_is_pending(self):
        """Neuer Job soll status='pending' haben."""
        job = IngestionJob(source_id="test")
        assert job.status == "pending"

    def test_job_id_auto_generated(self):
        """job_id soll automatisch generiert werden."""
        job = IngestionJob(source_id="test")
        assert job.job_id is not None
        assert len(job.job_id) == 36

    def test_two_jobs_have_different_ids(self):
        """Zwei Jobs sollen unterschiedliche IDs haben."""
        j1 = IngestionJob(source_id="test")
        j2 = IngestionJob(source_id="test")
        assert j1.job_id != j2.job_id

    def test_invalid_status_raises_error(self):
        """Ein ungültiger Status soll ValidationError werfen."""
        with pytest.raises(ValidationError):
            IngestionJob(source_id="test", status="invalid_status")

    def test_all_valid_statuses(self):
        """Alle vier gültigen Status-Werte sollen akzeptiert werden."""
        for status in ["pending", "running", "completed", "failed"]:
            job = IngestionJob(source_id="test", status=status)
            assert job.status == status

    def test_optional_fields_are_none_by_default(self):
        """Optionale Felder sollen standardmäßig None sein."""
        job = IngestionJob(source_id="test")
        assert job.completed_at is None
        assert job.records_fetched is None
        assert job.dataset_id is None
        assert job.error_message is None

    def test_started_at_is_set_automatically(self):
        """started_at soll automatisch auf die aktuelle Zeit gesetzt werden."""
        job = IngestionJob(source_id="test")
        assert job.started_at is not None
        diff = abs(
            (datetime.utcnow() - job.started_at.replace(tzinfo=None)).total_seconds()
        )
        assert diff < 60