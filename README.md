# 🌍 Klimaplattform

Eine Open-Source-Webplattform zur wissenschaftlichen Aufklärung über Klimaveränderungen.

## Was ist die Klimaplattform?

Die Klimaplattform macht wissenschaftliche Klimadaten für alle verständlich.
Sie zeigt, wie sich Temperatur, CO₂, Meeresspiegel und Eisflächen über Zeit verändert haben –
mit interaktiven Diagrammen, einfachen Erklärungen und didaktischen Simulationen.

Alle Inhalte basieren auf öffentlichen Daten von:
- [NASA GISS](https://data.giss.nasa.gov/)
- [NOAA](https://www.noaa.gov/)
- [Copernicus Climate Change Service](https://climate.copernicus.eu/)
- [NSIDC](https://nsidc.org/)
- [IPCC](https://www.ipcc.ch/)

> **Hinweis:** KI-generierte Artikelentwürfe werden immer von Menschen geprüft, bevor sie veröffentlicht werden.

---

## Funktionen

- 📈 Interaktive Zeitreihendiagramme (Temperatur, CO₂, Meereis)
- 🔍 Korrelationsanalysen zwischen Klimavariablen
- 🗺️ Kartenvisualisierungen
- 🎛️ Didaktische Szenarien-Simulationen (z. B. RCP 2.6 / 4.5 / 8.5)
- 📝 Verständliche Artikel, erstellt mit KI-Unterstützung und menschlicher Prüfung

---

## Schnellstart – Entwicklungsumgebung einrichten

Eine vollständige Anleitung für Anfänger findest du in:
👉 [`docs/setup_guide.md`](docs/setup_guide.md)

### Kurzübersicht

```bash
# 1. Repository klonen
git clone https://github.com/dein-nutzername/klimaplattform.git
cd klimaplattform

# 2. Backend starten (Python)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Frontend starten (in neuem Terminal)
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend-API: http://localhost:8000/docs

---

## Projektstruktur

```
klimaplattform/
├── backend/          # Python-Backend (FastAPI)
├── frontend/         # React-Frontend (Vite)
├── data/             # Lokaler Datencache (nicht in Git)
├── docs/             # Dokumentation
├── memory/           # Projektgedächtnis und Team-Aufgaben
└── README.md
```

Mehr Details: [`docs/architecture.md`](docs/architecture.md)

---

## Mitmachen

Dieses Projekt freut sich über Beiträge!
Lies zuerst: [`CONTRIBUTING.md`](CONTRIBUTING.md)

### Branch-Übersicht

| Branch | Team |
|---|---|
| `main` | Gemeinsame Dateien (kein direkter Commit) |
| `team/data-pipeline` | Data Pipeline Team |
| `team/climate-analysis` | Climate Analysis Team |
| `team/visualization` | Visualization Team |
| `team/simulation` | Simulation Team |
| `team/frontend` | Frontend Team |
| `team/ai-explanation` | AI Explanation Team |
| `team/ux` | UX Team |
| `team/documentation` | Documentation Team |

---

## Lizenz

MIT License – siehe [`LICENSE`](LICENSE)

---

## Kontakt

Fragen oder Ideen? Öffne ein [GitHub Issue](https://github.com/dein-nutzername/klimaplattform/issues).