"""
ClimateInsight — Ingestion API Router
services/api_gateway/src/routers/ingestion.py

Implementiert alle 5 Endpoints aus api_contracts.md:
  POST /api/v1/ingestion/trigger
  GET  /api/v1/ingestion/jobs/{job_id}
  GET  /api/v1/ingestion/datasets
  GET  /api/v1/ingestion/datasets/{dataset_id}/data
  GET  /api/v1/ingestion/sources

Owner: Data Pipeline Team
Consumer: Climate Analysis Team, Visualization Team, Frontend Team
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from modules.data_ingestion.src.models.climate_dataset import (
    ClimateVariable,
    DatasetQuality,
    JobStatus,
)

# ---------------------------------------------------------------------------
# Router-Konfiguration
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])
security = HTTPBearer()


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _meta() -> dict:
    """Standard-Response-Meta für alle Antworten."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version":   "1.0",
        "request_id": f"req_{uuid.uuid4().hex[:8]}",
    }


def _ok(data: dict) -> dict:
    """Erfolgs-Wrapper gemäß API-Vertrag."""
    return {"status": "ok", "data": data, "meta": _meta()}


def _error(code: str, message: str, http_status: int) -> HTTPException:
    """Fehler-Wrapper gemäß API-Vertrag."""
    return HTTPException(
        status_code=http_status,
        detail={
            "status": "error",
            "error":  {"code": code, "message": message},
            "meta":   _meta(),
        },
    )


# ---------------------------------------------------------------------------
# In-Memory-Speicher (Platzhalter — ersetzt durch TimescaleDB in Phase 2)
# ---------------------------------------------------------------------------

_jobs: dict[str, dict]     = {}  # job_id → IngestionJob-Dict
_datasets: dict[str, dict] = {}  # dataset_id → Dataset-Dict

# Konfigurierte Datenquellen (später aus YAML geladen)
_SOURCES = [
    {
        "id":                   "nasa_giss_surface_temp",
        "name":                 "GISS Surface Temperature Analysis (GISTEMP v4)",
        "provider":             "NASA",
        "variables":            ["surface_temperature_anomaly"],
        "update_frequency":     "monthly",
        "status":               "active",
        "last_successful_fetch": None,
    },
    {
        "id":                   "noaa_co2_mauna_loa",
        "name":                 "Mauna Loa CO₂ Monthly Mean",
        "provider":             "NOAA GML",
        "variables":            ["co2_concentration"],
        "update_frequency":     "monthly",
        "status":               "active",
        "last_successful_fetch": None,
    },
]
_SOURCE_IDS = {s["id"] for s in _SOURCES}


# ---------------------------------------------------------------------------
# Request-Modelle
# ---------------------------------------------------------------------------

class TriggerRequest(BaseModel):
    """Request-Body für POST /ingestion/trigger"""
    source_id:     str
    date_range:    Optional[dict] = None  # {"start": "...", "end": "..."}
    force_refresh: bool = False


# ---------------------------------------------------------------------------
# POST /api/v1/ingestion/trigger
# ---------------------------------------------------------------------------

@router.post(
    "/trigger",
    status_code=202,
    summary="Datenabruf starten",
    description="Startet einen asynchronen Job zum Abruf einer konfigurierten Datenquelle.",
)
async def trigger_ingestion(
    req: TriggerRequest,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    # Quelle prüfen
    if req.source_id not in _SOURCE_IDS:
        raise _error(
            "VALIDATION_ERROR",
            f"Unbekannte source_id: '{req.source_id}'. "
            f"Erlaubte Werte: {sorted(_SOURCE_IDS)}",
            422,
        )

    # Bereits laufenden Job prüfen
    running = [
        j for j in _jobs.values()
        if j["source_id"] == req.source_id and j["status"] == "running"
    ]
    if running and not req.force_refresh:
        raise _error("JOB_ALREADY_RUNNING", "Bereits ein laufender Job für diese Quelle.", 409)

    # Job erstellen
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job = {
        "job_id":                       job_id,
        "source_id":                    req.source_id,
        "status":                       JobStatus.QUEUED,
        "started_at":                   None,
        "completed_at":                 None,
        "records_ingested":             0,
        "dataset_id":                   None,
        "quality_report":               None,
        "error":                        None,
        "estimated_completion_seconds": 120,
    }
    _jobs[job_id] = job

    # Hintergrundaufgabe starten (in Produktion: Celery-Task)
    # background_tasks.add_task(_run_ingestion, job_id, req)

    return _ok({
        "job_id":                       job_id,
        "source_id":                    req.source_id,
        "status":                       "queued",
        "estimated_completion_seconds": 120,
    })


# ---------------------------------------------------------------------------
# GET /api/v1/ingestion/jobs/{job_id}
# ---------------------------------------------------------------------------

@router.get(
    "/jobs/{job_id}",
    summary="Job-Status abrufen",
    description="Gibt den aktuellen Status eines Ingestion-Jobs zurück.",
)
async def get_job_status(job_id: str):
    if job_id not in _jobs:
        raise _error("NOT_FOUND", f"Job '{job_id}' nicht gefunden.", 404)

    return _ok(_jobs[job_id])


# ---------------------------------------------------------------------------
# GET /api/v1/ingestion/datasets
# ---------------------------------------------------------------------------

@router.get(
    "/datasets",
    summary="Verfügbare Datensätze auflisten",
    description="Listet alle normalisierten Datensätze, optional gefiltert.",
)
async def list_datasets(
    variable: Optional[ClimateVariable] = Query(None, description="Klimavariable"),
    provider: Optional[str]             = Query(None, description="Datenanbieter"),
    from_:    Optional[str]             = Query(None, alias="from", description="ISO8601-Datum"),
    to:       Optional[str]             = Query(None, description="ISO8601-Datum"),
):
    result = list(_datasets.values())

    # Filter anwenden
    if variable:
        result = [d for d in result if d.get("variable") == variable]
    if provider:
        result = [d for d in result if d.get("source", {}).get("provider") == provider]

    return _ok({"datasets": result, "total": len(result)})


# ---------------------------------------------------------------------------
# GET /api/v1/ingestion/datasets/{dataset_id}/data
# ---------------------------------------------------------------------------

@router.get(
    "/datasets/{dataset_id}/data",
    summary="Rohdaten eines Datensatzes abrufen",
    description="Gibt paginierte Datenpunkte eines normalisierten Datensatzes zurück.",
)
async def get_dataset_data(
    dataset_id: str,
    from_:      Optional[str] = Query(None, alias="from"),
    to:         Optional[str] = Query(None),
    limit:      int           = Query(1000, ge=1, le=10000),
    offset:     int           = Query(0,    ge=0),
):
    if dataset_id not in _datasets:
        raise _error("NOT_FOUND", f"Datensatz '{dataset_id}' nicht gefunden.", 404)

    ds = _datasets[dataset_id]
    points: list[dict] = ds.get("_points", [])

    # Zeitraumfilter
    if from_:
        ts_from = datetime.fromisoformat(from_)
        points = [p for p in points if datetime.fromisoformat(p["timestamp"]) >= ts_from]
    if to:
        ts_to = datetime.fromisoformat(to)
        points = [p for p in points if datetime.fromisoformat(p["timestamp"]) <= ts_to]

    total  = len(points)
    paged  = points[offset : offset + limit]

    return _ok({
        "dataset_id":      dataset_id,
        "variable":        ds.get("variable"),
        "unit":            ds.get("unit"),
        "points":          paged,
        "total_points":    total,
        "returned_points": len(paged),
        "source":          ds.get("source"),
    })


# ---------------------------------------------------------------------------
# GET /api/v1/ingestion/sources
# ---------------------------------------------------------------------------

@router.get(
    "/sources",
    summary="Konfigurierte Datenquellen auflisten",
    description="Gibt alle konfigurierten Datenquellen mit ihrem Status zurück.",
)
async def list_sources():
    return _ok({"sources": _SOURCES})