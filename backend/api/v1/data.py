"""
DP-06 / DP-07: FastAPI-Router für Klimadaten-Endpunkte.

Implementiert:
  GET /api/v1/data          – Datensatz abrufen
  GET /api/v1/data/sources  – Verfügbare Quellen auflisten

Die Endpunkte entsprechen exakt dem API-Vertrag in docs/api_contracts.md.
Änderungen an diesem Vertrag nur per Pull Request mit Zustimmung aller Teams.
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from backend.modules.data_ingestion.service import DataIngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["Klimadaten"])

# Service-Instanz (in Produktion via Dependency Injection übergeben)
_service = DataIngestionService()

# API-Versionsnummer (wird in jede Antwort eingebettet)
_API_VERSION = "v1"


@router.get("/sources", summary="Verfügbare Datenquellen und Variablen")
def get_sources():
    """
    Gibt alle verfügbaren Datenquellen und deren Variablen zurück.

    Entspricht dem Vertrag:
        GET /api/v1/data/sources
    """
    sources = _service.get_sources()
    return {
        "version": _API_VERSION,
        "sources": sources,
    }


@router.get("", summary="Klimadatensatz abrufen")
def get_data(
    source: str = Query(..., description="Datenquelle, z.B. 'nasa', 'noaa', 'nsidc'"),
    variable: str = Query(..., description="Klimavariable, z.B. 'temperature', 'co2'"),
    start: str = Query(..., description="Startdatum im Format YYYY-MM-DD", example="1980-01-01"),
    end: str = Query(..., description="Enddatum im Format YYYY-MM-DD", example="2024-12-31"),
):
    """
    Gibt einen Klimadatensatz für die angegebene Quelle und Variable zurück,
    gefiltert auf den gewünschten Zeitraum.

    Entspricht dem Vertrag:
        GET /api/v1/data?source=nasa&variable=temperature&start=1980-01-01&end=2024-12-31
    """
    # Einfache Datumsformat-Prüfung (ausführliche Validierung im Service)
    for date_str, label in [(start, "start"), (end, "end")]:
        if not _is_valid_date_format(date_str):
            raise HTTPException(
                status_code=400,
                detail={
                    "code": 400,
                    "message": f"Ungültiges Datumsformat für '{label}'.",
                    "detail": f"Erwartet: 'YYYY-MM-DD', erhalten: '{date_str}'",
                },
            )

    if start > end:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 400,
                "message": "Ungültiger Zeitraum.",
                "detail": f"'start' ({start}) muss vor 'end' ({end}) liegen.",
            },
        )

    try:
        dataset = _service.get_dataset(
            source=source,
            variable=variable,
            start=start,
            end=end,
        )
    except ValueError as exc:
        # Unbekannte Quelle oder Variable
        raise HTTPException(
            status_code=400,
            detail={
                "code": 400,
                "message": "Ungültige Quelle oder Variable.",
                "detail": str(exc),
            },
        ) from exc
    except RuntimeError as exc:
        # Validierungsfehler
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": "Daten konnten nicht validiert werden.",
                "detail": str(exc),
            },
        ) from exc
    except Exception as exc:
        # Netzwerkfehler oder externe Quelle nicht erreichbar
        logger.exception(f"Fehler beim Datenabruf: {source}/{variable}")
        raise HTTPException(
            status_code=503,
            detail={
                "code": 503,
                "message": "Externe Datenquelle nicht erreichbar.",
                "detail": str(exc),
            },
        ) from exc

    if not dataset.get("data"):
        raise HTTPException(
            status_code=404,
            detail={
                "code": 404,
                "message": "Datensatz nicht gefunden.",
                "detail": (
                    f"Keine Daten für source='{source}', variable='{variable}' "
                    f"im Zeitraum {start}–{end}."
                ),
            },
        )

    # Antwort im API-Vertragsformat aufbauen
    response = {
        "version": _API_VERSION,
        "source": dataset["source"],
        "variable": dataset["variable"],
        "unit": dataset["unit"],
        "data": dataset["data"],
        "metadata": dataset["metadata"],
    }
    # Optionales Feld (nur bei Temperaturdaten vorhanden)
    if "reference_period" in dataset:
        response["reference_period"] = dataset["reference_period"]

    return response


def _is_valid_date_format(date_str: str) -> bool:
    """
    Prüft, ob ein String dem Format 'YYYY-MM-DD' entspricht.

    Args:
        date_str: Zu prüfender String.

    Returns:
        True, wenn das Format korrekt ist.
    """
    import re
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))