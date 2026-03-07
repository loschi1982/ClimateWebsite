"""
ClimateInsight — Knowledge Base API Router
services/api_gateway/src/routers/knowledge.py

Implementiert alle 3 Endpoints aus api_contracts.md:
  POST /api/v1/knowledge/entries
  GET  /api/v1/knowledge/search
  GET  /api/v1/knowledge/entries/{entry_id}

Owner:    Data Pipeline Team (Schema), AI Explanation Team (Schreibzugriff)
Consumer: AI Explanation Team, Frontend Team

Hinweis: Semantische Suche ist in Phase 1 eine Keyword-Suche (Platzhalter).
         In Phase 2 wird LlamaIndex + Embedding-Suche integriert.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

router   = APIRouter(prefix="/knowledge", tags=["Knowledge"])
security = HTTPBearer()


# ---------------------------------------------------------------------------
# In-Memory-Speicher (Phase 1 — wird in Phase 2 durch PostgreSQL ersetzt)
# ---------------------------------------------------------------------------

_entries: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Hilfsroutinen
# ---------------------------------------------------------------------------

def _meta() -> dict:
    return {
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "version":    "1.0",
        "request_id": f"req_{uuid.uuid4().hex[:8]}",
    }

def _ok(data: dict) -> dict:
    return {"status": "ok", "data": data, "meta": _meta()}

def _error(code: str, message: str, http_status: int) -> HTTPException:
    return HTTPException(
        status_code=http_status,
        detail={"status": "error", "error": {"code": code, "message": message}, "meta": _meta()},
    )


# ---------------------------------------------------------------------------
# Request-Modell
# ---------------------------------------------------------------------------

class SourceRef(BaseModel):
    """Quellenangabe innerhalb eines Wissensbasis-Eintrags."""
    source_id:   Optional[str] = None
    provider:    Optional[str] = None
    citation:    str
    doi:         Optional[str] = None
    url:         str
    accessed_at: Optional[str] = None


class CreateEntryRequest(BaseModel):
    """Request-Body für POST /knowledge/entries"""
    title:                str
    content:              str
    topic:                str
    supporting_analyses:  list[str]    = []
    supporting_datasets:  list[str]    = []
    sources:              list[SourceRef] = []
    tags:                 list[str]    = []


# ---------------------------------------------------------------------------
# POST /api/v1/knowledge/entries
# ---------------------------------------------------------------------------

@router.post(
    "/entries",
    status_code=201,
    summary="Wissensbasis-Eintrag erstellen",
    description="Erstellt einen neuen Eintrag in der Wissensbasis.",
)
async def create_entry(
    req: CreateEntryRequest,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    entry_id = f"ke_{uuid.uuid4().hex[:6]}"
    now      = datetime.now(timezone.utc).isoformat()

    entry = {
        "entry_id":             entry_id,
        "title":                req.title,
        "content":              req.content,
        "topic":                req.topic,
        "supporting_analyses":  req.supporting_analyses,
        "supporting_datasets":  req.supporting_datasets,
        "sources":              [s.model_dump() for s in req.sources],
        "tags":                 req.tags,
        "created_at":           now,
        "updated_at":           now,
    }
    _entries[entry_id] = entry

    return _ok({"entry_id": entry_id, "created_at": now})


# ---------------------------------------------------------------------------
# GET /api/v1/knowledge/search
# ---------------------------------------------------------------------------

@router.get(
    "/search",
    summary="Semantische Suche in der Wissensbasis",
    description=(
        "Phase 1: Keyword-Suche in Titel und Inhalt. "
        "Phase 2: Embedding-basierte semantische Suche via LlamaIndex."
    ),
)
async def search_entries(
    q:     str           = Query(..., description="Suchanfrage"),
    topic: Optional[str] = Query(None, description="Themenfilter"),
    limit: int           = Query(10, ge=1, le=100),
):
    query_lower = q.lower()
    results = []

    for entry in _entries.values():
        # Phase-1-Suche: Keyword-Match in Titel + Inhalt
        text = (entry["title"] + " " + entry["content"]).lower()
        if query_lower not in text:
            continue
        if topic and entry.get("topic") != topic:
            continue

        # Einfache Relevanzbewertung: wie oft kommt der Begriff vor?
        occurrences = text.count(query_lower)
        score = min(1.0, occurrences * 0.1 + 0.5)

        results.append({
            "entry_id":        entry["entry_id"],
            "title":           entry["title"],
            "summary":         entry["content"][:200] + "...",
            "topic":           entry["topic"],
            "relevance_score": round(score, 2),
            "tags":            entry["tags"],
        })

    # Nach Relevanz sortieren
    results.sort(key=lambda r: r["relevance_score"], reverse=True)
    paged = results[:limit]

    return _ok({"results": paged, "total": len(results)})


# ---------------------------------------------------------------------------
# GET /api/v1/knowledge/entries/{entry_id}
# ---------------------------------------------------------------------------

@router.get(
    "/entries/{entry_id}",
    summary="Einzelnen Wissensbasis-Eintrag abrufen",
)
async def get_entry(entry_id: str):
    if entry_id not in _entries:
        raise _error("NOT_FOUND", f"Eintrag '{entry_id}' nicht gefunden.", 404)

    return _ok(_entries[entry_id])