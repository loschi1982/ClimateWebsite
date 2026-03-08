# backend/api/v1/analysis.py
"""
FastAPI-Router für Analyse-Endpunkte (CA-05, CA-06, CA-07)
Verantwortlich: Climate Analysis Team
Branch: team/climate-analysis

Implementiert:
  GET /api/v1/analysis/trend
  GET /api/v1/analysis/correlation
  GET /api/v1/analysis/anomalies

Alle Endpunkte entsprechen dem API-Vertrag in docs/api_contracts.md.
Dieser Router darf NICHT eigenständig geändert werden (Zustimmung aller Teams
erforderlich, siehe api_contracts.md → Regeln für API-Änderungen).
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from modules.climate_analysis.analysis import (
    compute_anomalies,
    compute_correlation,
    compute_trend,
)
from modules.data_ingestion.cache import load_dataset  # Data Pipeline Team

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])

# API-Version wird in jeder Antwort mitgeliefert (Vertrag)
API_VERSION = "v1"


# ---------------------------------------------------------------------------
# CA-05: GET /api/v1/analysis/trend
# ---------------------------------------------------------------------------

@router.get("/trend")
async def get_trend(
    source: Annotated[str, Query(description="Datenquelle (z. B. 'nasa', 'noaa')")],
    variable: Annotated[str, Query(description="Klimavariable (z. B. 'temperature')")],
    start: Annotated[str, Query(description="Startdatum ISO (z. B. '1980-01-01')")],
    end: Annotated[str, Query(description="Enddatum ISO (z. B. '2024-12-31')")],
) -> dict:
    """
    Berechnet den linearen Trend eines Klimadatensatzes.

    Gibt Trend pro Jahrzehnt, R², p-Wert und Interpretation zurück.
    Entspricht dem TrendResult-Format aus api_contracts.md.
    """
    dataset = _load_or_404(source, variable)

    try:
        result = compute_trend(dataset, start, end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "version": API_VERSION,
        "source": source,
        **result,
    }


# ---------------------------------------------------------------------------
# CA-06: GET /api/v1/analysis/correlation
# ---------------------------------------------------------------------------

@router.get("/correlation")
async def get_correlation(
    source_a: Annotated[str, Query(description="Quelle Variable A")],
    variable_a: Annotated[str, Query(description="Variable A")],
    source_b: Annotated[str, Query(description="Quelle Variable B")],
    variable_b: Annotated[str, Query(description="Variable B")],
    start: Annotated[str, Query(description="Startdatum ISO")],
    end: Annotated[str, Query(description="Enddatum ISO")],
) -> dict:
    """
    Berechnet die Pearson-Korrelation zwischen zwei Klimavariablen.

    Beide Datensätze werden auf gemeinsame Datenpunkte (inner join) reduziert.
    Entspricht dem CorrelationResult-Format aus api_contracts.md.
    """
    dataset_a = _load_or_404(source_a, variable_a)
    dataset_b = _load_or_404(source_b, variable_b)

    try:
        result = compute_correlation(dataset_a, dataset_b, start, end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "version": API_VERSION,
        **result,
    }


# ---------------------------------------------------------------------------
# CA-07: GET /api/v1/analysis/anomalies
# ---------------------------------------------------------------------------

@router.get("/anomalies")
async def get_anomalies(
    source: Annotated[str, Query(description="Datenquelle")],
    variable: Annotated[str, Query(description="Klimavariable")],
    start: Annotated[str, Query(description="Startdatum ISO")],
    end: Annotated[str, Query(description="Enddatum ISO")],
    ref_start: Annotated[str, Query(description="Referenzzeitraum Start")] = "1951-01-01",
    ref_end: Annotated[str, Query(description="Referenzzeitraum Ende")] = "1980-12-31",
) -> dict:
    """
    Berechnet Anomalien gegenüber einem Referenzzeitraum.

    Standard-Referenzzeitraum: 1951–1980 (NASA GISS Konvention).
    Entspricht dem AnomalyResult-Format aus api_contracts.md.
    """
    dataset = _load_or_404(source, variable)

    try:
        result = compute_anomalies(dataset, start, end, ref_start, ref_end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "version": API_VERSION,
        "source": source,
        **result,
    }


# ---------------------------------------------------------------------------
# Hilfsfunktion: Datensatz laden oder 404 werfen
# ---------------------------------------------------------------------------

def _load_or_404(source: str, variable: str) -> dict:
    """
    Lädt einen Datensatz über den Cache des Data Pipeline Teams.
    Wirft HTTP 404, wenn der Datensatz nicht gefunden wird.
    Wirft HTTP 503, wenn die externe Quelle nicht erreichbar war.

    Args:
        source:   Datenquellen-ID (z. B. 'nasa').
        variable: Klimavariable (z. B. 'temperature').

    Returns:
        Normalisierter Datensatz.
    """
    try:
        return load_dataset(source, variable)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Datensatz nicht gefunden: Quelle '{source}', Variable '{variable}'. "
                   "Bitte zuerst /api/v1/data aufrufen.",
        ) from exc
    except ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Externe Datenquelle '{source}' nicht erreichbar: {exc}",
        ) from exc