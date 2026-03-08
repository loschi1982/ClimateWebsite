# Team-Aufgaben – Klimaplattform
*Letzte Aktualisierung: 2025-01-01 | Verantwortlich: Documentation Team*

Status-Legende: 🔴 offen · 🟡 in Bearbeitung · 🟢 abgeschlossen · ⏸️ blockiert

---

## Data Pipeline Team
**Branch:** `team/data-pipeline`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| DP-01 | NASA GISS Temperaturdaten abrufen und normalisieren | 🔴 | 1 | – |
| DP-02 | NOAA Mauna Loa CO₂-Daten abrufen und normalisieren | 🔴 | 1 | – |
| DP-03 | NSIDC Meereisausdehnung abrufen und normalisieren | 🔴 | 1 | – |
| DP-04 | Validierungslogik implementieren (Wertebereiche, Lücken) | 🔴 | 1 | DP-01 |
| DP-05 | Lokalen Datei-Cache implementieren (data/raw/, data/processed/) | 🔴 | 1 | DP-01 |
| DP-06 | GET /api/v1/data Endpunkt implementieren | 🔴 | 1 | DP-01, DP-02 |
| DP-07 | GET /api/v1/data/sources Endpunkt implementieren | 🔴 | 1 | DP-06 |
| DP-08 | Unit Tests für alle Abruf-Funktionen (mit Mocks) | 🔴 | 1 | DP-06 |
| DP-09 | Copernicus CDS API integrieren | 🔴 | 2 | DP-01 |
| DP-10 | Automatischer täglicher Datenabruf (Scheduler) | 🔴 | 3 | DP-06 |

---

## Climate Analysis Team
**Branch:** `team/climate-analysis`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| CA-01 | Lineare Trendberechnung implementieren (scipy) | 🔴 | 1 | DP-01 |
| CA-02 | Pearson-Korrelation zwischen zwei Variablen | 🔴 | 1 | DP-01, DP-02 |
| CA-03 | Anomalieerkennung (Abweichung vom Referenzzeitraum) | 🔴 | 1 | DP-01 |
| CA-04 | Gleitenden Mittelwert berechnen | 🔴 | 1 | DP-01 |
| CA-05 | GET /api/v1/analysis/trend Endpunkt | 🔴 | 1 | CA-01 |
| CA-06 | GET /api/v1/analysis/correlation Endpunkt | 🔴 | 1 | CA-02 |
| CA-07 | GET /api/v1/analysis/anomalies Endpunkt | 🔴 | 1 | CA-03 |
| CA-08 | Unit Tests (positive Trends, Korrelation, NaN-Umgang) | 🔴 | 1 | CA-05, CA-06 |
| CA-09 | AnalysisSummary-Format für AI Explanation Team definieren | 🔴 | 2 | CA-01 |
| CA-10 | Automatische Trendanalyse nach neuem Datenabruf | 🔴 | 3 | CA-01, DP-10 |

---

## Visualization Team
**Branch:** `team/visualization`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| VZ-01 | TimeSeriesChart.jsx implementieren (Recharts LineChart) | 🔴 | 1 | CA-05 |
| VZ-02 | TrendOverlay.jsx (Trendlinie über Zeitreihe) | 🔴 | 1 | CA-05 |
| VZ-03 | CorrelationChart.jsx (ScatterChart) | 🔴 | 1 | CA-06 |
| VZ-04 | MapView.jsx (Leaflet, Basis-Kartenansicht) | 🔴 | 2 | – |
| VZ-05 | Backend: timeseries.py (Daten für Charts aufbereiten) | 🔴 | 1 | CA-01 |
| VZ-06 | Quellenangabe in alle Diagramme einbauen | 🔴 | 1 | VZ-01 |
| VZ-07 | Vitest-Tests: Komponenten rendern, Quellenangabe vorhanden | 🔴 | 1 | VZ-01 |
| VZ-08 | Farbpalette mit UX Team abstimmen und umsetzen | 🔴 | 1 | UX-01 |
| VZ-09 | Leere-Daten-Fehlermeldung in allen Komponenten | 🔴 | 1 | VZ-01 |
| VZ-10 | Responsive Darstellung (Mobile) | 🔴 | 2 | VZ-01 |

---

## Simulation Team
**Branch:** `team/simulation`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| SI-01 | RCP-Temperaturszenarien implementieren (rcp26, rcp45, rcp85) | 🔴 | 2 | – |
| SI-02 | CO₂-Akkumulationsmodell implementieren | 🔴 | 2 | – |
| SI-03 | Meereis-Temperatur-Modell implementieren | 🔴 | 2 | – |
| SI-04 | POST /api/v1/simulation/run Endpunkt | 🔴 | 2 | SI-01 |
| SI-05 | GET /api/v1/simulation/scenarios Endpunkt | 🔴 | 2 | SI-01 |
| SI-06 | ScenarioSlider.jsx (React, Range-Input) | 🔴 | 2 | SI-04 |
| SI-07 | Disclaimer in alle SimResult-Antworten einbauen | 🔴 | 2 | SI-04 |
| SI-08 | Unit Tests (RCP-Reihenfolge, Disclaimer vorhanden) | 🔴 | 2 | SI-04 |
| SI-09 | Erklärungstext für jedes Szenario schreiben | 🔴 | 2 | SI-01 |

---

## Frontend Team
**Branch:** `team/frontend`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| FE-01 | React-Projektstruktur einrichten (Vite, Tailwind, Router) | 🔴 | 1 | – |
| FE-02 | Layout-Komponenten: Navbar, Footer | 🔴 | 1 | UX-01 |
| FE-03 | Home.jsx (Übersichtsseite) | 🔴 | 1 | FE-02 |
| FE-04 | API-Client (client.js) implementieren | 🔴 | 1 | DP-06 |
| FE-05 | useClimateData Hook implementieren | 🔴 | 1 | FE-04 |
| FE-06 | Explore.jsx (Explorationsseite, Grundstruktur) | 🔴 | 1 | FE-04 |
| FE-07 | DatasetSelector-Komponente | 🔴 | 1 | FE-06 |
| FE-08 | VariableComparison-Komponente | 🔴 | 2 | VZ-01, VZ-03 |
| FE-09 | Simulation.jsx (Simulationsseite) | 🔴 | 2 | SI-06 |
| FE-10 | Articles.jsx (Artikelseite) | 🔴 | 2 | AE-04 |
| FE-11 | About.jsx (Über das Projekt, Quellen, Methoden) | 🔴 | 1 | – |
| FE-12 | Fehlerbehandlung: API nicht erreichbar | 🔴 | 1 | FE-04 |
| FE-13 | Vitest-Tests: Alle Seiten rendern fehlerfrei | 🔴 | 1 | FE-03 |
| FE-14 | useSimulation Hook | 🔴 | 2 | SI-04 |

---

## AI Explanation Team
**Branch:** `team/ai-explanation`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| AE-01 | Anthropic API-Client einrichten (ANTHROPIC_API_KEY) | 🔴 | 2 | – |
| AE-02 | Basis-Prompt für Artikelgenerierung entwickeln | 🔴 | 2 | AE-01 |
| AE-03 | generate_article() implementieren | 🔴 | 2 | AE-02, CA-09 |
| AE-04 | POST /api/v1/articles/generate Endpunkt | 🔴 | 2 | AE-03 |
| AE-05 | GET /api/v1/articles Endpunkt | 🔴 | 2 | AE-03 |
| AE-06 | GET /api/v1/articles/{id} Endpunkt | 🔴 | 2 | AE-03 |
| AE-07 | Job-System für asynchrone Artikelgenerierung | 🔴 | 2 | AE-04 |
| AE-08 | suggest_topics() implementieren | 🔴 | 2 | AE-03 |
| AE-09 | explain_trend() für kurze Erklärungen | 🔴 | 2 | AE-03 |
| AE-10 | Unit Tests mit Mock-Anthropic-API | 🔴 | 2 | AE-03 |
| AE-11 | Sicherstellen: Alle Artikel erhalten status: "draft" | 🔴 | 2 | AE-03 |

---

## UX Team
**Branch:** `team/ux`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| UX-01 | Design-System definieren (Farben, Typografie, Abstände) | 🔴 | 1 | – |
| UX-02 | Tailwind-Konfiguration anpassen (custom colors) | 🔴 | 1 | UX-01 |
| UX-03 | CSS-Variablen in global.css definieren | 🔴 | 1 | UX-01 |
| UX-04 | Navigationsstruktur festlegen | 🔴 | 1 | – |
| UX-05 | UX-Review: Navbar und Footer (Frontend Team) | 🔴 | 1 | FE-02 |
| UX-06 | UX-Review: TimeSeriesChart (Visualization Team) | 🔴 | 1 | VZ-01 |
| UX-07 | UX-Review: Explorationsseite (Frontend Team) | 🔴 | 2 | FE-06 |
| UX-08 | UX-Review: ScenarioSlider (Simulation Team) | 🔴 | 2 | SI-06 |
| UX-09 | Barrierefreiheitsprüfung (Kontrast, Tastaturnavigation) | 🔴 | 2 | FE-03 |
| UX-10 | design-system.md schreiben und aktuell halten | 🔴 | 1 | UX-01 |

---

## Documentation Team
**Branch:** `team/documentation`

| # | Aufgabe | Status | Phase | Abhängigkeit |
|---|---|---|---|---|
| DO-01 | README.md erstellen | 🟢 | 1 | – |
| DO-02 | docs/architecture.md erstellen | 🟢 | 1 | – |
| DO-03 | docs/api_contracts.md erstellen | 🟢 | 1 | – |
| DO-04 | memory/team_tasks.md erstellen | 🟢 | 1 | – |
| DO-05 | memory/project_memory.json initialisieren | 🟢 | 1 | – |
| DO-06 | docs/setup_guide.md schreiben (Zorin OS 17, Anfänger) | 🔴 | 1 | – |
| DO-07 | docs/data_sources.md schreiben | 🔴 | 1 | DP-01 |
| DO-08 | CONTRIBUTING.md schreiben | 🔴 | 1 | – |
| DO-09 | Code-Kommentare aller Teams prüfen (Phase-1-Module) | 🔴 | 1 | DP-08, CA-08 |
| DO-10 | project_memory.json: Einträge anderer Teams prüfen | 🔴 | 1 | – |
| DO-11 | docs/setup_guide.md aktuell halten (nach jeder Abhängigkeitsänderung) | 🔴 | laufend | – |
| DO-12 | lessons_learned in project_memory.json zusammenfassen | 🔴 | laufend | – |

---

## Phasenplan

### Phase 1 (Wochen 1–6): Datenpipeline und erste Visualisierung
**Ziel:** Temperatur- und CO₂-Daten abrufbar und als Diagramm darstellbar

Beteiligte Teams: Data Pipeline, Climate Analysis, Visualization, Frontend, UX, Documentation

Meilenstein: `http://localhost:5173/explore` zeigt Temperatur- und CO₂-Zeitreihen mit Trendlinie.

---

### Phase 2 (Wochen 7–12): Simulation und KI-Erklärungen
**Ziel:** Interaktive Szenarien und erste KI-Artikelentwürfe

Beteiligte Teams: Simulation, AI Explanation, Frontend, Visualization

Meilenstein: Simulationsseite mit RCP-Schieberegler funktioniert. Erste Artikelentwürfe im System.

---

### Phase 3 (Wochen 13–18): Interaktive Exploration und UX-Verfeinerung
**Ziel:** Vollständige Explorationsseite für Endnutzer

Beteiligte Teams: Frontend, UX, alle

Meilenstein: Alle Sektionen der Plattform sind nutzbar und UX-reviewed.