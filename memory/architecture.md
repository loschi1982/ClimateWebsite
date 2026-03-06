# ClimateInsight — Systemarchitektur
## Version 1.0 | Pflichtlektüre für alle Teams

---

## Systemübersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEBPLATTFORM                             │
│          (Next.js Frontend + Interaktive Exploration)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST / WebSocket
┌──────────────────────────▼──────────────────────────────────────┐
│                      API GATEWAY                                │
│           (FastAPI · Versionierung · Auth · Rate Limit)         │
└──┬─────────┬─────────┬─────────┬─────────┬─────────┬───────────┘
   │         │         │         │         │         │
   ▼         ▼         ▼         ▼         ▼         ▼
┌──────┐ ┌───────┐ ┌───────┐ ┌──────┐ ┌───────┐ ┌────────┐
│Data  │ │Climate│ │Visual.│ │Simu- │ │Know-  │ │AI Expl.│
│Inge- │ │Analy- │ │Engine │ │lation│ │ledge  │ │System  │
│stion │ │sis    │ │       │ │Engine│ │Base   │ │        │
└──┬───┘ └───┬───┘ └───┬───┘ └──┬───┘ └───┬───┘ └────┬───┘
   │         │         │        │          │          │
   └─────────┴─────────┴────────┴──────────┴──────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        DATA LAYER                               │
│   TimescaleDB · Redis (Cache) · MinIO (Rohdaten) · PostgreSQL   │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                  EXTERNE DATENQUELLEN                           │
│       NASA · NOAA · Copernicus · IPCC · NSIDC                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Datenfluss

```
Externe Quellen
      │
      ▼
 Data Ingestion ──────────────────────────────────────┐
 (Abruf, Validierung,                                 │
  Normalisierung)                                     │
      │                                               │
      ▼                                               ▼
 TimescaleDB                                    MinIO / S3
 (normalisiert)                                 (Rohdaten)
      │
      ├──────────────────────┐
      │                      │
      ▼                      ▼
 Climate Analysis      Knowledge Base
 (Trends, Anomalien,   (Fakten, Quellen,
  Korrelationen,        Hypothesen)
  Hypothesen)               │
      │                     │
      ├──────────┐           ▼
      │          │      AI Explanation
      ▼          ▼      (Artikelentwurf)
 Visualization  Simulation     │
 Engine         Engine         │ status: pending_review
      │              │         │
      └──────┬────────┘         │
             │                  │
             ▼                  ▼
         Frontend ◄─────── Review Interface
         (Next.js)         (menschliche Prüfung)
             │
             ▼
     Veröffentlichung
     (nur nach Freigabe)
```

---

## Technologie-Stack

### Frontend
| Komponente | Technologie |
|------------|-------------|
| Framework | Next.js 15 (App Router) |
| Sprache | TypeScript |
| UI-Bibliothek | shadcn/ui + Tailwind CSS |
| Visualisierung | D3.js + Observable Plot |
| Karten | Deck.gl + MapLibre GL |
| State | Zustand + React Query |

### Backend
| Komponente | Technologie |
|------------|-------------|
| API Framework | FastAPI (Python 3.12) |
| Datenvalidierung | Pydantic v2 |
| Task Queue | Celery + Redis |
| Scheduling | APScheduler |
| Auth | JWT + OAuth2 |

### Daten
| Komponente | Technologie |
|------------|-------------|
| Zeitreihen | TimescaleDB |
| Cache | Redis |
| Objektspeicher | MinIO (S3-kompatibel) |
| Suche | PostgreSQL Full-Text |

### Analyse
| Komponente | Technologie |
|------------|-------------|
| Datenverarbeitung | Pandas + xarray |
| Klimaanalyse | xclim |
| Statistik | SciPy + NumPy |
| ML / Trends | scikit-learn |

### KI
| Komponente | Technologie |
|------------|-------------|
| LLM | Anthropic Claude API |
| RAG | LlamaIndex |

### Infrastruktur
| Komponente | Technologie |
|------------|-------------|
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |

---

## Module

### Modul 1: Data Ingestion
**Owner:** Data Pipeline Team | **Branch:** feature/data-pipeline

- Abruf von NASA, NOAA, Copernicus, IPCC, NSIDC
- Format-Normalisierung (NetCDF, CSV → einheitliches Schema)
- Datenvalidierung und Qualitätsprüfung
- Versionierung und Provenienz aller Datensätze

**API:** `POST/GET /api/v1/ingestion/*`
**Schreibt auf:** TimescaleDB, MinIO
**Gelesen von:** Climate Analysis, Visualization, Frontend

---

### Modul 2: Climate Analysis
**Owner:** Climate Analysis Team | **Branch:** feature/climate-analysis

- Zeitreihenanalyse (Trend, Anomalie, Saisonalität)
- Kreuzkorrelationen zwischen Klimavariablen
- Automatische Hypothesengenerierung
- Konfidenzintervalle und Unsicherheitsquantifizierung

**API:** `POST/GET /api/v1/analysis/*`
**Liest von:** Data Ingestion API
**Gelesen von:** Visualization, Simulation, AI Explanation, Frontend

---

### Modul 3: Visualization Engine
**Owner:** Visualization Team | **Branch:** feature/visualization

- Zeitreihendiagramme, Kartenvisualisierungen, Korrelationsmatrizen
- Vega-Lite Spezifikationen für Einbettung
- Export: SVG, PNG, CSV
- Quellenangabe in jedem Diagramm (Pflicht)

**API:** `POST/GET /api/v1/viz/*`
**Liest von:** Analysis API, Ingestion API
**Gelesen von:** Frontend

---

### Modul 4: Simulation Engine
**Owner:** Simulation Team | **Branch:** feature/simulation

- Didaktische IPCC-Szenarien (RCP 2.6 / 4.5 / 8.5)
- Parametrisierbare Klimaprojektionen
- Unsicherheitsbänder (5.–95. Perzentile)
- Vereinfachungen immer als `simplification_notes` kennzeichnen

**API:** `POST/GET /api/v1/simulation/*`
**Liest von:** Analysis API
**Gelesen von:** Frontend

---

### Modul 5: Knowledge Base
**Owner:** Data Pipeline Team | **Branch:** feature/data-pipeline

- Strukturierte Wissensbasis aus Analysen und Fakten
- Semantische Suche (Embedding-basiert)
- Quellenmanagement mit DOI-Verlinkung

**API:** `POST/GET /api/v1/knowledge/*`
**Gelesen von:** AI Explanation, Frontend

---

### Modul 6: AI Explanation System
**Owner:** AI Explanation Team | **Branch:** feature/ai-explanation

- RAG-Pipeline (LlamaIndex + Wissensbasis)
- Artikelgenerierung via Claude API
- Zielgruppenanpassung (general / expert)
- **Jeder Artikel hat immer status: pending_review**
- Veröffentlichung nur durch menschliche Freigabe

**API:** `POST/GET /api/v1/explain/*`
**Liest von:** Knowledge Base API, Analysis API
**Gelesen von:** Frontend, Review Interface

---

## Repository-Struktur

```
loschi1982/ClimateWebsite/
│
├── modules/                        # Kernmodule
│   ├── data_ingestion/
│   │   ├── src/
│   │   │   ├── connectors/         # ein Connector pro Datenquelle
│   │   │   ├── models/             # Pydantic-Datenmodelle
│   │   │   └── validators/         # Datenvalidierung
│   │   └── tests/
│   ├── climate_analysis/
│   │   ├── src/
│   │   │   ├── analyzers/          # Analyseklassen
│   │   │   └── models/             # Ergebnismodelle
│   │   ├── notebooks/              # Jupyter Notebooks
│   │   └── tests/
│   ├── visualization_engine/
│   │   ├── src/
│   │   └── tests/
│   ├── simulation_engine/
│   │   ├── src/
│   │   │   ├── models/             # Szenario-Definitionen
│   │   │   └── engine/             # Berechnungslogik
│   │   └── tests/
│   ├── knowledge_base/
│   └── ai_explanation/
│       ├── src/
│       │   ├── rag/                # Retrieval-Pipeline
│       │   ├── generator/          # Artikelgenerierung
│       │   └── review/             # Review-Workflow
│       └── tests/
│
├── services/
│   └── api_gateway/                # FastAPI Gateway
│       └── src/
│           ├── routers/            # ein Router pro Modul
│           └── main.py
│
├── frontend/                       # Next.js Anwendung
│   └── src/
│       ├── app/                    # Seiten (App Router)
│       │   ├── page.tsx            # Startseite
│       │   ├── explore/            # Explorations-Seite
│       │   ├── articles/           # Artikel
│       │   └── admin/              # Review-Interface
│       ├── components/
│       │   ├── charts/             # Visualization Team
│       │   ├── exploration/        # Frontend Team
│       │   └── ui/                 # UX Team
│       ├── lib/
│       │   └── api.ts              # zentraler API-Client
│       └── types/
│           └── climate.ts          # TypeScript-Typen
│
├── data/
│   ├── sources/                    # Quellendefinitionen (YAML)
│   ├── pipelines/                  # Airflow DAGs
│   ├── scenarios/                  # IPCC-Szenario-Daten
│   └── knowledge_seeds/            # Erste Wissensbasis-Einträge
│
├── api/
│   └── openapi.yaml                # Maschinenlesbare API-Spezifikation
│
├── memory/                         # Gemeinsame Projektdateien
│   ├── project_memory.json         # Projektgedächtnis (alle Teams)
│   ├── project_description.md      # Projektziel
│   ├── architecture.md             # diese Datei
│   ├── api_contracts.md            # API-Verträge
│   └── team_tasks.md               # Aufgaben pro Team
│
├── docs/
│   ├── deployment/
│   │   └── local_setup.md
│   ├── science/
│   │   └── glossary.md
│   ├── ux/
│   │   └── exploration_wireframes.md
│   └── review_guidelines.md
│
├── tests/
│   ├── integration/
│   ├── e2e/
│   └── api/
│       └── manual_tests.http
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── memory-validation.yml
│
├── .vscode/
│   ├── settings.json
│   ├── extensions.json
│   └── launch.json
│
├── docker-compose.yml
├── .env.example
├── README.md
└── CONTRIBUTING.md
```

---

## Branches

| Branch | Team | Verantwortung |
|--------|------|---------------|
| `main` | Projektverantwortlicher | Geprüfter, stabiler Code |
| `feature/data-pipeline` | Data Pipeline Team | Datenabruf, Normalisierung |
| `feature/climate-analysis` | Climate Analysis Team | Statistische Analyse |
| `feature/visualization` | Visualization Team | Charts, Karten |
| `feature/simulation` | Simulation Team | Klimaszenarien |
| `feature/frontend` | Frontend Team | Next.js Anwendung |
| `feature/ai-explanation` | AI Explanation Team | Artikelgenerierung |
| `feature/ux` | UX Team | Design-System |
| `feature/documentation` | Documentation Team | Docs, Glossar |
| `feature/developer-setup` | Developer Setup Team | Lokale Einrichtung |

---

## Architekturentscheidungen (ADRs)

Alle Entscheidungen stehen in `memory/project_memory.json`
unter `architecture_decisions`.

Kurzübersicht der wichtigsten:

| ID | Entscheidung |
|----|--------------|
| ADR-001 | TimescaleDB für Zeitreihendaten |
| ADR-002 | Next.js 15 mit App Router |
| ADR-003 | KI-Artikel immer pending_review (nicht verhandelbar) |
| ADR-004 | URL-Pfad-Versionierung (/api/v1/) |
| ADR-005 | Simulation server- oder client-seitig (noch offen) |

---

## Wichtigste Regeln für alle Teams

1. Jedes Team arbeitet **ausschließlich im eigenen Branch**
2. API-Verträge (`api_contracts.md`) sind **verbindlich**
3. Keine Architekturentscheidungen ohne Eintrag in `project_memory.json`
4. Alle Daten mit **vollständiger Quellenangabe** (DOI wenn möglich)
5. Kein KI-Artikel ohne **menschliche Prüfung** (`pending_review`)
6. Code wird **für Anfänger kommentiert**

---

*Stand: 2026-03-05 | Repository: loschi1982/ClimateWebsite*
