"""
ClimateInsight — Data Ingestion Models
modules/data_ingestion/src/models/climate_dataset.py

Pydantic-Datenmodelle für alle Klimadaten im System.
Pflichtlektüre für das Data Pipeline Team.

Alle anderen Teams nutzen diese Typen nur lesend,
Änderungen immer im project_memory.json dokumentieren.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class QualityFlag(str, Enum):
    """Datenqualität eines einzelnen Messpunkts."""
    GOOD         = "good"
    ESTIMATED    = "estimated"
    QUESTIONABLE = "questionable"
    MISSING      = "missing"


class ClimateVariable(str, Enum):
    """Alle unterstützten Klimavariablen der Plattform."""
    SURFACE_TEMPERATURE_ANOMALY = "surface_temperature_anomaly"
    SEA_LEVEL_CHANGE            = "sea_level_change"
    SEA_ICE_EXTENT              = "sea_ice_extent"
    CO2_CONCENTRATION           = "co2_concentration"
    ARCTIC_ICE_VOLUME           = "arctic_ice_volume"
    PRECIPITATION_ANOMALY       = "precipitation_anomaly"
    OCEAN_HEAT_CONTENT          = "ocean_heat_content"


class DataResolution(str, Enum):
    """Zeitliche Auflösung eines Datensatzes."""
    DAILY   = "daily"
    MONTHLY = "monthly"
    ANNUAL  = "annual"


class JobStatus(str, Enum):
    """Status eines asynchronen Ingestion-Jobs."""
    QUEUED    = "queued"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"


class DatasetQuality(str, Enum):
    """Gesamtqualität eines Datensatzes."""
    GOOD     = "good"
    DEGRADED = "degraded"
    UNKNOWN  = "unknown"


class SourceStatus(str, Enum):
    """Status einer konfigurierten Datenquelle."""
    ACTIVE   = "active"
    INACTIVE = "inactive"
    ERROR    = "error"


# ---------------------------------------------------------------------------
# DataPoint
# ---------------------------------------------------------------------------

class DataPoint(BaseModel):
    """
    Einzelner normalisierter Messpunkt.

    Beispiel:
        DataPoint(
            timestamp=datetime(1880, 1, 1),
            value=-0.16,
            unit="°C",
            quality_flag=QualityFlag.GOOD,
        )
    """
    timestamp:    datetime     = Field(..., description="Messzeitpunkt (UTC)")
    value:        float        = Field(..., description="Messwert")
    unit:         str          = Field(..., description="Einheit, z.B. '°C', 'mm', 'ppm'")
    quality_flag: QualityFlag  = Field(..., description="Datenqualität")


# ---------------------------------------------------------------------------
# SourceReference
# ---------------------------------------------------------------------------

class SourceReference(BaseModel):
    """
    Vollständige Quellenangabe — Pflicht für jeden Datensatz.
    Jede Datenquelle braucht Zitation + URL + Abrufdatum.
    DOI ist optional, aber empfohlen.
    """
    source_id:   str           = Field(..., description="Interner Bezeichner, z.B. 'nasa_giss_surface_temp_v4'")
    provider:    str           = Field(..., description="Datenanbieter, z.B. 'NASA'")
    citation:    str           = Field(..., description="Vollständige wissenschaftliche Zitation")
    doi:         Optional[str] = Field(None, description="Digital Object Identifier, z.B. '10.7289/V5MGNM48'")
    url:         str           = Field(..., description="Direkte URL zur Datenquelle")
    accessed_at: datetime      = Field(..., description="Abrufdatum (UTC) — dokumentiert Aktualität")


# ---------------------------------------------------------------------------
# ClimateDataset
# ---------------------------------------------------------------------------

class TemporalCoverage(BaseModel):
    """Zeitlicher Abdeckungsbereich eines Datensatzes."""
    start: str = Field(..., description="Startdatum ISO8601, z.B. '1880-01-01'")
    end:   str = Field(..., description="Enddatum ISO8601, z.B. '2025-12-31'")


class ClimateDataset(BaseModel):
    """
    Normalisierter Klimadatensatz — zentrale Einheit im System.
    Wird von Climate Analysis, Visualization und Frontend gelesen.
    """
    id:                str               = Field(..., description="Eindeutige Dataset-ID")
    variable:          ClimateVariable   = Field(..., description="Klimavariable")
    temporal_coverage: TemporalCoverage  = Field(..., description="Zeitraum des Datensatzes")
    spatial_coverage:  str               = Field(..., description="z.B. 'global', 'arctic'")
    resolution:        DataResolution    = Field(..., description="Zeitliche Auflösung")
    unit:              str               = Field(..., description="Maßeinheit der Werte")
    records:           int               = Field(0, ge=0, description="Anzahl Datenpunkte")
    citation:          Optional[str]     = Field(None)
    doi:               Optional[str]     = Field(None)
    last_updated:      Optional[datetime]= Field(None)
    quality:           DatasetQuality    = Field(DatasetQuality.UNKNOWN)
    source:            SourceReference   = Field(..., description="Vollständiger Quellenverweis")


# ---------------------------------------------------------------------------
# IngestionJob
# ---------------------------------------------------------------------------

class QualityReport(BaseModel):
    """
    Qualitätsbericht eines abgeschlossenen Ingestion-Jobs.
    Dokumentiert Datenmängel transparent.
    """
    missing_values:    int          = Field(0, ge=0)
    out_of_range_values: int        = Field(0, ge=0)
    duplicate_records: int          = Field(0, ge=0)
    overall_quality:   DatasetQuality = Field(DatasetQuality.UNKNOWN)


class IngestionJob(BaseModel):
    """
    Asynchroner Job zum Abruf einer Datenquelle.
    Wird über POST /api/v1/ingestion/trigger gestartet.
    """
    job_id:                      str                    = Field(..., description="Eindeutige Job-ID")
    source_id:                   str                    = Field(..., description="Datenquellen-Bezeichner")
    status:                      JobStatus              = Field(JobStatus.QUEUED)
    started_at:                  Optional[datetime]     = Field(None)
    completed_at:                Optional[datetime]     = Field(None)
    records_ingested:            int                    = Field(0, ge=0)
    dataset_id:                  Optional[str]          = Field(None, description="ID des erzeugten Datensatzes")
    quality_report:              Optional[QualityReport]= Field(None)
    error:                       Optional[str]          = Field(None)
    estimated_completion_seconds:Optional[int]          = Field(None)

    @field_validator("completed_at")
    @classmethod
    def completed_requires_started(cls, v, info):
        """Abschlusszeit darf nicht vor Startzeit liegen."""
        started = info.data.get("started_at")
        if v and started and v < started:
            raise ValueError("completed_at darf nicht vor started_at liegen")
        return v