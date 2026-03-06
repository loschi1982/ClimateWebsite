# ClimateInsight — Aufgaben pro Team
## Version 1.0 | team_tasks.md

---

> **Wie benutze ich diese Datei?**
> Jedes Team liest zu Beginn einer Session seinen Abschnitt.
> Abgeschlossene Aufgaben werden in `project_memory.json` unter
> `team_progress → [team] → completed_tasks` dokumentiert.

---

## Entwicklungsphasen

```
Phase 1 (aktuell): Walking Skeleton
  → Erste echte Daten fließen, erste Seite ist sichtbar

Phase 2: Vollständige Datenpipeline
  → Alle Datenquellen, vollständige Analysen

Phase 3: Interaktive Exploration
  → Alle Explorationsfunktionen, Simulationen

Phase 4: KI-Artikel und Veröffentlichung
  → Artikel-Workflow, Review-System, Launch
```

---

## 🟦 Data Pipeline Team

**Branch:** `feature/data-pipeline`
**Abhängigkeiten:** keiner (Startpunkt des Systems)
**Wird gebraucht von:** Climate Analysis, Visualization, Frontend

### Phase 1 — Priorität: HOCH

- [ ] **P1-DP-01** Pydantic-Datenmodelle definieren
  - `DataPoint`, `ClimateDataset`, `IngestionJob`, `SourceReference`
  - Datei: `modules/data_ingestion/src/models/climate_dataset.py`

- [ ] **P1-DP-02** NASA GISS Connector implementieren
  - GISTEMP v4 Temperaturdaten abrufen und normalisieren
  - Datei: `modules/data_ingestion/src/connectors/nasa_giss.py`

- [ ] **P1-DP-03** Ingestion API Router implementieren
  - Alle 5 Endpoints aus `api_contracts.md`
  - Datei: `services/api_gateway/src/routers/ingestion.py`

- [ ] **P1-DP-04** Knowledge Base Router implementieren
  - Datei: `services/api_gateway/src/routers/knowledge.py`

- [ ] **P1-DP-05** Unit Tests für Connector und Modelle
  - Datei: `modules/data_ingestion/tests/`

### Phase 2

- [ ] **P2-DP-01** NOAA CO₂ Connector (Mauna Loa)
- [ ] **P2-DP-02** NSIDC Meereis-Connector
- [ ] **P2-DP-03** NASA Meeresspiegel-Connector
- [ ] **P2-DP-04** Airflow DAGs für automatischen Abruf
- [ ] **P2-DP-05** Copernicus C3S Connector

---

## 🟩 Climate Analysis Team

**Branch:** `feature/climate-analysis`
**Abhängigkeiten:** Data Pipeline Team (P1-DP-01, P1-DP-02)
**Wird gebraucht von:** Visualization, Simulation, AI Explanation, Frontend

### Phase 1 — Priorität: HOCH

- [ ] **P1-CA-01** Lineare Trendanalyse implementieren
  - OLS-Regression, Konfidenzintervalle, p-Wert
  - Datei: `modules/climate_analysis/src/analyzers/trend_analyzer.py`

- [ ] **P1-CA-02** Analysis API Router implementieren
  - Alle 4 Endpoints aus `api_contracts.md`
  - Datei: `services/api_gateway/src/routers/analysis.py`

- [ ] **P1-CA-03** Unit Tests für Trendanalyse
  - Referenzwerte: IPCC AR6 Temperaturtrend ±5%
  - Datei: `modules/climate_analysis/tests/test_trend_analyzer.py`

- [ ] **P1-CA-04** Jupyter Notebook: Temperaturtrend
  - Datei: `modules/climate_analysis/notebooks/01_temperature_trend.ipynb`

### Phase 2

- [ ] **P2-CA-01** Anomalieerkennung (Z-Score + IQR)
- [ ] **P2-CA-02** Kreuzkorrelationsanalyse
- [ ] **P2-CA-03** Zeitreihendekomposition (Trend + Saisonalität)
- [ ] **P2-CA-04** Hypothesengenerator
- [ ] **P2-CA-05** Kurzfrist-Forecast (max. 10 Jahre)

---

## 🟨 Visualization Team

**Branch:** `feature/visualization`
**Abhängigkeiten:** Climate Analysis Team (P1-CA-01), UX Team (P1-UX-01)
**Wird gebraucht von:** Frontend

### Phase 1 — Priorität: HOCH

- [ ] **P1-VZ-01** Zeitreihen-Chart-Komponente
  - D3.js / Observable Plot, Trendlinie, Konfidenzband, Tooltip
  - Datei: `frontend/src/components/charts/TimeSeriesChart.tsx`

- [ ] **P1-VZ-02** Farbschemata definieren
  - `diverging_rdbu`, `sequential_blue`, `sequential_orange`
  - Datei: `frontend/src/lib/viz/color_schemes.ts`

- [ ] **P1-VZ-03** Visualization API Router
  - Alle 4 Endpoints aus `api_contracts.md`
  - Datei: `services/api_gateway/src/routers/viz.py`

- [ ] **P1-VZ-04** Vega-Lite Spec Generator (Python)
  - Datei: `modules/visualization_engine/src/spec_generator.py`

### Phase 2

- [ ] **P2-VZ-01** Korrelationsmatrix-Komponente
- [ ] **P2-VZ-02** Weltkarten-Visualisierung (Deck.gl)
- [ ] **P2-VZ-03** Export-Funktion (SVG, PNG, CSV)
- [ ] **P2-VZ-04** Scatter-Plot-Komponente

---

## 🟧 Simulation Team

**Branch:** `feature/simulation`
**Abhängigkeiten:** Climate Analysis Team (P1-CA-01)
**Offene Frage:** ADR-005 (server- vs. client-seitig) — mit Frontend Team klären

### Phase 1 — Priorität: MITTEL

- [ ] **P1-SM-01** ADR-005 entscheiden
  - Koordination mit Frontend Team erforderlich
  - Ergebnis in `project_memory.json` dokumentieren

- [ ] **P1-SM-02** IPCC-Szenarien als Datenmodelle
  - RCP 2.6 / 4.5 / 8.5
  - Dateien: `data/scenarios/rcp_*.yaml`
  - Datei: `modules/simulation_engine/src/models/scenario.py`

- [ ] **P1-SM-03** Simulation API Router
  - Alle 4 Endpoints aus `api_contracts.md`
  - Datei: `services/api_gateway/src/routers/simulation.py`

### Phase 2

- [ ] **P2-SM-01** Parametrisierbarer Simulationsmotor
- [ ] **P2-SM-02** Unsicherheitsbänder (5.–95. Perzentile)
- [ ] **P2-SM-03** Validierungstests gegen IPCC AR6
- [ ] **P2-SM-04** WebAssembly-Version (falls ADR-005 = client-seitig)

---

## 🟥 Frontend Team

**Branch:** `feature/frontend`
**Abhängigkeiten:** UX Team (P1-UX-01), Visualization Team (P1-VZ-01)
**Konsumiert:** alle APIs

### Phase 1 — Priorität: HOCH

- [ ] **P1-FE-01** TypeScript API-Client
  - Typisierte Funktionen für alle 6 Module
  - Datei: `frontend/src/lib/api.ts`

- [ ] **P1-FE-02** TypeScript-Typen aus API-Verträgen
  - Datei: `frontend/src/types/climate.ts`

- [ ] **P1-FE-03** Next.js Grundstruktur (4 Seiten)
  - `app/page.tsx` — Startseite
  - `app/explore/page.tsx` — Exploration
  - `app/articles/page.tsx` — Artikelübersicht
  - `app/articles/[id]/page.tsx` — Einzelartikel

- [ ] **P1-FE-04** Explorations-Seite (Basis)
  - Dataset-Auswahl, Zeitraumwähler, Zeitreihendiagramm
  - URL-State für Sharing

### Phase 2

- [ ] **P2-FE-01** Variablenvergleich (mehrere Datensätze)
- [ ] **P2-FE-02** Szenario-Simulator integrieren
- [ ] **P2-FE-03** Admin/Review-Interface
- [ ] **P2-FE-04** Artikeldarstellung mit Quellenangaben
- [ ] **P2-FE-05** E2E-Tests (Playwright)

---

## 🟪 AI Explanation Team

**Branch:** `feature/ai-explanation`
**Abhängigkeiten:** Knowledge Base (P1-DP-04), Climate Analysis (P2-CA-04)
**Kritische Regel:** Jeder Artikel hat immer `status: pending_review`

### Phase 1 — Priorität: NIEDRIG (wartet auf Daten)

- [ ] **P1-AI-01** Knowledge Base Seed-Daten erstellen
  - 2 erste Einträge manuell
  - Dateien: `data/knowledge_seeds/*.json`

- [ ] **P1-AI-02** Review-Richtlinien dokumentieren
  - Datei: `docs/review_guidelines.md`

### Phase 2

- [ ] **P2-AI-01** RAG-Pipeline (LlamaIndex)
  - Datei: `modules/ai_explanation/src/rag/retriever.py`

- [ ] **P2-AI-02** Artikelgenerator (Claude API)
  - Datei: `modules/ai_explanation/src/generator/article_generator.py`

- [ ] **P2-AI-03** AI Explanation API Router
  - Datei: `services/api_gateway/src/routers/explain.py`

- [ ] **P2-AI-04** Review-Workflow-Backend

---

## ⬜ UX Team

**Branch:** `feature/ux`
**Abhängigkeiten:** keine (Startpunkt)
**Wird gebraucht von:** Visualization Team, Frontend Team

### Phase 1 — Priorität: HOCH (andere Teams warten darauf)

- [ ] **P1-UX-01** Design-Token-System
  - Farbpaletten, Typografie, Abstände
  - Datei: `frontend/tailwind.config.ts`
  - Datei: `frontend/src/styles/globals.css`

- [ ] **P1-UX-02** Design-System-Dokumentation
  - Datei: `docs/design_system.md`

- [ ] **P1-UX-03** Explorations-Wireframes
  - Datei: `docs/ux/exploration_wireframes.md`

### Phase 2

- [ ] **P2-UX-01** Barrierefreiheits-Checkliste
  - Datei: `docs/ux/accessibility_checklist.md`

- [ ] **P2-UX-02** Offene Frage oq_002 beantworten
  - Mehrsprachigkeit: DE + EN von Anfang an, oder erst DE?
  - Eintrag in `project_memory.json`

- [ ] **P2-UX-03** Komponentenspezifikationen
  - Charts, Karten, Navigation, Quellenangabe

---

## 📄 Documentation Team

**Branch:** `feature/documentation`
**Abhängigkeiten:** liest alle anderen Teams via `project_memory.json`

### Phase 1 — Priorität: MITTEL

- [ ] **P1-DO-01** README.md erstellen
  - Datei: `README.md`

- [ ] **P1-DO-02** CONTRIBUTING.md erstellen
  - Datei: `CONTRIBUTING.md`

- [ ] **P1-DO-03** Wissenschaftliches Glossar (15 Einträge)
  - Datei: `docs/science/glossary.md`

- [ ] **P1-DO-04** OpenAPI Spec prüfen und synchronisieren
  - Datei: `api/openapi.yaml` mit `memory/api_contracts.md` abgleichen

### Phase 2

- [ ] **P2-DO-01** Architekturübersicht für Einsteiger
  - Datei: `docs/architecture/overview.md`

- [ ] **P2-DO-02** Deployment-Guide aktuell halten
  - Datei: `docs/deployment/local_setup.md`

- [ ] **P2-DO-03** Glossar auf 30+ Einträge erweitern

---

## 🛠️ Developer Setup Team

**Branch:** `feature/developer-setup`
**Abhängigkeiten:** keine (Startpunkt, parallel zu allen anderen)
**Wird gebraucht von:** alle Teams

### Phase 1 — Priorität: SEHR HOCH (alle anderen warten darauf)

- [ ] **P1-DS-01** docker-compose.yml erstellen
  - Alle lokalen Services: API, Frontend, DB, Redis, MinIO, Swagger
  - Datei: `docker-compose.yml`

- [ ] **P1-DS-02** .env.example erstellen
  - Alle Umgebungsvariablen mit Erklärungen
  - Datei: `.env.example`

- [ ] **P1-DS-03** VSCode-Konfiguration
  - Dateien: `.vscode/settings.json`, `.vscode/extensions.json`, `.vscode/launch.json`

- [ ] **P1-DS-04** Manuelle API-Tests
  - Fertige .http Datei für alle Endpoints
  - Datei: `tests/api/manual_tests.http`

- [ ] **P1-DS-05** Setup-Anleitung (Zorin OS 17)
  - Datei: `docs/deployment/local_setup.md`

### Phase 2

- [ ] **P2-DS-01** GitHub Actions CI/CD Pipeline
  - Datei: `.github/workflows/ci.yml`

- [ ] **P2-DS-02** Memory-Validierungs-Workflow
  - Datei: `.github/workflows/memory-validation.yml`

- [ ] **P2-DS-03** docker-compose.prod.yml für Produktion

---

## Abhängigkeitsgraph Phase 1

```
Developer Setup Team  ──────────────────────────────┐
UX Team               ──────────────────────────┐   │
Data Pipeline Team    ──────────────────────┐   │   │
                                            │   │   │
                                            ▼   ▼   ▼
Climate Analysis Team ────────────────► Visualization Team
        │                                       │
        │                                       ▼
        └──────────────────────────────► Frontend Team
                                               ▲
Simulation Team ───────────────────────────────┘
```

**Was das bedeutet:**
- Developer Setup Team und UX Team können sofort starten
- Data Pipeline Team kann sofort starten
- Climate Analysis Team startet sobald erste Datensätze vorliegen
- Visualization Team startet sobald Analysen und Design-Tokens vorliegen
- Frontend Team startet sobald Basis-Komponenten und API-Client bereit sind

---

## Fortschritt verfolgen

Den aktuellen Stand aller Teams findest du in:
```
memory/project_memory.json → team_progress
```

Nach jeder abgeschlossenen Aufgabe:
```json
"completed_tasks": ["P1-DP-01", "P1-DP-02"]
```

---

*Stand: 2026-03-05 | Repository: loschi1982/ClimateWebsite*
