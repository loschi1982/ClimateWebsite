# ClimateInsight – Lokale Einrichtungsanleitung

> **Für wen ist diese Anleitung?**  
> Für absolute Anfänger ohne Vorkenntnisse. Jeder Schritt wird erklärt.

> **Betriebssysteme:** Windows 10/11 · macOS 12+ · Ubuntu 22.04 / Zorin OS 17

---

## Inhaltsverzeichnis

1. [Software installieren](#1-software-installieren)
2. [VSCode einrichten](#2-vscode-einrichten-und-erweiterungen-installieren)
3. [Repository klonen und öffnen](#3-repository-klonen-und-öffnen)
4. [Umgebungsvariablen einrichten](#4-umgebungsvariablen-einrichten)
5. [Docker starten und Services prüfen](#5-docker-starten-und-services-prüfen)
6. [Erste API-Tests durchführen](#6-erste-api-tests-durchführen)
7. [Code einfügen](#7-code-einfügen)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Software installieren

Du brauchst vier Programme. Installiere sie in dieser Reihenfolge.

### 1.1 Git

Git ist ein Versionskontrollsystem. Es merkt sich jede Änderung an Dateien und ermöglicht die Zusammenarbeit aller neun Teams.

**Windows:**
1. Öffne https://git-scm.com/download/win
2. Lade den Installer herunter und führe ihn aus
3. Klicke überall auf **Next** – die Standardeinstellungen sind richtig
4. Wähle bei "Default editor" → **Visual Studio Code**
5. Wähle bei "Adjust your PATH" → **Git from the command line and also from 3rd-party software**

**macOS:**
```bash
# Homebrew installieren (falls noch nicht vorhanden):
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git
```

**Ubuntu 22.04 / Zorin OS 17:**
```bash
sudo apt update && sudo apt install git -y
```

**✅ Prüfen ob es funktioniert hat:**
```bash
git --version
# Erwartete Ausgabe: git version 2.43.0 (oder ähnlich)
```

---

### 1.2 Visual Studio Code (VSCode)

1. Öffne https://code.visualstudio.com/
2. Lade VSCode für dein Betriebssystem herunter
3. Installiere mit Standardeinstellungen
4. Windows: Aktiviere **"Add to PATH"** im Installer (wichtig für `code .` im Terminal!)

**✅ Prüfen ob es funktioniert hat:**
```bash
code --version
# Erwartete Ausgabe: 1.x.x
```

---

### 1.3 Docker Desktop

Docker startet alle Services (TimescaleDB, Redis, MinIO, API Gateway, Frontend) gleichzeitig.

**Windows:**
1. Öffne https://www.docker.com/products/docker-desktop/
2. Lade **Docker Desktop for Windows** herunter und installiere es
3. Starte deinen Computer neu
4. Starte Docker Desktop – warte bis das Symbol in der Taskleiste grün wird

> **Windows-Nutzer:** Docker benötigt WSL 2 (Windows Subsystem for Linux).  
> Der Installer richtet das automatisch ein.

**macOS:**
```bash
brew install --cask docker
# Dann: Docker Desktop aus dem Programme-Ordner öffnen
```

**Ubuntu 22.04 / Zorin OS 17:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Abmelden und wieder anmelden damit die Gruppe aktiv wird
sudo apt install docker-compose-plugin -y
```

**✅ Prüfen ob es funktioniert hat:**
```bash
docker --version
# Erwartete Ausgabe: Docker version 26.x.x

docker compose version
# Erwartete Ausgabe: Docker Compose version v2.x.x
```

---

### 1.4 Node.js

Wird für das Next.js 15 Frontend benötigt.

**Windows & macOS:**
1. Öffne https://nodejs.org/
2. Lade die **LTS**-Version herunter
3. Installiere mit Standardeinstellungen

**Ubuntu 22.04 / Zorin OS 17:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

**✅ Prüfen ob es funktioniert hat:**
```bash
node --version    # Erwartete Ausgabe: v20.x.x oder höher
npm --version     # Erwartete Ausgabe: 10.x.x oder höher
```

---

## 2. VSCode einrichten und Erweiterungen installieren

Das Projekt enthält `.vscode/extensions.json` – VSCode schlägt alle Erweiterungen automatisch vor.

1. Öffne VSCode
2. Extensions öffnen: **Strg+Shift+X** (Windows/Linux) oder **Cmd+Shift+X** (macOS)
3. Suche nach: `@recommended`
4. Klicke auf **"Install Workspace Recommended Extensions"**

Die wichtigsten Erweiterungen und wozu sie dienen:

| Erweiterung | Zweck |
|---|---|
| Python + Pylance + Black | Python-Code schreiben und formatieren |
| Prettier + ESLint | TypeScript/Next.js formatieren |
| REST Client | API-Tests direkt in VSCode (für `manual_tests.http`) |
| Docker | Container verwalten ohne Terminal |
| GitLens | Git-Historie nachvollziehen |
| Tailwind CSS IntelliSense | Autovervollständigung für shadcn/ui-Klassen |
| YAML + OpenAPI | `api/openapi.yaml` mit Syntax-Prüfung bearbeiten |

**✅ Prüfen ob es funktioniert hat:**  
Unten links in VSCode siehst du das Python- und Git-Symbol. Wenn du eine `.py`-Datei öffnest, erscheint der Interpreter-Status.

---

## 3. Repository klonen und öffnen

### Was bedeutet "klonen"?

Klonen = eine vollständige Kopie des Projekts auf deinen Computer herunterladen.

### 3.1 Repository klonen

Öffne ein Terminal:
- **Windows:** Git Bash (Rechtsklick → "Git Bash Here")
- **macOS/Linux:** Terminal

```bash
# Projektordner erstellen und öffnen
mkdir -p ~/Projekte
cd ~/Projekte

# Repository klonen
git clone https://github.com/loschi1982/ClimateWebsite.git

# In den Projektordner wechseln
cd ClimateWebsite
```

### 3.2 In den richtigen Branch wechseln

> ⚠️ **Jedes Team arbeitet NUR in seinem eigenen Branch** (Regel G1)  
> Als Developer Setup Team arbeitest du in `feature/developer-setup`.

```bash
# Zum richtigen Branch wechseln
git checkout feature/developer-setup

# Prüfen ob du im richtigen Branch bist
git branch
# Der aktive Branch hat ein * davor:
#   main
# * feature/developer-setup
```

**Alle Team-Branches auf einen Blick:**

| Branch | Team |
|---|---|
| `feature/data-pipeline` | Data Pipeline Team |
| `feature/climate-analysis` | Climate Analysis Team |
| `feature/visualization` | Visualization Team |
| `feature/simulation` | Simulation Team |
| `feature/frontend` | Frontend Team |
| `feature/ai-explanation` | AI Explanation Team |
| `feature/ux` | UX Team |
| `feature/documentation` | Documentation Team |
| `feature/developer-setup` | **Developer Setup Team (du!)** |

### 3.3 Projekt in VSCode öffnen

```bash
code .
```

VSCode öffnet das Projekt. Eine Meldung erscheint: *"Do you want to install the recommended extensions?"* → Klicke **Install All**.

**Repository-Struktur (vereinfacht):**
```
ClimateWebsite/
├── services/
│   └── api_gateway/          ← FastAPI Gateway (Einstiegspunkt Backend)
│       └── src/
│           ├── routers/       ← Ein Router pro Modul
│           └── main.py
├── modules/                  ← Kernmodule
│   ├── data_ingestion/       ← NASA, NOAA, Copernicus usw.
│   ├── climate_analysis/     ← Trends, Anomalien, Korrelationen
│   ├── visualization_engine/ ← Vega-Lite Spec Generator
│   ├── simulation_engine/    ← IPCC-Szenarien
│   ├── knowledge_base/       ← Wissensbasis
│   └── ai_explanation/       ← RAG + Claude-Artikel
├── frontend/                 ← Next.js 15 (App Router)
│   └── src/
│       ├── app/               ← Seiten: /, /explore, /articles, /admin
│       ├── components/        ← Charts, Exploration, UI
│       ├── lib/api.ts         ← Zentraler API-Client
│       └── types/climate.ts   ← TypeScript-Typen
├── api/
│   └── openapi.yaml          ← API-Spezifikation (alle Endpunkte)
├── data/
│   ├── sources/               ← Quellendefinitionen (YAML)
│   ├── scenarios/             ← IPCC-Szenario-Daten (RCP 2.6/4.5/8.5)
│   └── knowledge_seeds/       ← Erste Wissensbasis-Einträge
├── memory/                   ← Gemeinsame Projektdateien (LESEN!)
│   ├── project_memory.json    ← Projektgedächtnis
│   ├── project_description.md
│   ├── architecture.md
│   ├── api_contracts.md
│   └── team_tasks.md
├── tests/
│   ├── integration/
│   └── api/
│       └── manual_tests.http  ← REST-Client Testdatei (du bist hier!)
└── docker-compose.yml
```

**✅ Prüfen ob es funktioniert hat:**  
Im VSCode Explorer siehst du alle Ordner. Unten in der Statusleiste steht `feature/developer-setup`.

---

## 4. Umgebungsvariablen einrichten

### Was sind Umgebungsvariablen?

Sie enthalten Passwörter, API-Schlüssel und Adressen – und werden NICHT in Git gespeichert.

### 4.1 .env-Datei erstellen

```bash
# Windows (Git Bash) / macOS / Linux:
cp .env.example .env
```

### 4.2 .env-Datei anpassen

```bash
code .env
```

**Für den ersten Start reichen die Standardwerte!** Nur wenn du echte Klimadaten abrufen möchtest, trage API-Schlüssel ein:

```bash
# NASA GISS (kostenlos, https://api.nasa.gov/):
NASA_API_KEY=dein-schlüssel

# Anthropic Claude (für AI Explanation Modul, https://console.anthropic.com/):
ANTHROPIC_API_KEY=dein-schlüssel
```

> **WICHTIG (ADR-003):** KI-generierte Artikel werden niemals automatisch veröffentlicht.  
> Jeder Artikel hat immer `status: pending_review` und braucht menschliche Freigabe.

**✅ Prüfen ob es funktioniert hat:**
```bash
ls -la .env         # Datei muss existieren
git status          # .env darf NICHT in der Liste erscheinen (steht in .gitignore)
```

---

## 5. Docker starten und Services prüfen

### 5.1 Docker Desktop starten

- **Windows/macOS:** Docker Desktop öffnen – warte bis Symbol grün ist
- **Linux:** `sudo systemctl start docker`

### 5.2 Alle Services starten

```bash
# Im Projektordner (ClimateWebsite/):
docker compose up
```

**Beim ersten Start** lädt Docker alle Images herunter (ca. 5–10 Minuten). Du siehst viele Log-Nachrichten – das ist normal.

**Warte auf diese Meldungen:**
```
climateinsight_db      | database system is ready to accept connections
climateinsight_api     | Application startup complete.
climateinsight_frontend| ✓ Ready in 3.2s
```

**Im Hintergrund starten (empfohlen nach dem ersten Mal):**
```bash
docker compose up -d
```

### 5.3 Services prüfen

Öffne diese Adressen im Browser:

| Service | Adresse | Was du siehst |
|---|---|---|
| **API Gateway** | http://localhost:8000/health | `{"status": "ok"}` |
| **API Docs** | http://localhost:8000/docs | Automatische FastAPI-Dokumentation |
| **Frontend** | http://localhost:3000 | ClimateInsight Weboberfläche |
| **Swagger UI** | http://localhost:8080 | Interaktive API-Dokumentation (openapi.yaml) |
| **MinIO Web** | http://localhost:9001 | Objektspeicher für Rohdaten |

**MinIO-Login:** Benutzer `climateinsight` · Passwort `password123`

**Services stoppen:**
```bash
docker compose down         # Services stoppen (Daten bleiben erhalten)
docker compose down -v      # Services stoppen UND alle Daten löschen (Vorsicht!)
```

**✅ Prüfen ob es funktioniert hat:**
```bash
docker compose ps
# Alle 6 Container sollten Status "running" haben:
# climateinsight_api       running
# climateinsight_frontend  running
# climateinsight_db        running
# climateinsight_redis     running
# climateinsight_minio     running
# climateinsight_swagger   running
```

---

## 6. Erste API-Tests durchführen

### 6.1 REST Client in VSCode verwenden

1. Öffne: `tests/api/manual_tests.http`
2. Wähle Umgebung: Klick auf **"No Environment"** unten rechts → **"local"**
3. Scrolle zum ersten Request (`GET {{baseUrl}}/health`)
4. Klicke auf **"Send Request"** das über dem Request erscheint
5. Rechts öffnet sich ein Tab mit der Antwort:

```json
{
  "status": "ok",
  "version": "1.0"
}
```

### 6.2 Alle Module testen

Die `manual_tests.http`-Datei enthält Requests für alle sieben Module:

| Abschnitt | Was getestet wird |
|---|---|
| Health Check | Backend läuft |
| Ingestion | Datenquellen, Datensätze, Jobs abrufen |
| Analysis | Trendanalyse, Anomalien, Korrelation |
| Visualization | Diagramme erstellen und exportieren |
| Simulation | IPCC-Szenarien (RCP 2.6 / 4.5 / 8.5) |
| Knowledge Base | Wissensbasis suchen und erstellen |
| AI Explanation | Artikel generieren und reviewen |
| Exploration | Variablen vergleichen, Ansicht teilen |

**Empfohlene Reihenfolge:**
1. Health → prüfen ob Backend läuft
2. Ingestion Sources → Datenquellen sehen
3. Ingestion Datasets → Datensätze sehen
4. Analysis Run → Trendanalyse starten, `analysis_id` notieren
5. Visualization Create → Diagramm erstellen, `viz_id` notieren

**✅ Prüfen ob es funktioniert hat:**  
HTTP-Status 200 (oder 201/202) erscheint oben im Antwort-Tab.

---

## 7. Code einfügen

### 7.1 In welchen Ordner gehört mein Code?

Jedes Team hat einen klaren Bereich:

```
modules/data_ingestion/src/         ← Data Pipeline Team
modules/climate_analysis/src/       ← Climate Analysis Team
modules/visualization_engine/src/   ← Visualization Team
modules/simulation_engine/src/      ← Simulation Team
modules/knowledge_base/             ← Data Pipeline Team
modules/ai_explanation/src/         ← AI Explanation Team
services/api_gateway/src/routers/   ← Alle Teams (je ein Router)
frontend/src/                       ← Frontend Team
docs/                               ← Documentation Team
docs/deployment/                    ← Developer Setup Team (hier!)
.vscode/                            ← Developer Setup Team
```

> **Regel G1:** Du erstellst Dateien NUR in deinem Branch (`feature/developer-setup`).  
> Du änderst KEINE Dateien in `main` oder fremden Branches.

### 7.2 Neue Datei erstellen und committen

```bash
# Schritt 1: Prüfen ob du im richtigen Branch bist
git branch
# * feature/developer-setup  ← muss so aussehen

# Schritt 2: Datei erstellen (Beispiel)
touch docs/deployment/meine-neue-datei.md

# Schritt 3: Datei in VSCode öffnen und bearbeiten
code docs/deployment/meine-neue-datei.md

# Schritt 4: Änderungen anzeigen
git status

# Schritt 5: Änderungen für Commit vorbereiten
git add docs/deployment/meine-neue-datei.md
# oder alle Änderungen auf einmal:
git add .

# Schritt 6: Commit erstellen (Regel G2: Format beachten!)
git commit -m "docs(setup): Neue Anleitung hinzugefügt"

# Schritt 7: Auf GitHub hochladen
git push origin feature/developer-setup
```

### 7.3 Commit-Message Format (Regel G2)

```
typ(bereich): kurze Beschreibung
```

| Typ | Bedeutung | Beispiel |
|---|---|---|
| `feat` | Neues Feature | `feat(connector): NASA GISS Connector` |
| `fix` | Bugfix | `fix(api): Timeout in /ingestion/trigger` |
| `docs` | Dokumentation | `docs(setup): Troubleshooting ergänzt` |
| `test` | Tests | `test(analysis): OLS-Trend Unit Tests` |
| `refactor` | Code-Umbau | `refactor(pipeline): Validierung ausgelagert` |
| `chore` | Wartung/Konfiguration | `chore(docker): Port für MinIO korrigiert` |

> **Regel G4:** Wenn du `memory/project_memory.json` aktualisierst,  
> ist das ein eigener Commit: `chore(memory): [was du dokumentiert hast]`

### 7.4 Häufige Fehler

**Problem:** `error: failed to push some refs`
```bash
git pull origin feature/developer-setup
git push origin feature/developer-setup
```

**Problem:** Versehentlich auf `main` gearbeitet
```bash
git stash                              # Änderungen zwischenspeichern
git checkout feature/developer-setup   # Richtigen Branch wechseln
git stash pop                          # Änderungen wiederherstellen
```

**Problem:** Letzte Commit-Message korrigieren (nur wenn noch nicht gepusht!)
```bash
git commit --amend -m "feat(connector): NASA GISS Connector implementiert"
```

---

## 8. Troubleshooting

### Docker startet nicht

```bash
# Logs eines Services anzeigen:
docker compose logs api_gateway
docker compose logs db

# Alles stoppen und neu bauen:
docker compose down
docker compose up --build
```

**Windows:** Prüfe ob WSL 2 aktiv ist:
```powershell
# PowerShell als Administrator:
wsl --update
wsl --set-default-version 2
```

---

### Port bereits belegt

**Symptom:** `Error: bind: address already in use` (Port 8000, 3000, 5432 usw.)

```bash
# Windows (Git Bash):
netstat -ano | grep 8000
taskkill /PID 12345 /F

# macOS/Linux:
lsof -i :8000
kill -9 12345
```

---

### Python-Interpreter nicht gefunden

```bash
# Virtuelles Environment erstellen und aktivieren:
python -m venv .venv

# Windows (Git Bash):
source .venv/Scripts/activate

# macOS/Linux:
source .venv/bin/activate

# Abhängigkeiten installieren:
pip install -r services/api_gateway/requirements.txt
pip install -r modules/data_ingestion/requirements.txt
```

Dann in VSCode: **Strg+Shift+P** → `Python: Select Interpreter` → `.venv` wählen.

---

### API gibt 503 oder Verbindungsfehler zurück

```bash
# Ist die Datenbank bereit?
docker compose ps db
docker compose logs db

# Datenbank neu starten und warten:
docker compose restart db
sleep 15
curl http://localhost:8000/health
```

---

### Code-Änderungen werden nicht übernommen

**Backend (FastAPI):**  
`--reload` startet den Server automatisch neu. Falls nicht:
```bash
docker compose restart api_gateway
```

**Frontend (Next.js 15):**  
Hot-Reload ist eingebaut. Falls nicht:
```bash
docker compose restart frontend
```

---

### Nuclear Option – komplett neu starten

```bash
# Alles stoppen:
docker compose down

# Neu bauen:
docker compose up --build

# Alles löschen und von vorne (ALLE DATEN GEHEN VERLOREN!):
docker compose down -v --rmi local
docker compose up --build
```

---

## Schnellreferenz

```bash
# Services starten (Hintergrund):
docker compose up -d

# Services stoppen:
docker compose down

# Logs anzeigen:
docker compose logs -f api_gateway

# Container-Status:
docker compose ps

# Branch prüfen:
git branch

# Commiten und pushen:
git add .
git commit -m "typ(bereich): beschreibung"
git push origin feature/developer-setup

# Neueste Änderungen holen:
git pull origin feature/developer-setup
```

---

*Letzte Aktualisierung: 2026-03-07 · Developer Setup Team · Branch: `feature/developer-setup`*  
*Repository: loschi1982/ClimateWebsite*