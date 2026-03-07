# ─────────────────────────────────────────────────────────────────────────────
# Was macht diese Datei?
# Definiert alle HTTP-Endpoints (Routen) für die Daten-Ingestion-API.
# Hier legen wir fest, welche URLs andere Teams und Frontend aufrufen können,
# um Daten abzurufen oder Ingestion-Jobs zu starten.
#
# Was ist ein "Router" in FastAPI?
# Ein Router ist eine Sammlung zusammengehöriger Endpoints.
# Statt alle Endpoints in einer Datei zu haben, teilen wir sie auf:
# - ingestion.py → alles rund um Datenabruf und -verwaltung
# - analysis.py  → alles rund um Analyse (anderes Team)
# So bleibt der Code übersichtlich.
#
# Alle Endpoints sind exakt so implementiert wie in memory/api_contracts.md
# definiert. Keine eigenmächtigen Änderungen! (Regel G3)
#
# Team: Data Pipeline Team | Branch: feature/data-pipeline
# ─────────────────────────────────────────────────────────────────────────────

# logging: Für Protokollierung (wer hat wann was angefragt?)
import logging

# uuid: Für eindeutige Job-IDs
import uuid

# datetime, timezone: Für Zeitstempel
from datetime import datetime, timezone

# Dict, List, Any: Typangaben
from typing import Dict, List, Any, Optional

# FastAPI-Imports
# APIRouter: Erstellt einen Router (Sammlung von Endpoints)
# HTTPException: Ermöglicht strukturierte Fehlerantworten (z.B. 404 Not Found)
# BackgroundTasks: Führt aufwändige Aufgaben im Hintergrund aus,
#   damit der Client nicht warten muss (asynchron)
# Query, Path: Typen für URL-Parameter und Pfad-Parameter
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse

# Pydantic-Modelle für Request-Body-Validierung
# BaseModel: Basisklasse für Request-Daten
from pydantic import BaseModel, Field

# Eigene Modelle (aus Aufgabe 1.2)
from models.climate_dataset import ClimateDataset, IngestionJob, DataPoint

# Connector importieren (aus Aufgabe 1.1)
from connectors.nasa_giss import NasaGissConnector


# ─────────────────────────────────────────────────────────────────────────────
# Logger einrichten
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory-Speicher für Jobs und Datensätze
#
# WICHTIG: Das ist ein temporärer Speicher nur für die Entwicklung!
# In Produktion werden Jobs in TimescaleDB und Datensätze in MinIO gespeichert.
# (Siehe architecture.md für die endgültige Datenhaltung)
#
# Was ist "In-Memory"?
# "Im Arbeitsspeicher" bedeutet: Daten existieren nur solange der Server läuft.
# Nach einem Neustart sind sie weg. Das ist OK für Entwicklung, aber nicht
# für Produktion.
# ─────────────────────────────────────────────────────────────────────────────

# Alle laufenden und abgeschlossenen Jobs
_jobs_store: Dict[str, IngestionJob] = {}

# Alle fertig ingesierten Datensätze
_datasets_store: Dict[str, ClimateDataset] = {}

# Verfügbare Datenquellen (konfiguriert, aber noch nicht unbedingt abgerufen)
_available_sources = {
    "nasa_giss": {
        "source_id": "nasa_giss",
        "name": "NASA GISS Surface Temperature Analysis v4",
        "provider": "NASA Goddard Institute for Space Studies",
        "variable": "surface_temperature_anomaly",
        "temporal_coverage": "1880–present",
        "update_frequency": "monthly",
        "doi": "10.7289/V5T72FNM",
        "url": "https://data.giss.nasa.gov/gistemp/",
        "status": "available",
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# Request-Body-Modelle
# Diese Klassen definieren, welche Daten im HTTP-Request-Body erwartet werden.
# FastAPI validiert automatisch, ob der Client die richtigen Daten schickt.
# ─────────────────────────────────────────────────────────────────────────────
class IngestionTriggerRequest(BaseModel):
    """
    Daten für POST /api/v1/ingestion/trigger.

    Was ist ein "Request-Body"?
    Bei einem POST-Request kann der Client Daten mitsenden (im "Body").
    Diese Klasse definiert, welche Daten erwartet werden.
    """

    # source_id: Welche Datenquelle soll abgerufen werden?
    source_id: str = Field(
        description="ID der Datenquelle, z.B. 'nasa_giss'",
        example="nasa_giss",
    )

    # start_year / end_year: Optionaler Zeitraum
    start_year: Optional[int] = Field(
        default=None,
        description="Startjahr (optional), z.B. 1950",
        ge=1880,  # ge = "greater or equal" — NASA hat keine Daten vor 1880
        le=2100,
    )
    end_year: Optional[int] = Field(
        default=None,
        description="Endjahr (optional), z.B. 2025",
        ge=1880,
        le=2100,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Router erstellen
# prefix="/api/v1/ingestion" → Alle Endpoints beginnen mit diesem Pfad
# tags=["Data Ingestion"]    → Gruppierung in der API-Dokumentation
# ─────────────────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["Data Ingestion"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 1: POST /api/v1/ingestion/trigger
# Startet einen neuen Ingestion-Job für eine Datenquelle.
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/trigger",
    status_code=202,  # 202 Accepted: Request akzeptiert, Job läuft im Hintergrund
    summary="Ingestion-Job starten",
    description=(
        "Startet asynchron einen neuen Datenabruf-Job für eine konfigurierte "
        "Klimadatenquelle. Gibt sofort eine Job-ID zurück, mit der der Status "
        "abgefragt werden kann."
    ),
    response_description="Job wurde erstellt und läuft im Hintergrund",
)
async def trigger_ingestion(
    request: IngestionTriggerRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Startet einen asynchronen Ingestion-Job.

    Was bedeutet "asynchron"?
    Der Datendownload von NASA kann mehrere Sekunden dauern.
    Statt den Client warten zu lassen, gibt dieser Endpoint sofort eine
    Job-ID zurück. Der Download läuft im Hintergrund weiter.
    Der Client kann dann GET /jobs/{job_id} aufrufen, um den Status zu prüfen.

    HTTP Status 202 Accepted: "Ich habe deinen Auftrag angenommen und
    bearbeite ihn" — im Gegensatz zu 200 OK ("Ich bin fertig").
    """
    logger.info("Ingestion-Trigger für Quelle '%s'", request.source_id)

    # Prüfen ob die angeforderte Quelle bekannt ist
    if request.source_id not in _available_sources:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Unbekannte Datenquelle: '{request.source_id}'. "
                f"Verfügbare Quellen: {list(_available_sources.keys())}"
            ),
        )

    # Neuen Job erstellen
    job = IngestionJob(
        job_id=str(uuid.uuid4()),
        source_id=request.source_id,
        status="pending",
        started_at=datetime.now(timezone.utc),
        parameters={
            "start_year": request.start_year,
            "end_year": request.end_year,
        },
    )

    # Job im Speicher ablegen
    _jobs_store[job.job_id] = job

    # Den eigentlichen Download als Hintergrundaufgabe registrieren.
    # background_tasks.add_task() führt die Funktion NACH dem Response aus.
    # So bekommt der Client die Job-ID sofort, ohne auf den Download warten.
    background_tasks.add_task(
        _run_ingestion_job,
        job_id=job.job_id,
        source_id=request.source_id,
        start_year=request.start_year,
        end_year=request.end_year,
    )

    logger.info("Job erstellt: job_id=%s", job.job_id)

    return {
        "job_id": job.job_id,
        "status": job.status,
        "source_id": job.source_id,
        "message": (
            f"Ingestion-Job gestartet. Status abrufbar unter: "
            f"/api/v1/ingestion/jobs/{job.job_id}"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 2: GET /api/v1/ingestion/jobs/{job_id}
# Gibt den Status eines laufenden oder abgeschlossenen Jobs zurück.
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/jobs/{job_id}",
    summary="Job-Status abrufen",
    description="Gibt den aktuellen Status eines Ingestion-Jobs zurück.",
)
async def get_job_status(
    job_id: str = Path(
        description="UUID des Jobs, z.B. 'a1b2c3d4-e5f6-...'",
        example="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    ),
) -> IngestionJob:
    """
    Gibt den Status und Details eines Ingestion-Jobs zurück.

    Was ist ein Path-Parameter?
    In der URL /jobs/{job_id} ist {job_id} ein Platzhalter.
    FastAPI extrahiert automatisch den Wert aus der URL.
    Aufruf: GET /api/v1/ingestion/jobs/a1b2c3d4-... → job_id = "a1b2c3d4-..."
    """
    if job_id not in _jobs_store:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' nicht gefunden.",
        )

    return _jobs_store[job_id]


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 3: GET /api/v1/ingestion/datasets
# Listet alle verfügbaren (ingesierten) Datensätze auf.
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/datasets",
    summary="Alle Datensätze auflisten",
    description=(
        "Gibt eine Liste aller erfolgreich ingesierten Klimadatensätze zurück. "
        "Kann nach Variable und Anbieter gefiltert werden."
    ),
)
async def list_datasets(
    variable: Optional[str] = Query(
        default=None,
        description="Filter nach Klimavariable, z.B. 'surface_temperature_anomaly'",
    ),
    provider: Optional[str] = Query(
        default=None,
        description="Filter nach Datenanbieter, z.B. 'NASA'",
    ),
) -> Dict[str, Any]:
    """
    Listet alle verfügbaren Klimadatensätze.

    Was ist ein Query-Parameter?
    Query-Parameter stehen in der URL nach einem '?':
    GET /datasets?variable=surface_temperature_anomaly&provider=NASA
    Sie sind optional und dienen der Filterung/Suche.

    Returns:
        Liste von Datensatz-Metadaten (ohne die eigentlichen Messwerte,
        da diese groß sein können).
    """
    datasets = list(_datasets_store.values())

    # Optionaler Filter nach Variable
    if variable:
        datasets = [d for d in datasets if d.variable == variable]

    # Optionaler Filter nach Anbieter
    if provider:
        datasets = [
            d for d in datasets
            if provider.lower() in d.source.provider.lower()
        ]

    # Metadaten zurückgeben (records nicht mitschicken — zu groß)
    return {
        "total": len(datasets),
        "datasets": [
            {
                "dataset_id": d.dataset_id,
                "variable": d.variable,
                "description": d.description,
                "provider": d.source.provider,
                "doi": d.source.doi,
                "record_count": d.record_count,
                "temporal_coverage_start": (
                    d.temporal_coverage_start.isoformat()
                    if d.temporal_coverage_start else None
                ),
                "temporal_coverage_end": (
                    d.temporal_coverage_end.isoformat()
                    if d.temporal_coverage_end else None
                ),
            }
            for d in datasets
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 4: GET /api/v1/ingestion/datasets/{dataset_id}/data
# Gibt die tatsächlichen Messdaten eines Datensatzes zurück.
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/datasets/{dataset_id}/data",
    summary="Datensatz-Messwerte abrufen",
    description=(
        "Gibt die Messwerte (DataPoints) eines bestimmten Datensatzes zurück. "
        "Unterstützt Pagination und Zeitraumfilterung."
    ),
)
async def get_dataset_data(
    dataset_id: str = Path(
        description="ID des Datensatzes, z.B. 'nasa_giss_surface_temp_v4'",
    ),
    start_year: Optional[int] = Query(
        default=None,
        description="Nur Daten ab diesem Jahr",
        ge=1880,
    ),
    end_year: Optional[int] = Query(
        default=None,
        description="Nur Daten bis zu diesem Jahr",
        le=2100,
    ),
    limit: int = Query(
        default=100,
        description="Maximale Anzahl zurückgegebener Datenpunkte (Pagination)",
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        description="Wie viele Datenpunkte überspringen (Pagination)",
        ge=0,
    ),
) -> Dict[str, Any]:
    """
    Gibt Messwerte eines Datensatzes zurück.

    Was ist Pagination?
    Wenn ein Datensatz 150 Jahre Daten enthält (1800+ Punkte), ist es
    ineffizient, alles auf einmal zu schicken. Mit limit und offset kann
    der Client die Daten in Seiten abrufen:
    - limit=10, offset=0  → Punkte 1–10
    - limit=10, offset=10 → Punkte 11–20
    - usw.
    """
    if dataset_id not in _datasets_store:
        raise HTTPException(
            status_code=404,
            detail=f"Datensatz '{dataset_id}' nicht gefunden.",
        )

    dataset = _datasets_store[dataset_id]
    records = dataset.records

    # Zeitraumfilterung
    if start_year:
        records = [r for r in records if r.timestamp.year >= start_year]
    if end_year:
        records = [r for r in records if r.timestamp.year <= end_year]

    total_count = len(records)

    # Pagination anwenden
    records_page = records[offset: offset + limit]

    return {
        "dataset_id": dataset_id,
        "variable": dataset.variable,
        "unit": records_page[0].unit if records_page else None,
        "total_records": total_count,
        "limit": limit,
        "offset": offset,
        "records": [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": r.value,
                "unit": r.unit,
                "quality_flag": r.quality_flag,
            }
            for r in records_page
        ],
        "source": {
            "provider": dataset.source.provider,
            "doi": dataset.source.doi,
            "citation": dataset.source.citation,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint 5: GET /api/v1/ingestion/sources
# Listet alle konfigurierten (verfügbaren) Datenquellen auf.
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/sources",
    summary="Verfügbare Datenquellen auflisten",
    description="Gibt alle konfigurierten Klimadatenquellen zurück.",
)
async def list_sources() -> Dict[str, Any]:
    """
    Gibt alle konfigurierten Datenquellen zurück.

    Unterschied zu /datasets:
    - /sources → konfigurierte Quellen (auch noch nicht abgerufene)
    - /datasets → tatsächlich abgerufene und gespeicherte Datensätze
    """
    return {
        "total": len(_available_sources),
        "sources": list(_available_sources.values()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Interne Hilfsfunktion: _run_ingestion_job
# Wird von BackgroundTasks aufgerufen — läuft im Hintergrund.
# NICHT als Endpoint erreichbar (kein @router.get/post Decorator).
# ─────────────────────────────────────────────────────────────────────────────
async def _run_ingestion_job(
    job_id: str,
    source_id: str,
    start_year: Optional[int],
    end_year: Optional[int],
) -> None:
    """
    Führt den eigentlichen Datenabruf für einen Job aus.

    Was passiert hier?
    Diese Funktion wird von FastAPI im Hintergrund ausgeführt,
    nachdem der Endpoint dem Client bereits geantwortet hat.
    Sie aktualisiert den Job-Status in _jobs_store, damit der Client
    über GET /jobs/{job_id} den Fortschritt verfolgen kann.

    Args:
        job_id: ID des zu aktualisierenden Jobs.
        source_id: ID der Datenquelle ("nasa_giss", ...).
        start_year: Optionales Startjahr.
        end_year: Optionales Endjahr.
    """
    job = _jobs_store[job_id]

    try:
        # Job als "laufend" markieren
        _jobs_store[job_id] = job.model_copy(
            update={"status": "running"}
        )
        logger.info("Job %s gestartet (source=%s)", job_id, source_id)

        # ── Daten abrufen (nach Quelle unterscheiden) ───────────────────────
        dataset: Optional[ClimateDataset] = None

        if source_id == "nasa_giss":
            connector = NasaGissConnector()
            dataset = connector.fetch_dataset(
                start_year=start_year,
                end_year=end_year,
            )
        else:
            # Andere Quellen werden in zukünftigen Aufgaben implementiert.
            raise NotImplementedError(
                f"Connector für '{source_id}' ist noch nicht implementiert."
            )

        # Datensatz im Speicher ablegen
        _datasets_store[dataset.dataset_id] = dataset

        # Job als "abgeschlossen" markieren
        _jobs_store[job_id] = job.model_copy(
            update={
                "status": "completed",
                "completed_at": datetime.now(timezone.utc),
                "records_fetched": dataset.record_count,
                "dataset_id": dataset.dataset_id,
            }
        )
        logger.info(
            "Job %s abgeschlossen: %d Datenpunkte in '%s'",
            job_id, dataset.record_count, dataset.dataset_id,
        )

    except Exception as exc:
        # Bei JEDEM Fehler: Job als "failed" markieren und Fehler loggen.
        # Fehler werden NIEMALS still ignoriert. (Projektregeln)
        error_msg = f"{type(exc).__name__}: {str(exc)}"
        logger.error("Job %s fehlgeschlagen: %s", job_id, error_msg)

        _jobs_store[job_id] = job.model_copy(
            update={
                "status": "failed",
                "completed_at": datetime.now(timezone.utc),
                "error_message": error_msg,
            }
        )