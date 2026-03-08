# Systemarchitektur – Klimaplattform
*Version: 1.0 | Letzte Änderung: 2025-01-01 | Verantwortlich: Documentation Team*

---

## Übersicht

Die Klimaplattform besteht aus mehreren unabhängigen Modulen,
die über klar definierte Schnittstellen (APIs) miteinander kommunizieren.

```
┌─────────────────────────────────────────────────────────────┐
│                        WEBPLATTFORM                         │
│         (React Frontend + interaktive Exploration)          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / REST
┌────────────────────────▼────────────────────────────────────┐
│                      BACKEND API                            │
│                  (FastAPI / Python)                         │
│                  http://localhost:8000                      │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│  Data    │ Climate  │  Viz     │  Simul.  │  AI Explain   │
│ Ingest.  │ Analysis │  Engine  │  Engine  │  System       │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬──────────┘
     │          │          │          │          │
┌────▼──────────▼──────────▼──────────▼──────────▼──────────┐
│                     WISSENSBASIS                           │
│         SQLite (lokal) + JSON/CSV-Dateien                  │
└────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  EXTERNE DATENQUELLEN                       │
│     NASA · NOAA · Copernicus · NSIDC · IPCC               │
└─────────────────────────────────────────────────────────────┘
```

---

## Datenfluss (Schritt für Schritt)

1. **Data Ingestion** ruft Rohdaten von externen Quellen ab und speichert sie lokal
2. **Climate Analysis** liest die gespeicherten Daten und berechnet Trends, Korrelationen, Anomalien
3. **Knowledge Base** speichert alle Analyseergebnisse strukturiert in SQLite
4. **Visualization Engine** bereitet Daten für Diagramme auf (JSON für React)
5. **Simulation Engine** berechnet Szenarien auf Basis vereinfachter Modelle
6. **AI Explanation System** generiert Artikelentwürfe aus Analysezusammenfassungen
7. **Backend API** stellt alle Ergebnisse als REST-Endpunkte bereit
8. **React Frontend** ruft die API ab und zeigt Ergebnisse interaktiv an

---

## Module

### Data Ingestion Module
- **Pfad:** `backend/modules/data_ingestion/`
- **Team:** Data Pipeline Team
- **Zweck:** Externe Klimadaten abrufen, validieren, normalisieren und speichern
- **Input:** Konfiguration (Quelle, Variable, Zeitraum)
- **Output:** Normalisierte JSON/CSV-Dateien in `data/processed/`
- **Abhängigkeiten:** Keine (ist die Datenquelle für alle anderen Module)

### Climate Analysis Module
- **Pfad:** `backend/modules/climate_analysis/`
- **Team:** Climate Analysis Team
- **Zweck:** Trendberechnung, Korrelationsanalyse, Anomalieerkennung
- **Input:** Normalisierte Datensätze aus `data/processed/`
- **Output:** TrendResult, CorrelationResult, AnomalyResult (JSON)
- **Abhängigkeiten:** Data Ingestion Module

### Visualization Engine
- **Pfad:** `backend/modules/visualization/` + `frontend/src/components/charts/`
- **Team:** Visualization Team
- **Zweck:** Daten für Diagramme aufbereiten, React-Diagrammkomponenten
- **Input:** Analyseergebnisse und Rohdatensätze (über API)
- **Output:** ChartData (JSON) + React-Komponenten
- **Abhängigkeiten:** Climate Analysis Module, Data Ingestion Module

### Simulation Engine
- **Pfad:** `backend/modules/simulation/`
- **Team:** Simulation Team
- **Zweck:** Didaktische Klimaszenarien berechnen
- **Input:** Szenario-Parameter (z. B. Emissionspfad, Jahre)
- **Output:** SimResult (JSON) mit Daten + Disclaimer + Erklärung
- **Abhängigkeiten:** Keine (eigene vereinfachte Modelle)

### Knowledge Base
- **Pfad:** `backend/modules/knowledge_base/`
- **Team:** Backend Team / alle
- **Zweck:** Zentraler Datenspeicher (SQLite)
- **Tabellen:** `datasets`, `analyses`, `articles`, `sources`
- **Abhängigkeiten:** Alle Module schreiben in die Knowledge Base

### AI Explanation System
- **Pfad:** `backend/modules/ai_explanation/`
- **Team:** AI Explanation Team
- **Zweck:** Verständliche Artikelentwürfe generieren (immer als "draft")
- **Input:** AnalysisSummary (von Climate Analysis)
- **Output:** ArticleDraft (Markdown, status: "draft")
- **Abhängigkeiten:** Climate Analysis Module, Anthropic API

---

## Technologie-Stack

| Schicht | Technologie | Version |
|---|---|---|
| Frontend | React + Vite | React 18 |
| Frontend Styling | Tailwind CSS | 3.x |
| Frontend Diagramme | Recharts | aktuell |
| Frontend Karten | Leaflet | aktuell |
| Frontend Routing | React Router | v6 |
| Backend | FastAPI (Python) | 0.100+ |
| Backend Server | uvicorn | aktuell |
| Datenanalyse | pandas, numpy, scipy | aktuell |
| Datenbank | SQLite (via SQLAlchemy) | – |
| KI-Integration | Anthropic API | claude-sonnet-4-20250514 |
| Tests Backend | pytest | aktuell |
| Tests Frontend | Vitest | aktuell |

---

## Repository-Struktur

```
klimaplattform/
│
├── README.md
├── CONTRIBUTING.md
├── .env.example
├── .gitignore
│
├── docs/
│   ├── architecture.md       ← diese Datei
│   ├── api_contracts.md
│   ├── setup_guide.md
│   ├── data_sources.md
│   └── contributing.md
│
├── memory/
│   ├── project_memory.json
│   └── team_tasks.md
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── config.py
│   ├── modules/
│   │   ├── data_ingestion/
│   │   ├── climate_analysis/
│   │   ├── visualization/
│   │   ├── simulation/
│   │   ├── knowledge_base/
│   │   └── ai_explanation/
│   ├── api/
│   │   └── v1/
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── hooks/
│       ├── api/
│       └── styles/
│
└── data/
    ├── raw/         (nicht in Git)
    └── processed/   (nicht in Git)
```

---

## Architekturregeln (für alle Teams verbindlich)

1. Kein Team committed direkt in `main` – nur per Pull Request
2. Jede API-Änderung muss in `docs/api_contracts.md` dokumentiert werden
3. Jede Architekturentscheidung wird in `memory/project_memory.json` eingetragen
4. Module kommunizieren nur über definierte APIs – kein direkter Modulaufruf zwischen Teams
5. KI-generierte Artikel erhalten immer `status: "draft"` – keine automatische Veröffentlichung
6. Alle Quellenangaben müssen in der UI sichtbar sein

---

## Änderungshistorie

| Version | Datum | Team | Änderung |
|---|---|---|---|
| 1.0 | 2025-01-01 | Architect | Initiale Architektur erstellt |