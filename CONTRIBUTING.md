# Mitmachen – Klimaplattform
*Anleitung für Beitragende | Zielgruppe: Anfänger*

Herzlich willkommen! Diese Anleitung erklärt, wie du zum Projekt beitragen kannst –
auch wenn du noch wenig Erfahrung mit Git oder GitHub hast.

---

## Inhaltsverzeichnis

- [Mitmachen – Klimaplattform](#mitmachen--klimaplattform)
  - [Inhaltsverzeichnis](#inhaltsverzeichnis)
  - [1. Grundregeln](#1-grundregeln)
  - [2. Branch-Struktur verstehen](#2-branch-struktur-verstehen)
  - [3. Typischer Arbeitsablauf](#3-typischer-arbeitsablauf)
    - [Schritt 1: Neuesten Stand holen](#schritt-1-neuesten-stand-holen)
    - [Schritt 2: Aufgabe auswählen](#schritt-2-aufgabe-auswählen)
    - [Schritt 3: Code schreiben](#schritt-3-code-schreiben)
    - [Schritt 4: Änderungen speichern (Commit)](#schritt-4-änderungen-speichern-commit)
    - [Schritt 5: Zu GitHub hochladen](#schritt-5-zu-github-hochladen)
  - [4. Pull Request erstellen](#4-pull-request-erstellen)
  - [5. Code-Standards](#5-code-standards)
    - [Python (Backend)](#python-backend)
    - [JavaScript / React (Frontend)](#javascript--react-frontend)
  - [6. Tests schreiben und ausführen](#6-tests-schreiben-und-ausführen)
    - [Backend-Tests (pytest)](#backend-tests-pytest)
    - [Frontend-Tests (Vitest)](#frontend-tests-vitest)
  - [7. Projektgedächtnis aktualisieren](#7-projektgedächtnis-aktualisieren)
  - [8. Neue Datenquelle hinzufügen](#8-neue-datenquelle-hinzufügen)
  - [9. Neue Visualisierung hinzufügen](#9-neue-visualisierung-hinzufügen)
  - [10. Häufige Fehler vermeiden](#10-häufige-fehler-vermeiden)

---

## 1. Grundregeln

Diese Regeln gelten für alle Teams und alle Beiträge:

- **Kein direkter Commit in `main`.** Immer über einen Pull Request.
- **Jede Aufgabe bekommt einen eigenen Commit** mit einer verständlichen Nachricht.
- **Architekturentscheidungen** werden nicht allein getroffen – immer in `project_memory.json` dokumentieren.
- **API-Änderungen** erfordern die Zustimmung aller betroffenen Teams.
- **KI-generierte Artikel** erhalten immer `status: "draft"` – niemals automatisch veröffentlichen.
- **Quellenangaben** müssen immer sichtbar sein.

---

## 2. Branch-Struktur verstehen

```
main                    ← Gemeinsame Dateien. Kein direkter Commit.
├── team/data-pipeline
├── team/climate-analysis
├── team/visualization
├── team/simulation
├── team/frontend
├── team/ai-explanation
├── team/ux
└── team/documentation
```

Jedes Team arbeitet ausschließlich in seinem eigenen Branch.
Änderungen an gemeinsamen Dateien (z. B. `project_memory.json`) kommen per Pull Request in `main`.

**Aktuellen Branch anzeigen:**
```bash
git branch
```

**In deinen Team-Branch wechseln:**
```bash
git checkout team/mein-team
```

---

## 3. Typischer Arbeitsablauf

### Schritt 1: Neuesten Stand holen

Bevor du anfängst zu arbeiten, hole dir die aktuellen Änderungen:

```bash
# Zum main-Branch wechseln
git checkout main

# Neuesten Stand von GitHub holen
git pull

# Zurück in deinen Team-Branch wechseln
git checkout team/mein-team

# Änderungen aus main in deinen Branch übernehmen
git merge main
```

### Schritt 2: Aufgabe auswählen

Öffne `memory/team_tasks.md` und suche nach einer Aufgabe mit Status 🔴 (offen) für dein Team.

### Schritt 3: Code schreiben

Schreibe deinen Code in deinem Team-Branch. Speichere regelmäßig mit Git.

### Schritt 4: Änderungen speichern (Commit)

```bash
# Prüfen, welche Dateien geändert wurden
git status

# Alle geänderten Dateien hinzufügen
git add .

# Commit mit einer verständlichen Beschreibung
git commit -m "DP-01: NASA GISS Temperaturdaten abrufen und normalisieren"
```

> 💡 **Gute Commit-Nachrichten:**
> - Beginne mit der Aufgaben-ID (z. B. `DP-01`, `CA-03`, `FE-07`)
> - Beschreibe kurz, was du gemacht hast
> - Beispiel: `CA-02: Pearson-Korrelation implementiert`

### Schritt 5: Zu GitHub hochladen

```bash
git push
```

Wenn du den Branch zum ersten Mal hochlädst:
```bash
git push --set-upstream origin team/mein-team
```

---

## 4. Pull Request erstellen

Ein Pull Request ist eine Anfrage, deine Änderungen in einen anderen Branch zu übernehmen.
Verwende Pull Requests für:

- Änderungen an gemeinsamen Dateien (`main`-Branch)
- Abgeschlossene Aufgaben, die andere Teams betreffen

**So erstellst du einen Pull Request auf GitHub:**

1. Öffne das Repository auf github.com
2. Klicke auf den Tab **„Pull requests"**
3. Klicke auf **„New pull request"**
4. Wähle als **base** den Zielbranch (z. B. `main`)
5. Wähle als **compare** deinen Team-Branch
6. Gib einen Titel ein (z. B. `DP-01: NASA-Datenabruf implementiert`)
7. Fülle die Beschreibung aus (was wurde gemacht? Was müssen andere wissen?)
8. Klicke auf **„Create pull request"**

**Pull Request Beschreibung (Vorlage):**

```markdown
## Was wurde gemacht?
Kurze Beschreibung der Änderungen.

## Aufgabe
Bezug zu team_tasks.md: z. B. DP-01

## Betroffene andere Teams
Welche Teams müssen das wissen oder zustimmen?

## Tests
Welche Tests wurden hinzugefügt oder angepasst?

## Projektgedächtnis
Wurde project_memory.json aktualisiert? [ ] Ja / [ ] Nein / [ ] Nicht nötig
```

---

## 5. Code-Standards

### Python (Backend)

**Docstrings für alle Funktionen (auf Deutsch):**
```python
def compute_trend(dataset: list[dict]) -> dict:
    """
    Berechnet den linearen Trend eines Datensatzes.

    Args:
        dataset: Liste von Datenpunkten mit 'date' und 'value'.

    Returns:
        Dict mit 'trend_per_decade', 'r_squared' und 'p_value'.
    """
    ...
```

**Variablennamen auf Englisch, Kommentare auf Deutsch:**
```python
# Fehlende Werte entfernen, bevor der Trend berechnet wird
clean_data = [d for d in dataset if d["value"] is not None]
```

**Keine Magic Numbers – benannte Konstanten verwenden:**
```python
# Gut:
REFERENCE_START_YEAR = 1951
REFERENCE_END_YEAR = 1980

# Nicht gut:
if year >= 1951 and year <= 1980:
```

---

### JavaScript / React (Frontend)

**Funktionale Komponenten mit Props-Dokumentation:**
```jsx
/**
 * Zeigt eine Zeitreihe als Liniendiagramm.
 *
 * @param {Array} data - Array von { date, value } Objekten
 * @param {string} variable - Anzeigename der Variable (z. B. "Temperatur")
 * @param {string} unit - Einheit für die Y-Achse (z. B. "°C")
 * @param {string} source - Quellenangabe (wird unter dem Diagramm angezeigt)
 */
function TimeSeriesChart({ data, variable, unit, source }) {
  ...
}
```

**Keine inline Styles – Tailwind-Klassen verwenden:**
```jsx
// Gut:
<div className="bg-white p-4 rounded shadow">

// Nicht gut:
<div style={{ backgroundColor: 'white', padding: '16px' }}>
```

---

## 6. Tests schreiben und ausführen

### Backend-Tests (pytest)

**Tests ausführen:**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Einzelne Testdatei ausführen:**
```bash
pytest tests/test_climate_analysis.py -v
```

**Teststruktur (Beispiel):**
```python
# tests/test_climate_analysis.py

def test_trend_steigt_bei_wachsenden_werten():
    """Ein steigender Datensatz muss einen positiven Trend ergeben."""
    daten = [
        {"date": "2000-01-01", "value": 14.0},
        {"date": "2001-01-01", "value": 14.2},
        {"date": "2002-01-01", "value": 14.4},
    ]
    ergebnis = ClimateAnalysisModule().compute_trend(daten)
    assert ergebnis["trend_per_decade"] > 0

def test_fehlende_werte_werden_ignoriert():
    """Fehlende Werte (None) dürfen den Trend nicht verfälschen."""
    daten = [
        {"date": "2000-01-01", "value": 14.0},
        {"date": "2001-01-01", "value": None},
        {"date": "2002-01-01", "value": 14.4},
    ]
    ergebnis = ClimateAnalysisModule().compute_trend(daten)
    assert ergebnis is not None
```

### Frontend-Tests (Vitest)

**Tests ausführen:**
```bash
cd frontend
npm run test
```

**Teststruktur (Beispiel):**
```jsx
// tests/components/TimeSeriesChart.test.jsx
import { render, screen } from "@testing-library/react";
import TimeSeriesChart from "../../src/components/charts/TimeSeriesChart";

test("zeigt Quellenangabe an", () => {
  const daten = [{ date: "2000-01-01", value: 0.5 }];
  render(<TimeSeriesChart data={daten} variable="Temperatur"
                          unit="°C" source="NASA GISS" />);
  expect(screen.getByText(/NASA GISS/i)).toBeInTheDocument();
});

test("rendert ohne Fehler bei leeren Daten", () => {
  render(<TimeSeriesChart data={[]} variable="Temperatur"
                          unit="°C" source="NASA GISS" />);
  expect(screen.getByText(/keine daten/i)).toBeInTheDocument();
});
```

---

## 7. Projektgedächtnis aktualisieren

Nach jeder abgeschlossenen Aufgabe trägst du einen Eintrag in `memory/project_memory.json` ein.

**Format:**
```json
{
  "timestamp": "2025-01-15T14:30:00Z",
  "team": "Data Pipeline Team",
  "topic": "NASA-Client implementiert",
  "decision": "requests-Bibliothek mit 30 Sekunden Timeout verwendet",
  "reasoning": "Einfach zu verwenden, gut dokumentiert, zuverlässig",
  "impact": "Alle Datenquellen sollen dasselbe Timeout-Muster verwenden"
}
```

Den Eintrag fügst du in die Liste `architecture_decisions` ein und stellst ihn per Pull Request in `main`.

> 💡 Wann einen Eintrag erstellen?
> - Bei technischen Entscheidungen (Bibliothek, Datenformat, Algorithmus)
> - Bei API-Änderungen
> - Bei Erkenntnissen, die andere Teams betreffen
> - Bei neuen Datenquellen

---

## 8. Neue Datenquelle hinzufügen

1. **Lizenz prüfen** – Nur Public Domain oder CC BY verwenden
2. **Eintrag in `docs/data_sources.md`** nach dem vorhandenen Schema ergänzen
3. **Eintrag in `memory/project_memory.json`** unter `data_sources` hinzufügen
4. **Client-Klasse implementieren** in `backend/modules/data_ingestion/`
   - Dateiname: `<quelle>_client.py` (z. B. `copernicus_client.py`)
   - Output muss dem einheitlichen Dataset-Format entsprechen (siehe `docs/architecture.md`)
5. **Unit Test schreiben** in `backend/tests/test_data_ingestion.py`
6. **Pull Request** in `main` erstellen mit Hinweis auf neue Datenquelle

---

## 9. Neue Visualisierung hinzufügen

1. **Abstimmung mit UX Team** – Design-Vorgaben einhalten
2. **React-Komponente erstellen** in `frontend/src/components/charts/`
   - Props dokumentieren (JSDoc-Kommentar)
   - Quellenangabe einbauen (Pflicht)
   - Leere-Daten-Fall behandeln
3. **Backend-Datenvorbereitung** in `backend/modules/visualization/` (falls nötig)
4. **Vitest-Test schreiben** – mindestens: rendert ohne Fehler, Quellenangabe vorhanden
5. **Eintrag in `project_memory.json`** mit Beschreibung der Komponente
6. **Pull Request** erstellen

---

## 10. Häufige Fehler vermeiden

| Fehler | Lösung |
|---|---|
| Direkt in `main` committed | `git revert` + zukünftig immer Branch prüfen mit `git branch` |
| Commit-Nachricht zu ungenau | Format: `AUFGABEN-ID: Was wurde gemacht` |
| Virtuelle Umgebung vergessen | `source venv/bin/activate` vor jedem Backend-Start |
| API-Endpunkt geändert ohne Absprache | Änderungsvorschlag als Pull Request + Diskussion |
| Fehlende Quellenangabe in Diagramm | Jede Visualisierung muss `source`-Prop anzeigen |
| Artikel automatisch veröffentlicht | Status muss immer `"draft"` bleiben |
| `project_memory.json` nicht aktualisiert | Nach jeder Aufgabe: Eintrag erstellen + Pull Request |

---

*Letzte Aktualisierung: 2025-01-01 | Verantwortlich: Documentation Team*