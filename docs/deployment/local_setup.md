# ClimateInsight – Lokale Einrichtungsanleitung

> **Für wen ist diese Anleitung?**  
> Für absolute Anfänger ohne Vorkenntnisse. Jeder Schritt wird erklärt.  
> Wenn du noch nie ein Entwicklerprojekt aufgesetzt hast – kein Problem!

> **Betriebssysteme:** Windows 10/11 · macOS 12+ · Ubuntu 22.04+

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

Git ist ein Versionskontrollsystem. Es merkt sich jede Änderung an Dateien und ermöglicht die Zusammenarbeit mit anderen Entwicklern.

**Windows:**
1. Öffne https://git-scm.com/download/win
2. Lade den Installer herunter und führe ihn aus
3. Klicke überall auf **Next** – die Standardeinstellungen sind richtig
4. Wähle bei "Default editor" → **Visual Studio Code** (wenn du es bereits installiert hast)

**macOS:**
```bash
# Homebrew (ein Paketmanager) installieren – falls noch nicht vorhanden:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git installieren:
brew install git
```

**Ubuntu/Linux:**
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

VSCode ist ein kostenloser Code-Editor der für dieses Projekt konfiguriert ist.

1. Öffne https://code.visualstudio.com/
2. Lade VSCode für dein Betriebssystem herunter
3. Installiere es mit den Standardeinstellungen

**✅ Prüfen ob es funktioniert hat:**  
Öffne VSCode – das Programm sollte sich öffnen ohne Fehlermeldung.

---

### 1.3 Docker Desktop

Docker startet alle Services (Datenbank, Backend, Frontend) in isolierten Containern. Du brauchst keine Programme manuell zu installieren.

**Windows:**
1. Öffne https://www.docker.com/products/docker-desktop/
2. Lade **Docker Desktop for Windows** herunter
3. Installiere es und starte deinen Computer neu
4. Starte Docker Desktop – warte bis das Docker-Symbol in der Taskleiste grün wird

> **Windows-Nutzer:** Docker benötigt WSL 2 (Windows Subsystem for Linux).  
> Der Installer richtet das automatisch ein – folge den Anweisungen auf dem Bildschirm.

**macOS:**
```bash
brew install --cask docker
# Dann öffne Docker Desktop aus dem Programme-Ordner
```

**Ubuntu/Linux:**
```bash
# Docker Engine installieren:
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Abmelden und neu anmelden damit die Gruppe aktiv wird

# Docker Compose Plugin:
sudo apt install docker-compose-plugin -y
```

**✅ Prüfen ob es funktioniert hat:**
```bash
docker --version
# Erwartete Ausgabe: Docker version 26.x.x, build ...

docker compose version
# Erwartete Ausgabe: Docker Compose version v2.x.x
```

---

### 1.4 Node.js

Node.js wird für das Next.js Frontend benötigt.

**Windows & macOS:**
1. Öffne https://nodejs.org/
2. Lade die **LTS**-Version herunter (die empfohlene stabile Version)
3. Installiere mit Standardeinstellungen

**Ubuntu/Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

**✅ Prüfen ob es funktioniert hat:**
```bash
node --version
# Erwartete Ausgabe: v20.x.x (oder höher)

npm --version
# Erwartete Ausgabe: 10.x.x (oder höher)
```

---

## 2. VSCode einrichten und Erweiterungen installieren

### 2.1 Erweiterungen installieren

Das Projekt enthält eine Datei `.vscode/extensions.json` mit allen empfohlenen Erweiterungen. VSCode installiert sie automatisch.

1. Öffne VSCode
2. Öffne den Extensions-Bereich: **Strg+Shift+X** (Windows/Linux) oder **Cmd+Shift+X** (macOS)
3. Tippe in die Suchleiste: `@recommended`
4. Klicke auf den **Cloud-mit-Pfeil-Button** ("Install Workspace Recommended Extensions")

**Alternativ – Erweiterungen einzeln suchen und installieren:**

| Erweiterung | Wozu? |
|---|---|
| Python | Python-Code verstehen und ausführen |
| Black Formatter | Python-Code automatisch formatieren |
| Pylint | Python-Fehler erkennen |
| Prettier | TypeScript/JavaScript formatieren |
| ESLint | TypeScript-Fehler erkennen |
| Docker | Container verwalten |
| REST Client | API-Tests direkt in VSCode |
| GitLens | Git-Historie anzeigen |

**✅ Prüfen ob es funktioniert hat:**  
Unten links in VSCode siehst du Symbole für Python und Git. Wenn du eine `.py`-Datei öffnest, erscheint oben der Interpreter-Status.

---

## 3. Repository klonen und öffnen

### Was bedeutet "klonen"?

Klonen bedeutet: eine Kopie des Projekts auf deinen Computer herunterladen.

### 3.1 Repository klonen

Öffne ein Terminal:
- **Windows:** Rechtsklick auf den Desktop → "Git Bash Here" (oder Suche nach "Git Bash")
- **macOS/Linux:** Terminal-App öffnen

```bash
# Navigiere zu dem Ordner wo du das Projekt speichern möchtest.
# Beispiel: Ordner "Projekte" im Home-Verzeichnis erstellen und öffnen
mkdir -p ~/Projekte
cd ~/Projekte

# Repository klonen (herunterladen):
git clone https://github.com/loschi1982/ClimateWebsite.git

# In den Projektordner wechseln:
cd ClimateWebsite
```

### 3.2 In den richtigen Branch wechseln

> ⚠️ **Wichtige Regel:** Jedes Team arbeitet NUR in seinem eigenen Branch!  
> Als Developer Setup Team arbeitest du in `feature/developer-setup`.

```bash
# Zum Developer Setup Branch wechseln:
git checkout feature/developer-setup

# Prüfen ob du im richtigen Branch bist:
git branch
# Der aktive Branch hat ein * davor:
#   main
# * feature/developer-setup
```

### 3.3 Projekt in VSCode öffnen

```bash
# Projekt in VSCode öffnen (im selben Terminal-Fenster):
code .
```

**Was passiert als nächstes:**  
VSCode öffnet das Projekt. Unten rechts erscheint eine Meldung: *"Do you want to install the recommended extensions?"* → Klicke auf **Install All**.

**✅ Prüfen ob es funktioniert hat:**  
Im VSCode Explorer (links) siehst du alle Projektdateien. Unten in der Statusleiste steht `feature/developer-setup`.

---

## 4. Umgebungsvariablen einrichten

### Was sind Umgebungsvariablen?

Umgebungsvariablen sind wie Einstellungen für deine Anwendung: Passwörter, Adressen und API-Schlüssel. Sie stehen in einer `.env`-Datei die **niemals in Git eingecheckt wird** (damit Passwörter nicht öffentlich werden).

### 4.1 .env-Datei aus der Vorlage erstellen

```bash
# Windows (Git Bash):
cp .env.example .env

# macOS/Linux:
cp .env.example .env
```

### 4.2 .env-Datei öffnen und anpassen

```bash
# Datei in VSCode öffnen:
code .env
```

**Für die lokale Entwicklung musst du fast nichts ändern!** Die Standardwerte in `.env.example` funktionieren direkt mit Docker Compose.

**Optional: API-Schlüssel eintragen (für echte Klimadaten)**

Wenn du echte NASA- oder NOAA-Daten abrufen möchtest, trage deine API-Schlüssel ein:

```bash
# In .env:
NASA_API_KEY=dein-schlüssel-hier       # https://api.nasa.gov/
NOAA_API_TOKEN=dein-token-hier         # https://www.ncdc.noaa.gov/cdo-web/token
ANTHROPIC_API_KEY=dein-schlüssel-hier  # https://console.anthropic.com/
```

Für den ersten Start mit Testdaten reichen die Standardwerte.

**✅ Prüfen ob es funktioniert hat:**

```bash
# Prüfe ob die .env-Datei existiert:
ls -la .env
# Ausgabe: -rw-r--r-- 1 ... .env

# Prüfe dass die Datei NICHT in Git getrackt wird:
git status
# Die .env-Datei sollte NICHT in der Ausgabe erscheinen
```

---

## 5. Docker starten und Services prüfen

### 5.1 Docker Desktop starten

Stelle sicher dass Docker Desktop läuft:
- **Windows/macOS:** Docker Desktop öffnen – warte bis das Symbol grün ist / "Docker Desktop is running" erscheint
- **Linux:** `sudo systemctl start docker`

### 5.2 Alle Services starten

```bash
# Im Projektordner (ClimateWebsite):
docker compose up
```

**Was passiert jetzt?**  
Docker lädt alle benötigten Images herunter (beim ersten Start ca. 5–10 Minuten) und startet alle Services. Du siehst viele Log-Nachrichten – das ist normal!

**Warte auf diese Meldungen:**
```
climateinsight_db      | database system is ready to accept connections
climateinsight_api     | Application startup complete.
climateinsight_frontend| Ready in 3.2s
```

**Im Hintergrund starten (empfohlen nach dem ersten Mal):**
```bash
# -d = detached (im Hintergrund)
docker compose up -d
```

### 5.3 Services prüfen

Öffne diese Adressen im Browser – sie sollten alle funktionieren:

| Service | Adresse | Was du siehst |
|---|---|---|
| **API Backend** | http://localhost:8000/health | `{"status": "ok"}` |
| **API Docs** | http://localhost:8000/docs | Interaktive Swagger-Dokumentation |
| **Frontend** | http://localhost:3000 | ClimateInsight Weboberfläche |
| **Swagger UI** | http://localhost:8080 | Alternative API-Dokumentation |
| **MinIO** | http://localhost:9001 | Dateispeicher-Weboberfläche |

**Anmeldung MinIO:** Benutzer: `climateinsight` · Passwort: `password123`

**Services stoppen:**
```bash
# Alle Services stoppen:
docker compose down

# Alle Services stoppen UND alle Daten löschen (Vorsicht!):
docker compose down -v
```

**✅ Prüfen ob es funktioniert hat:**
```bash
# Zeigt alle laufenden Container:
docker compose ps

# Alle Container sollten den Status "running" haben:
# NAME                     STATUS
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

1. Öffne in VSCode die Datei: `tests/api/manual_tests.http`
2. Wähle die Umgebung: Klick auf **"No Environment"** unten rechts → wähle **"local"**
3. Fahre mit der Maus über den ersten Request:
   ```
   GET http://localhost:8000/health
   ```
4. Klicke auf **"Send Request"** das über dem Request erscheint
5. Rechts öffnet sich ein Tab mit der Antwort:
   ```json
   {
     "status": "ok",
     "version": "1.0.0"
   }
   ```

### 6.2 Ersten echten Request senden

Teste den Ingestion-Endpoint um verfügbare Datensätze zu sehen:

1. Scrolle in `manual_tests.http` zu `# INGESTION: Alle verfügbaren Datensätze auflisten`
2. Klicke auf "Send Request"
3. Du siehst alle verfügbaren Klimadatensätze

**✅ Prüfen ob es funktioniert hat:**  
Du bekommst eine JSON-Antwort ohne Fehlermeldung. HTTP-Status 200 erscheint oben im Antwort-Tab.

---

## 7. Code einfügen

### 7.1 In welche Datei gehört mein Code?

Jedes Team hat seinen eigenen Ordner:

```
ClimateWebsite/
├── api/                    ← Backend (Python/FastAPI)
│   ├── ingestion/          ← Data Pipeline Team
│   ├── analysis/           ← Climate Analysis Team
│   ├── simulation/         ← Simulation Team
│   └── ai_explanation/     ← AI Explanation Team
├── frontend/               ← Frontend Team (Next.js)
├── docs/                   ← Documentation Team
│   └── deployment/         ← Developer Setup Team (hier!)
└── memory/                 ← Gemeinsame Projektdateien
```

### 7.2 Neue Datei erstellen

```bash
# Beispiel: Neue Python-Datei im richtigen Ordner erstellen
touch api/ingestion/my_new_connector.py

# Dann in VSCode öffnen:
code api/ingestion/my_new_connector.py
```

### 7.3 Änderungen speichern und committen

> ⚠️ **Erst prüfen:** Bist du im richtigen Branch?
> ```bash
> git branch  # Der aktive Branch hat ein * davor
> ```

```bash
# Schritt 1: Welche Dateien hast du geändert?
git status

# Schritt 2: Änderungen für den Commit vorbereiten ("stagen")
# Einzelne Datei:
git add api/ingestion/my_new_connector.py

# Alle Änderungen auf einmal:
git add .

# Schritt 3: Commit mit aussagekräftiger Message erstellen
# Format: typ(bereich): kurze Beschreibung
git commit -m "feat(connector): NASA GISS Connector implementiert"

# Schritt 4: Änderungen auf GitHub hochladen ("pushen")
git push origin feature/developer-setup
```

**Erlaubte Commit-Typen:**

| Typ | Bedeutung | Beispiel |
|---|---|---|
| `feat` | Neues Feature | `feat(connector): NOAA Connector hinzugefügt` |
| `fix` | Bugfix | `fix(api): Timeout-Fehler behoben` |
| `docs` | Dokumentation | `docs(setup): Anleitung ergänzt` |
| `test` | Tests | `test(analysis): Unit Tests für Trend` |
| `refactor` | Code-Umbau | `refactor(pipeline): Klasse aufgeteilt` |
| `chore` | Wartung | `chore(deps): Pakete aktualisiert` |

### 7.4 Häufige Fehler beim Committing

**Problem:** `error: failed to push some refs`  
**Lösung:** Hole zuerst die neuesten Änderungen:
```bash
git pull origin feature/developer-setup
# Dann erneut pushen:
git push origin feature/developer-setup
```

**Problem:** Versehentlich auf `main` gearbeitet  
**Lösung:**
```bash
# Änderungen temporär speichern:
git stash

# Zum richtigen Branch wechseln:
git checkout feature/developer-setup

# Gespeicherte Änderungen wiederherstellen:
git stash pop
```

**Problem:** Commit-Message falsch geschrieben  
**Lösung:** (nur wenn noch nicht gepusht!)
```bash
git commit --amend -m "feat(connector): NASA GISS Connector implementiert"
```

---

## 8. Troubleshooting

### Problem: Docker startet nicht

**Symptom:** `docker compose up` gibt Fehler aus oder Container starten nicht.

```bash
# Logs eines bestimmten Services anzeigen:
docker compose logs api_gateway
docker compose logs db

# Alles stoppen und neu starten:
docker compose down
docker compose up --build
```

**Windows-spezifisch:** Stelle sicher dass WSL 2 aktiviert ist:
```powershell
# In PowerShell (als Administrator):
wsl --update
wsl --set-default-version 2
```

---

### Problem: Port bereits belegt

**Symptom:** `Error: bind: address already in use` für Port 8000, 3000 oder 5432.

```bash
# Welches Programm nutzt Port 8000?
# Windows (Git Bash):
netstat -ano | grep 8000
# macOS/Linux:
lsof -i :8000

# Prozess beenden (ersetze PID mit der Prozess-ID aus dem vorherigen Befehl):
# Windows:
taskkill /PID 12345 /F
# macOS/Linux:
kill -9 12345
```

---

### Problem: Python-Interpreter nicht gefunden

**Symptom:** VSCode zeigt "No Python interpreter selected" oder Importe werden nicht erkannt.

```bash
# Virtuelles Environment erstellen:
python -m venv .venv

# Aktivieren:
# Windows (Git Bash):
source .venv/Scripts/activate
# macOS/Linux:
source .venv/bin/activate

# Abhängigkeiten installieren:
pip install -r requirements.txt
```

Dann in VSCode: **Strg+Shift+P** → "Python: Select Interpreter" → `.venv` auswählen.

---

### Problem: npm-Fehler beim Frontend

**Symptom:** `npm install` oder `npm run dev` schlägt fehl.

```bash
cd frontend

# node_modules löschen und neu installieren:
rm -rf node_modules package-lock.json
npm install

# Oder mit Docker (empfohlen):
docker compose up frontend --build
```

---

### Problem: Datenbank-Verbindungsfehler

**Symptom:** API gibt `connection refused` für PostgreSQL zurück.

```bash
# Ist die Datenbank überhaupt gestartet?
docker compose ps db

# Logs der Datenbank anzeigen:
docker compose logs db

# Datenbank neu starten:
docker compose restart db

# Warte 10 Sekunden und teste erneut:
sleep 10
curl http://localhost:8000/health/detailed
```

---

### Problem: Änderungen werden nicht übernommen

**Symptom:** Du änderst Code, aber im Browser ist noch die alte Version.

**Backend (FastAPI):**  
Wenn `--reload` in der Docker-Konfiguration aktiv ist (Standard in `docker-compose.override.yml`), sollte der Server automatisch neu starten. Falls nicht:
```bash
docker compose restart api_gateway
```

**Frontend (Next.js):**  
Next.js hat Hot-Reload eingebaut. Falls es nicht funktioniert:
```bash
docker compose restart frontend
```

---

### Alle Container neu starten (Nuclear Option)

Wenn gar nichts mehr funktioniert:

```bash
# Alles stoppen:
docker compose down

# Alle Images neu bauen (dauert länger):
docker compose up --build

# Oder: Alles löschen und von vorne (ALLE DATEN GEHEN VERLOREN!):
docker compose down -v --rmi local
docker compose up --build
```

---

## Schnellreferenz: Die wichtigsten Befehle

```bash
# Services starten:
docker compose up -d

# Services stoppen:
docker compose down

# Logs anzeigen:
docker compose logs -f api_gateway

# Container-Status:
docker compose ps

# Branch prüfen:
git branch

# Änderungen committen:
git add .
git commit -m "feat(bereich): beschreibung"
git push origin feature/developer-setup

# Neueste Änderungen holen:
git pull origin feature/developer-setup
```

---

*Letzte Aktualisierung: 2025 · Developer Setup Team · Branch: `feature/developer-setup`*