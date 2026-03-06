# API-Verträge — ClimateInsight
## Version 1.0 | Zentrales Dokument | Gültig für alle Teams

---

> **Verbindlichkeit:** Alle Teams sind an diese API-Verträge gebunden.
> Änderungen erfordern einen Eintrag in `project_memory.json` (Kategorie: `api_definitions`)
> und müssen mit allen betroffenen Consumer-Teams abgestimmt werden.

---

## Globale Konventionen

```
Base URL:       /api/v1
Format:         application/json (UTF-8)
Versionierung:  URL-Pfad (/api/v1/, /api/v2/)
Authentifizierung: Bearer JWT (alle schreibenden Endpoints)
Rate Limiting:  100 req/min (public), 1000 req/min (intern)
```

### Standard-Response-Hülle

```json
// Erfolg
{
  "status": "ok",
  "data": { ... },
  "meta": {
    "timestamp": "2026-03-05T10:00:00Z",
    "version": "1.0",
    "request_id": "req_abc123"
  }
}

// Fehler
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Menschenlesbare Beschreibung",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2026-03-05T10:00:00Z",
    "request_id": "req_abc123"
  }
}
```

### HTTP-Statuscodes und Fehlercodes

| HTTP | Code | Bedeutung |
|------|------|-----------|
| 200 | — | Erfolg |
| 201 | — | Ressource erstellt |
| 202 | — | Asynchroner Job gestartet |
| 400 | INVALID_REQUEST | Syntaktisch ungültige Anfrage |
| 401 | UNAUTHORIZED | Kein oder ungültiges Token |
| 403 | FORBIDDEN | Keine Berechtigung |
| 404 | NOT_FOUND | Ressource nicht gefunden |
| 409 | CONFLICT | Ressource existiert bereits |
| 422 | VALIDATION_ERROR | Semantisch ungültige Eingabe |
| 429 | RATE_LIMITED | Zu viele Anfragen |
| 500 | INTERNAL_ERROR | Unerwarteter Serverfehler |
| 503 | SERVICE_UNAVAILABLE | Modul nicht erreichbar |

---

## Gemeinsame Datentypen

```typescript
// Zeitreihen-Datenpunkt
interface DataPoint {
  timestamp: string;    // ISO8601, z.B. "1980-01-01T00:00:00Z"
  value: number;
  unit: string;         // z.B. "°C", "mm", "ppm"
  quality_flag: "good" | "estimated" | "questionable" | "missing";
}

// Klimavariable
type ClimateVariable =
  | "surface_temperature_anomaly"
  | "sea_level_change"
  | "sea_ice_extent"
  | "co2_concentration"
  | "arctic_ice_volume"
  | "precipitation_anomaly"
  | "ocean_heat_content";

// Quellenverweis
interface SourceReference {
  source_id: string;      // z.B. "nasa_giss_surface_temp_v4"
  provider: string;       // z.B. "NASA"
  citation: string;       // Vollständige Zitation
  doi?: string;
  url: string;
  accessed_at: string;    // ISO8601
}

// Datensatz-Referenz
interface DatasetRef {
  id: string;
  variable: ClimateVariable;
  temporal_coverage: { start: string; end: string };
  spatial_coverage: "global" | "regional" | string;
  resolution: "daily" | "monthly" | "annual";
  unit: string;
  source: SourceReference;
}

// Analyse-Status
type JobStatus = "queued" | "running" | "completed" | "failed";

// Artikel-Status
type ArticleStatus = "pending_review" | "in_review" | "approved" | "published" | "rejected";
```

---

## Modul 1: Data Ingestion API

**Owner:** Data Pipeline Team
**Consumer:** Climate Analysis Team, Visualization Team, Frontend Team

---

### POST /api/v1/ingestion/trigger

Startet einen Datenabruf für eine Quelle.

**Request:**
```json
{
  "source_id": "nasa_giss_surface_temp",
  "date_range": {
    "start": "2000-01-01",
    "end": "2025-12-31"
  },
  "force_refresh": false
}
```

**Response 202:**
```json
{
  "status": "ok",
  "data": {
    "job_id": "job_abc123",
    "source_id": "nasa_giss_surface_temp",
    "status": "queued",
    "estimated_completion_seconds": 120
  }
}
```

**Fehlercodes:**
- `VALIDATION_ERROR` — Ungültiger Datumsbereich oder unbekannte source_id
- `SOURCE_UNAVAILABLE` — Externe Quelle nicht erreichbar
- `JOB_ALREADY_RUNNING` — Bereits laufender Job für diese Quelle

---

### GET /api/v1/ingestion/jobs/{job_id}

Status eines Abrufjobs.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "job_id": "job_abc123",
    "source_id": "nasa_giss_surface_temp",
    "status": "completed",
    "started_at": "2026-03-05T10:00:00Z",
    "completed_at": "2026-03-05T10:02:15Z",
    "records_ingested": 1728,
    "dataset_id": "nasa_giss_surface_temp_v4_20260305",
    "quality_report": {
      "missing_values": 0,
      "out_of_range_values": 0,
      "duplicate_records": 0,
      "overall_quality": "good"
    },
    "error": null
  }
}
```

---

### GET /api/v1/ingestion/datasets

Listet alle verfügbaren normalisierten Datensätze.

**Query-Parameter:**
```
variable:   ClimateVariable   (optional, Filter)
provider:   string            (optional, z.B. "NASA")
from:       ISO8601-Date      (optional)
to:         ISO8601-Date      (optional)
```

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "datasets": [
      {
        "id": "nasa_giss_surface_temp_v4",
        "variable": "surface_temperature_anomaly",
        "provider": "NASA",
        "temporal_coverage": {
          "start": "1880-01-01",
          "end": "2025-12-31"
        },
        "spatial_coverage": "global",
        "resolution": "monthly",
        "unit": "°C",
        "records": 1728,
        "citation": "GISTEMP Team (2024): GISS Surface Temperature Analysis (GISTEMP v4). NASA Goddard Institute for Space Studies.",
        "doi": "10.7289/V5MGNM48",
        "url": "https://data.giss.nasa.gov/gistemp/",
        "last_updated": "2026-03-01T00:00:00Z",
        "quality": "good"
      }
    ],
    "total": 12
  }
}
```

---

### GET /api/v1/ingestion/datasets/{dataset_id}/data

Rohdaten eines Datensatzes abrufen.

**Query-Parameter:**
```
from:       ISO8601-Date      (optional)
to:         ISO8601-Date      (optional)
limit:      int               (default: 1000, max: 10000)
offset:     int               (default: 0)
```

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "dataset_id": "nasa_giss_surface_temp_v4",
    "variable": "surface_temperature_anomaly",
    "unit": "°C",
    "points": [
      {
        "timestamp": "1880-01-01T00:00:00Z",
        "value": -0.16,
        "quality_flag": "good"
      },
      {
        "timestamp": "1880-02-01T00:00:00Z",
        "value": -0.09,
        "quality_flag": "good"
      }
    ],
    "total_points": 1728,
    "returned_points": 100,
    "source": {
      "provider": "NASA",
      "citation": "GISTEMP Team (2024)...",
      "doi": "10.7289/V5MGNM48"
    }
  }
}
```

---

### GET /api/v1/ingestion/sources

Listet alle konfigurierten Datenquellen.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "sources": [
      {
        "id": "nasa_giss_surface_temp",
        "name": "GISS Surface Temperature Analysis (GISTEMP v4)",
        "provider": "NASA",
        "variables": ["surface_temperature_anomaly"],
        "update_frequency": "monthly",
        "status": "active",
        "last_successful_fetch": "2026-03-01T03:00:00Z"
      }
    ]
  }
}
```

---

## Modul 2: Climate Analysis API

**Owner:** Climate Analysis Team
**Consumer:** Visualization Team, Simulation Team, AI Explanation Team, Frontend Team

---

### POST /api/v1/analysis/run

Startet eine Klimaanalyse.

**Request:**
```json
{
  "dataset_id": "nasa_giss_surface_temp_v4",
  "analysis_type": "trend",
  "parameters": {
    "method": "linear",
    "confidence_level": 0.95,
    "time_range": {
      "start": "1960-01-01",
      "end": "2025-01-01"
    }
  }
}
```

**analysis_type Werte:**
```
trend        — Lineare/polynomiale Trendberechnung
anomaly      — Anomalieerkennung (z-Score, IQR)
correlation  — Kreuzkorrelation zweier Datensätze
decompose    — Zeitreihendekomposition (Trend + Saisonalität + Residual)
forecast     — Kurzfristige Projektion (max. 10 Jahre)
```

**Response 202:**
```json
{
  "status": "ok",
  "data": {
    "analysis_id": "ana_xyz789",
    "status": "queued",
    "estimated_seconds": 15
  }
}
```

---

### GET /api/v1/analysis/{analysis_id}

Ergebnis einer Analyse abrufen.

**Response 200 (type: trend):**
```json
{
  "status": "ok",
  "data": {
    "analysis_id": "ana_xyz789",
    "status": "completed",
    "dataset_id": "nasa_giss_surface_temp_v4",
    "analysis_type": "trend",
    "result": {
      "trend_slope": 0.019,
      "trend_slope_unit": "°C/year",
      "trend_total": 1.24,
      "trend_total_unit": "°C",
      "p_value": 0.0001,
      "r_squared": 0.94,
      "confidence_interval_95": [0.017, 0.021],
      "interpretation": "Signifikant steigender Trend",
      "time_range": {
        "start": "1960-01-01",
        "end": "2025-01-01"
      },
      "trend_series": [
        { "timestamp": "1960-01-01T00:00:00Z", "value": -0.12 },
        { "timestamp": "2025-01-01T00:00:00Z", "value": 1.12 }
      ]
    },
    "hypotheses": [
      {
        "id": "hyp_001",
        "statement": "Die globale Oberflächentemperatur zeigt seit 1960 einen statistisch signifikanten positiven Trend.",
        "confidence": 0.9999,
        "supporting_datasets": ["nasa_giss_surface_temp_v4"],
        "method": "OLS-Regression, p < 0.0001"
      }
    ],
    "methodology": {
      "method": "ordinary_least_squares",
      "library": "scipy.stats.linregress",
      "reference": "Montgomery et al. (2012)"
    },
    "computed_at": "2026-03-05T10:01:30Z"
  }
}
```

**Response 200 (type: correlation):**
```json
{
  "status": "ok",
  "data": {
    "analysis_id": "ana_cor001",
    "analysis_type": "correlation",
    "result": {
      "pearson_r": 0.87,
      "spearman_r": 0.84,
      "p_value": 0.0001,
      "lag_months": 0,
      "dataset_a": "nasa_giss_surface_temp_v4",
      "dataset_b": "noaa_co2_mauna_loa_v1",
      "interpretation": "Starke positive Korrelation"
    }
  }
}
```

---

### GET /api/v1/analysis/hypotheses

Alle generierten Hypothesen, optional gefiltert.

**Query-Parameter:**
```
topic:       string           (optional, z.B. "temperature")
min_confidence: float        (optional, 0.0–1.0)
dataset_id:  string          (optional)
```

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "hypotheses": [
      {
        "id": "hyp_001",
        "statement": "...",
        "confidence": 0.9999,
        "topic": "temperature",
        "supporting_datasets": ["nasa_giss_surface_temp_v4"],
        "analysis_id": "ana_xyz789",
        "created_at": "2026-03-05T10:01:30Z"
      }
    ],
    "total": 24
  }
}
```

---

### POST /api/v1/analysis/correlate

Startet eine Kreuzkorrelation zwischen zwei Datensätzen.

**Request:**
```json
{
  "dataset_a": "nasa_giss_surface_temp_v4",
  "dataset_b": "noaa_co2_mauna_loa_v1",
  "time_range": {
    "start": "1960-01-01",
    "end": "2025-01-01"
  },
  "max_lag_months": 24
}
```

**Response 202:** Wie `/analysis/run`

---

## Modul 3: Visualization API

**Owner:** Visualization Team
**Consumer:** Frontend Team, Exploration System

---

### POST /api/v1/viz/create

Erstellt eine Visualisierungskonfiguration.

**Request:**
```json
{
  "viz_type": "timeseries",
  "dataset_ids": ["nasa_giss_surface_temp_v4"],
  "analysis_id": "ana_xyz789",
  "config": {
    "x_axis": "time",
    "y_axis": "surface_temperature_anomaly",
    "time_range": {
      "start": "1880-01-01",
      "end": "2025-12-31"
    },
    "show_trend": true,
    "show_confidence_band": true,
    "color_scheme": "diverging_rdbu",
    "title": "Globale Temperaturanomalie 1880–2025",
    "show_source": true
  }
}
```

**viz_type Werte:**
```
timeseries    — Zeitreihendiagramm
map           — Geospatiale Karte
scatter       — Streudiagramm (zwei Variablen)
correlation   — Korrelationsmatrix
bar           — Balkendiagramm (z.B. Jahreswerte)
```

**Response 201:**
```json
{
  "status": "ok",
  "data": {
    "viz_id": "viz_def456",
    "viz_type": "timeseries",
    "spec_format": "vega-lite",
    "spec": { "...vollständige Vega-Lite Spec..." : "..." },
    "embed_url": "/embed/viz/viz_def456",
    "thumbnail_url": "/api/v1/viz/viz_def456/thumbnail",
    "export_urls": {
      "svg": "/api/v1/viz/viz_def456/export?format=svg",
      "png": "/api/v1/viz/viz_def456/export?format=png",
      "csv": "/api/v1/viz/viz_def456/export?format=csv"
    },
    "created_at": "2026-03-05T10:03:00Z"
  }
}
```

---

### GET /api/v1/viz/{viz_id}

Visualisierungsdaten abrufen.

**Response 200:** Wie Response bei `/viz/create`

---

### GET /api/v1/viz/{viz_id}/export

Visualisierung exportieren.

**Query-Parameter:**
```
format:   "svg" | "png" | "csv"   (required)
width:    int                     (optional, default: 1200, nur PNG/SVG)
height:   int                     (optional, default: 600, nur PNG/SVG)
```

**Response 200:** Binary (image/svg+xml, image/png, text/csv)

---

### GET /api/v1/viz/templates

Vordefinierte Visualisierungsvorlagen.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "templates": [
      {
        "id": "tpl_temperature_timeseries",
        "name": "Globale Temperaturentwicklung",
        "viz_type": "timeseries",
        "description": "Standarddiagramm für Temperaturanomalien",
        "default_config": { "..." : "..." }
      }
    ]
  }
}
```

---

## Modul 4: Simulation API

**Owner:** Simulation Team
**Consumer:** Frontend Team, Exploration System

---

### GET /api/v1/simulation/scenarios

Vordefinierte Klimaszenarien.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "scenarios": [
      {
        "id": "rcp_2_6",
        "name": "RCP 2.6 — Starke Emissionsreduktion",
        "description": "Globale Erwärmung unter 2°C bis 2100",
        "source": "IPCC AR6",
        "parameters": {
          "co2_trajectory": "declining_after_2030",
          "temperature_projection_2100": { "median": 1.5, "range": [1.0, 2.0] }
        }
      },
      {
        "id": "rcp_4_5",
        "name": "RCP 4.5 — Mittlere Emissionen"
      },
      {
        "id": "rcp_8_5",
        "name": "RCP 8.5 — Hohe Emissionen",
        "description": "Business-as-usual Szenario"
      }
    ]
  }
}
```

---

### POST /api/v1/simulation/run

Startet eine Simulation.

**Request:**
```json
{
  "scenario_id": "rcp_4_5",
  "custom_parameters": {
    "co2_reduction_start_year": 2030,
    "co2_annual_reduction_percent": 3.0
  },
  "base_dataset_id": "nasa_giss_surface_temp_v4",
  "time_horizon_years": 75,
  "variable": "surface_temperature_anomaly"
}
```

**Response 202:**
```json
{
  "status": "ok",
  "data": {
    "simulation_id": "sim_mno789",
    "status": "running",
    "estimated_seconds": 5
  }
}
```

---

### GET /api/v1/simulation/{simulation_id}

Simulationsergebnis abrufen.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "simulation_id": "sim_mno789",
    "status": "completed",
    "scenario_id": "rcp_4_5",
    "result": {
      "projection_series": [
        {
          "timestamp": "2026-01-01T00:00:00Z",
          "value_median": 1.3,
          "value_lower_95": 1.1,
          "value_upper_95": 1.5,
          "unit": "°C"
        }
      ],
      "key_milestones": [
        {
          "year": 2052,
          "event": "Überschreitung 1.5°C Marke (Median)",
          "probability": 0.67
        }
      ],
      "simplification_notes": [
        "Dieses Modell ist didaktisch vereinfacht. Es basiert auf IPCC AR6 Projektionsdaten, bildet aber keine vollständige Klimadynamik ab."
      ]
    },
    "computed_at": "2026-03-05T10:05:00Z"
  }
}
```

---

### GET /api/v1/simulation/parameters

Verfügbare Parameter für eigene Szenarien.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "parameters": [
      {
        "id": "co2_annual_reduction_percent",
        "label": "CO₂-Reduktion pro Jahr (%)",
        "type": "float",
        "min": 0.0,
        "max": 15.0,
        "default": 0.0,
        "unit": "%/Jahr"
      },
      {
        "id": "co2_reduction_start_year",
        "label": "Startjahr der Reduktion",
        "type": "int",
        "min": 2026,
        "max": 2050,
        "default": 2030
      }
    ]
  }
}
```

---

## Modul 5: Knowledge Base API

**Owner:** Knowledge Base (Data Pipeline Team pflegt Schema, AI Team schreibt)
**Consumer:** AI Explanation Team, Frontend Team

---

### POST /api/v1/knowledge/entries

Erstellt einen Wissensbasis-Eintrag.

**Request:**
```json
{
  "title": "Globale Erwärmung seit 1880",
  "content": "Die globale Mitteltemperatur ist seit 1880 um approximately 1.2°C gestiegen...",
  "topic": "temperature",
  "supporting_analyses": ["ana_xyz789"],
  "supporting_datasets": ["nasa_giss_surface_temp_v4"],
  "sources": [
    {
      "citation": "GISTEMP Team (2024)...",
      "doi": "10.7289/V5MGNM48",
      "url": "https://data.giss.nasa.gov/gistemp/"
    }
  ],
  "tags": ["temperature", "global_warming", "trend"]
}
```

**Response 201:**
```json
{
  "status": "ok",
  "data": {
    "entry_id": "ke_001",
    "created_at": "2026-03-05T10:06:00Z"
  }
}
```

---

### GET /api/v1/knowledge/search

Semantische Suche in der Wissensbasis.

**Query-Parameter:**
```
q:       string   (required, Suchanfrage)
topic:   string   (optional)
limit:   int      (default: 10)
```

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "results": [
      {
        "entry_id": "ke_001",
        "title": "Globale Erwärmung seit 1880",
        "summary": "...",
        "topic": "temperature",
        "relevance_score": 0.94,
        "tags": ["temperature", "global_warming"]
      }
    ],
    "total": 3
  }
}
```

---

### GET /api/v1/knowledge/entries/{entry_id}

Einzelnen Eintrag abrufen.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "entry_id": "ke_001",
    "title": "Globale Erwärmung seit 1880",
    "content": "...",
    "topic": "temperature",
    "supporting_analyses": ["ana_xyz789"],
    "supporting_datasets": ["nasa_giss_surface_temp_v4"],
    "sources": [ { "..." : "..." } ],
    "tags": ["temperature", "global_warming", "trend"],
    "created_at": "2026-03-05T10:06:00Z",
    "updated_at": "2026-03-05T10:06:00Z"
  }
}
```

---

## Modul 6: AI Explanation API

**Owner:** AI Explanation Team
**Consumer:** Frontend Team, Admin/Review Interface

---

### POST /api/v1/explain/generate

Generiert einen Artikelentwurf.

**Request:**
```json
{
  "topic": "Globale Temperaturentwicklung seit 1880",
  "knowledge_entry_ids": ["ke_001", "ke_002"],
  "analysis_ids": ["ana_xyz789"],
  "audience": "general",
  "language": "de",
  "target_word_count": 800
}
```

**Response 202:**
```json
{
  "status": "ok",
  "data": {
    "article_id": "art_ghi012",
    "status": "pending_review"
  }
}
```

---

### GET /api/v1/explain/articles/{article_id}

Artikelentwurf abrufen.

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "article_id": "art_ghi012",
    "status": "pending_review",
    "title": "125 Jahre Erderwärmung: Was die Daten zeigen",
    "content": "...",
    "summary": "...",
    "key_findings": [
      "Die globale Mitteltemperatur ist seit 1880 um ~1,2°C gestiegen.",
      "Der Trend hat sich seit 1960 deutlich beschleunigt."
    ],
    "sources": [
      {
        "citation": "GISTEMP Team (2024)...",
        "doi": "10.7289/V5MGNM48"
      }
    ],
    "audience": "general",
    "language": "de",
    "word_count": 823,
    "generated_at": "2026-03-05T10:07:00Z",
    "reviewed_by": null,
    "published_at": null
  }
}
```

---

### POST /api/v1/explain/articles/{article_id}/review

Review-Entscheidung einreichen (nur autorisierte Reviewer).

**Request:**
```json
{
  "decision": "approved",
  "notes": "Wissenschaftlich korrekt, Quellenangaben vollständig.",
  "reviewer_id": "reviewer_42"
}
```

**decision Werte:** `approved` | `rejected` | `revision_required`

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "article_id": "art_ghi012",
    "status": "approved",
    "reviewed_by": "reviewer_42",
    "reviewed_at": "2026-03-05T14:00:00Z"
  }
}
```

---

### GET /api/v1/explain/articles

Liste aller Artikel (mit Filteroptionen).

**Query-Parameter:**
```
status:   ArticleStatus   (optional)
language: string          (optional)
topic:    string          (optional)
limit:    int             (default: 20)
offset:   int             (default: 0)
```

---

## Exploration API

**Owner:** Frontend Team (koordiniert mit Analysis + Simulation)
**Consumer:** Frontend (Explorationsseiten)

---

### POST /api/v1/explore/compare

Vergleich mehrerer Variablen.

**Request:**
```json
{
  "dataset_ids": [
    "nasa_giss_surface_temp_v4",
    "noaa_co2_mauna_loa_v1"
  ],
  "time_range": {
    "start": "1960-01-01",
    "end": "2025-12-31"
  },
  "normalize": true
}
```

**Response 200:**
```json
{
  "status": "ok",
  "data": {
    "comparison_id": "cmp_001",
    "series": [
      {
        "dataset_id": "nasa_giss_surface_temp_v4",
        "variable": "surface_temperature_anomaly",
        "unit": "°C",
        "normalized": true,
        "points": [ { "timestamp": "...", "value": 0.0 } ]
      }
    ],
    "auto_correlation": {
      "pearson_r": 0.87,
      "interpretation": "Starke positive Korrelation"
    }
  }
}
```

---

### POST /api/v1/explore/share

Exploration-Zustand speichern und Sharing-Link erzeugen.

**Request:**
```json
{
  "state": {
    "dataset_ids": ["nasa_giss_surface_temp_v4"],
    "time_range": { "start": "1960-01-01", "end": "2025-12-31" },
    "view_mode": "timeseries"
  }
}
```

**Response 201:**
```json
{
  "status": "ok",
  "data": {
    "share_token": "shr_abc123",
    "share_url": "https://climateinsight.org/explore?share=shr_abc123",
    "expires_at": null
  }
}
```

---

*Letzte Änderung: 2026-03-05 | System Architect | Alle Teams wurden informiert*
