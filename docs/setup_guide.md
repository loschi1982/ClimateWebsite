# Entwicklungsumgebung einrichten – Schritt-für-Schritt-Anleitung
*Betriebssystem: Zorin OS 17 | Zielgruppe: Anfänger ohne Vorkenntnisse*

---

## Was wir in dieser Anleitung einrichten

Am Ende dieser Anleitung hast du folgendes auf deinem Computer:

- **Git** – um den Quellcode zu verwalten und mit GitHub zu synchronisieren
- **Python 3.11+** – für das Backend (die „Rechenmaschine" im Hintergrund)
- **Node.js** – für das Frontend (die Webseite im Browser)
- **Visual Studio Code** – als Texteditor für den Code
- Das **Klimaplattform-Projekt** läuft lokal auf deinem Computer

Die gesamte Einrichtung dauert etwa **30–45 Minuten**.

---

## Voraussetzungen

- Zorin OS 17 ist installiert und startet normal
- Du hast Internetzugang
- Du hast ein GitHub-Konto (kostenlos erstellen auf [github.com](https://github.com))

---

## Schritt 1: Terminal öffnen

Das Terminal ist das wichtigste Werkzeug für Entwickler. Es ist ein Textfenster,
in das du Befehle eingibst.

**So öffnest du das Terminal in Zorin OS 17:**

1. Drücke gleichzeitig die Tasten `Strg` + `Alt` + `T`
2. Ein schwarzes Fenster öffnet sich – das ist das Terminal
3. Du siehst einen blinkenden Cursor und deinen Benutzernamen

> 💡 **Tipp:** Befehle werden immer mit der `Enter`-Taste bestätigt.
> Wenn du einen Befehl kopierst und einfügst, nutze im Terminal `Strg` + `Umschalt` + `V` (nicht `Strg` + `V`).

---

## Schritt 2: System aktualisieren

Bevor wir Software installieren, aktualisieren wir das System.
Das stellt sicher, dass alle Programme auf dem neuesten Stand sind.

Gib im Terminal folgenden Befehl ein und drücke `Enter`:

```bash
sudo apt update && sudo apt upgrade -y
```

> 💡 **Was bedeutet das?**
> `sudo` bedeutet „mit Administratorrechten ausführen".
> Das System fragt dich nach deinem Passwort – tippe es ein (du siehst keine Sterne, das ist normal) und drücke `Enter`.

Warte, bis der Vorgang abgeschlossen ist. Das kann einige Minuten dauern.

---

## Schritt 3: Git installieren

Git ist ein Programm, das alle Änderungen am Code speichert und es ermöglicht,
mit anderen zusammenzuarbeiten.

```bash
sudo apt install git -y
```

**Prüfen, ob Git installiert wurde:**

```bash
git --version
```

Du solltest eine Ausgabe wie `git version 2.x.x` sehen.

**Git mit deinem Namen und deiner E-Mail konfigurieren:**
(Diese Angaben erscheinen später bei deinen Code-Beiträgen auf GitHub.)

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine@email.de"
```

> 💡 Ersetze `Dein Name` und `deine@email.de` durch deine echten Angaben.
> Verwende dieselbe E-Mail-Adresse wie bei deinem GitHub-Konto.

---

## Schritt 4: Python installieren

Python ist die Programmiersprache, mit der das Backend geschrieben ist.
Zorin OS 17 hat Python bereits vorinstalliert, wir stellen aber sicher, dass Version 3.11+ vorhanden ist.

**Aktuelle Version prüfen:**

```bash
python3 --version
```

Wenn du `Python 3.11.x` oder höher siehst, kannst du zu Schritt 5 springen.

**Falls die Version älter ist, installiere Python 3.11:**

```bash
sudo apt install python3.11 python3.11-venv python3-pip -y
```

**pip installieren** (pip ist der Paketmanager für Python-Bibliotheken):

```bash
sudo apt install python3-pip -y
```

**Prüfen:**

```bash
python3 --version
pip3 --version
```

---

## Schritt 5: Node.js installieren

Node.js wird benötigt, um das React-Frontend zu starten.
Wir installieren die aktuelle LTS-Version (Long Term Support = langfristig unterstützte Version).

```bash
# Node.js-Installationsquelle hinzufügen
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Node.js installieren
sudo apt install nodejs -y
```

**Prüfen:**

```bash
node --version
npm --version
```

Du solltest `v20.x.x` und `10.x.x` (oder höher) sehen.

> 💡 **Was ist npm?**
> npm (Node Package Manager) wird automatisch mit Node.js installiert.
> Es ist der Paketmanager für JavaScript-Bibliotheken – ähnlich wie pip für Python.

---

## Schritt 6: Visual Studio Code installieren

Visual Studio Code (kurz: VS Code) ist der Texteditor, in dem wir den Code schreiben.

```bash
# Microsoft-Paketquelle hinzufügen
sudo apt install wget gpg -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg

sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] \
https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

# VS Code installieren
sudo apt update
sudo apt install code -y
```

**VS Code starten:**

```bash
code
```

Oder suche im Zorin-Startmenü nach „Visual Studio Code".

---

## Schritt 7: GitHub-Repository klonen

„Klonen" bedeutet: Den Quellcode vom GitHub-Server auf deinen Computer herunterladen.

**Zuerst: Einen Ordner für deine Projekte erstellen**

```bash
mkdir ~/Projekte
cd ~/Projekte
```

> 💡 `mkdir` erstellt einen neuen Ordner. `cd` wechselt in diesen Ordner.

**Repository klonen:**

```bash
git clone https://github.com/dein-nutzername/klimaplattform.git
```

> ⚠️ Ersetze `dein-nutzername` durch deinen GitHub-Benutzernamen.

**In den Projektordner wechseln:**

```bash
cd klimaplattform
```

**Prüfen, ob alles da ist:**

```bash
ls
```

Du solltest die Ordner `backend`, `frontend`, `docs`, `memory` und die Datei `README.md` sehen.

---

## Schritt 8: In den richtigen Branch wechseln

Jedes Team arbeitet in einem eigenen Branch (einer eigenen „Arbeitsebene").
Wechsle in den Branch deines Teams:

```bash
# Beispiel für das Data Pipeline Team:
git checkout team/data-pipeline

# Beispiel für das Frontend Team:
git checkout team/frontend
```

**Den aktuellen Branch anzeigen:**

```bash
git branch
```

Der aktive Branch ist mit einem `*` markiert.

---

## Schritt 9: Backend einrichten

Das Backend ist der Python-Server, der die Daten verarbeitet.

**In den Backend-Ordner wechseln:**

```bash
cd ~/Projekte/klimaplattform/backend
```

**Virtuelle Python-Umgebung erstellen:**

```bash
python3 -m venv venv
```

> 💡 **Was ist eine virtuelle Umgebung?**
> Sie ist ein isolierter Bereich für Python-Bibliotheken.
> So bleiben die Bibliotheken dieses Projekts von anderen Projekten getrennt.

**Virtuelle Umgebung aktivieren:**

```bash
source venv/bin/activate
```

Du erkennst, dass die Umgebung aktiv ist, wenn vor deinem Cursor `(venv)` steht.

> ⚠️ **Wichtig:** Du musst die virtuelle Umgebung jedes Mal aktivieren,
> wenn du ein neues Terminal öffnest und am Backend arbeiten möchtest.

**Python-Bibliotheken installieren:**

```bash
pip install -r requirements.txt
```

Das installiert alle Bibliotheken, die das Backend benötigt (FastAPI, pandas, numpy usw.).

**Umgebungsvariablen einrichten:**

```bash
cd ~/Projekte/klimaplattform
cp .env.example .env
```

Öffne die `.env`-Datei in VS Code:

```bash
code .env
```

Trage deinen Anthropic API-Key ein (wird vom AI Explanation Team benötigt):

```
ANTHROPIC_API_KEY=dein-api-key-hier
```

Speichere die Datei mit `Strg` + `S`.

---

## Schritt 10: Backend-Server starten

```bash
cd ~/Projekte/klimaplattform/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

> 💡 **Was bedeutet `--reload`?**
> Der Server startet automatisch neu, wenn du Code-Änderungen speicherst.
> Das ist sehr praktisch beim Entwickeln.

**Prüfen, ob der Server läuft:**

Öffne deinen Browser und gib ein:
```
http://localhost:8000/docs
```

Du solltest eine Seite mit allen API-Endpunkten sehen (Swagger UI).

> ✅ Wenn du die API-Dokumentation siehst, läuft das Backend korrekt.

---

## Schritt 11: Frontend einrichten

Das Frontend ist die Webseite, die du im Browser siehst.
Öffne ein **neues Terminal** (das Backend-Terminal läuft weiter).

**In den Frontend-Ordner wechseln:**

```bash
cd ~/Projekte/klimaplattform/frontend
```

**Node.js-Pakete installieren:**

```bash
npm install
```

Das lädt alle JavaScript-Bibliotheken herunter (React, Tailwind usw.).
Das kann beim ersten Mal einige Minuten dauern.

---

## Schritt 12: Frontend-Server starten

```bash
npm run dev
```

Du siehst eine Ausgabe wie:

```
  VITE v5.x.x  ready in 300ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Prüfen, ob das Frontend läuft:**

Öffne deinen Browser und gib ein:
```
http://localhost:5173
```

Du solltest die Klimaplattform-Startseite sehen.

> ✅ Wenn die Seite lädt, ist alles korrekt eingerichtet.

---

## Zusammenfassung: Lokale Entwicklung starten

Ab jetzt brauchst du für jede Entwicklungssitzung nur noch diese Befehle:

**Terminal 1 – Backend:**
```bash
cd ~/Projekte/klimaplattform/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 – Frontend:**
```bash
cd ~/Projekte/klimaplattform/frontend
npm run dev
```

**Dann im Browser öffnen:**
- Webseite:       http://localhost:5173
- API-Dokumentation: http://localhost:8000/docs

---

## Schritt 13: VS Code für das Projekt einrichten

**Projektordner in VS Code öffnen:**

```bash
code ~/Projekte/klimaplattform
```

**Empfohlene VS Code-Erweiterungen installieren:**

Öffne in VS Code die Erweiterungssuche mit `Strg` + `Umschalt` + `X` und installiere:

| Erweiterung | Warum? |
|---|---|
| `Python` (Microsoft) | Python-Unterstützung, Autovervollständigung |
| `Pylance` | Bessere Python-Fehlererkennung |
| `ESLint` | Fehler in JavaScript/React finden |
| `Prettier` | Code automatisch formatieren |
| `Tailwind CSS IntelliSense` | Tailwind-Klassen vorschlagen |
| `GitLens` | Git-Verlauf direkt in VS Code anzeigen |

---

## Häufige Probleme und Lösungen

### Problem: „Permission denied" bei einem Befehl
**Lösung:** Füge `sudo` vor den Befehl ein.
```bash
sudo apt install ...
```

---

### Problem: `python3` nicht gefunden
**Lösung:**
```bash
sudo apt install python3 -y
```

---

### Problem: `npm` nicht gefunden nach Node.js-Installation
**Lösung:** Terminal schließen, neu öffnen und erneut versuchen.
```bash
source ~/.bashrc
npm --version
```

---

### Problem: Backend startet nicht – „ModuleNotFoundError"
**Lösung:** Virtuelle Umgebung ist nicht aktiviert.
```bash
source venv/bin/activate
```
Du siehst dann `(venv)` vor deinem Cursor.

---

### Problem: Frontend startet nicht – „ENOENT: no such file or directory"
**Lösung:** `npm install` wurde nicht ausgeführt.
```bash
cd ~/Projekte/klimaplattform/frontend
npm install
npm run dev
```

---

### Problem: Browser zeigt „Cannot connect" bei localhost:8000
**Lösung:** Der Backend-Server läuft nicht. Starte ihn in einem neuen Terminal:
```bash
cd ~/Projekte/klimaplattform/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

---

## Git-Grundbefehle (für den Alltag)

Diese Befehle brauchst du regelmäßig:

```bash
# Aktuellen Status anzeigen (welche Dateien wurden geändert?)
git status

# Alle Änderungen zum nächsten Commit hinzufügen
git add .

# Änderungen speichern (mit kurzer Beschreibung)
git commit -m "Kurze Beschreibung der Änderung"

# Änderungen zu GitHub hochladen
git push

# Neueste Änderungen von GitHub herunterladen
git pull

# Aktuellen Branch anzeigen
git branch

# In einen anderen Branch wechseln
git checkout team/mein-team
```

> ⚠️ **Wichtige Regel:** Committe NIE direkt in den `main`-Branch.
> Arbeite immer in deinem Team-Branch und erstelle einen Pull Request.

---

## Nächste Schritte

Jetzt, da deine Umgebung eingerichtet ist:

1. Lies die [Architektur-Dokumentation](architecture.md) um das Gesamtbild zu verstehen
2. Schau in [memory/team_tasks.md](../memory/team_tasks.md) welche Aufgaben dein Team hat
3. Lies [CONTRIBUTING.md](../CONTRIBUTING.md) um zu verstehen, wie Pull Requests funktionieren
4. Starte mit der ersten offenen Aufgabe deines Teams

Bei Fragen: Öffne ein [GitHub Issue](https://github.com/dein-nutzername/klimaplattform/issues).

---

*Letzte Aktualisierung: 2025-01-01 | Verantwortlich: Documentation Team*