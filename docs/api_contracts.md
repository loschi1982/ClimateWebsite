# API-Verträge – Klimaplattform
*Version: v1 | Basis-URL (lokal): `http://localhost:8000/api/v1`*
*Letzte Änderung: 2025-01-01 | Verantwortlich: Documentation Team*

---

## Allgemeine Regeln

- Alle Endpunkte beginnen mit `/api/v1/`
- Antworten sind immer JSON
- Datumsformat: ISO 8601 (`YYYY-MM-DD` oder `YYYY-MM-DDTHH:MM:SSZ`)
- Fehlercodes folgen dem HTTP-Standard (siehe unten)
- Jede Antwort enthält ein `"version"` Feld mit dem API-Versionsnamen

## Interaktive API-Dokumentation (lokal)
Wenn der Backend-Server läuft, ist die vollständige API-Dokumentation erreichbar unter:
- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

---

## Allgemeine Fehlercodes

| Code | Bedeutung | Wann? |
|---|---|---|
| `400` | Bad Request | Ungültige Parameter |
| `404` | Not Found | Datensatz oder Ressource nicht gefunden |
| `422` | Unprocessable Entity | Fehlende Pflichtparameter |
| `500` | Internal Server Error | Unerwarteter Fehler im Backend |
| `503` | Service Unavailable | Externe Datenquelle nicht erreichbar |

Fehlerantwort-Format (immer gleich):
```json
{
  "error": {
    "code": 404,
    "message": "Datensatz nicht gefunden",
    "detail": "Quelle 'nasa', Variable 'temperature' für den Zeitraum 2030–2050 nicht verfügbar"
  }
}
```

---

## 1. Daten-Endpunkte

### GET /api/v1/data

Gibt einen Klimadatensatz zurück.

**Parameter (Query-String):**

| Parameter | Typ | Pflicht | Beschreibung | Beispiel |
|---|---|---|---|---|
| `source` | string | ✅ | Datenquelle | `nasa`, `noaa`, `nsidc` |
| `variable` | string | ✅ | Klimavariable | `temperature`, `co2`, `sea_ice` |
| `start` | string | ✅ | Startdatum (ISO) | `1980-01-01` |
| `end` | string | ✅ | Enddatum (ISO) | `2024-12-31` |

**Beispiel-Aufruf:**
```
GET /api/v1/data?source=nasa&variable=temperature&start=1980-01-01&end=2024-12-31
```

**Antwort (200):**
```json
{
  "version": "v1",
  "source": "nasa",
  "variable": "temperature",
  "unit": "°C",
  "reference_period": "1951-1980",
  "data": [
    { "date": "1980-01-01", "value": 0.24 },
    { "date": "1980-02-01", "value": 0.31 }
  ],
  "metadata": {
    "source_name": "NASA GISS Surface Temperature Analysis (GISTEMP v4)",
    "source_url": "https://data.giss.nasa.gov/gistemp/",
    "retrieved_at": "2025-01-01T10:00:00Z",
    "license": "Public Domain"
  }
}
```

**Fehlerfälle:**
- `400` – Ungültige Quelle oder Variable
- `404` – Keine Daten für den Zeitraum vorhanden
- `503` – Externe Quelle nicht erreichbar

---

### GET /api/v1/data/sources

Gibt alle verfügbaren Datenquellen und Variablen zurück.

**Antwort (200):**
```json
{
  "version": "v1",
  "sources": [
    {
      "id": "nasa",
      "name": "NASA GISS",
      "variables": ["temperature"],
      "available_from": "1880-01-01",
      "update_frequency": "monthly"
    },
    {
      "id": "noaa",
      "name": "NOAA GML",
      "variables": ["co2"],
      "available_from": "1958-03-01",
      "update_frequency": "monthly"
    },
    {
      "id": "nsidc",
      "name": "NSIDC Sea Ice Index",
      "variables": ["sea_ice_arctic", "sea_ice_antarctic"],
      "available_from": "1979-01-01",
      "update_frequency": "monthly"
    }
  ]
}
```

---

## 2. Analyse-Endpunkte

### GET /api/v1/analysis/trend

Berechnet den linearen Trend eines Datensatzes.

**Parameter (Query-String):**

| Parameter | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `source` | string | ✅ | Datenquelle |
| `variable` | string | ✅ | Klimavariable |
| `start` | string | ✅ | Startdatum |
| `end` | string | ✅ | Enddatum |

**Beispiel-Aufruf:**
```
GET /api/v1/analysis/trend?source=nasa&variable=temperature&start=1980-01-01&end=2024-12-31
```

**Antwort (200):**
```json
{
  "version": "v1",
  "source": "nasa",
  "variable": "temperature",
  "unit": "°C",
  "trend_per_decade": 0.18,
  "trend_unit": "°C/Jahrzehnt",
  "r_squared": 0.94,
  "p_value": 0.001,
  "period": {
    "start": "1980-01-01",
    "end": "2024-12-31"
  },
  "interpretation": "Statistisch signifikanter positiver Trend"
}
```

---

### GET /api/v1/analysis/correlation

Berechnet die Korrelation zwischen zwei Klimavariablen.

**Parameter (Query-String):**

| Parameter | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `source_a` | string | ✅ | Quelle Variable A |
| `variable_a` | string | ✅ | Variable A |
| `source_b` | string | ✅ | Quelle Variable B |
| `variable_b` | string | ✅ | Variable B |
| `start` | string | ✅ | Startdatum |
| `end` | string | ✅ | Enddatum |

**Beispiel-Aufruf:**
```
GET /api/v1/analysis/correlation?source_a=noaa&variable_a=co2&source_b=nasa&variable_b=temperature&start=1980-01-01&end=2024-12-31
```

**Antwort (200):**
```json
{
  "version": "v1",
  "variable_a": "co2",
  "variable_b": "temperature",
  "correlation": 0.97,
  "method": "pearson",
  "p_value": 0.001,
  "period": {
    "start": "1980-01-01",
    "end": "2024-12-31"
  },
  "note": "Korrelation bedeutet keine Kausalität. Weitere Analyse notwendig."
}
```

---

### GET /api/v1/analysis/anomalies

Berechnet Anomalien gegenüber einem Referenzzeitraum.

**Parameter (Query-String):**

| Parameter | Typ | Pflicht | Standard | Beschreibung |
|---|---|---|---|---|
| `source` | string | ✅ | – | Datenquelle |
| `variable` | string | ✅ | – | Klimavariable |
| `start` | string | ✅ | – | Startdatum Analyse |
| `end` | string | ✅ | – | Enddatum Analyse |
| `ref_start` | string | ❌ | `1951-01-01` | Referenzzeitraum Start |
| `ref_end` | string | ❌ | `1980-12-31` | Referenzzeitraum Ende |

**Antwort (200):**
```json
{
  "version": "v1",
  "variable": "temperature",
  "reference_period": {
    "start": "1951-01-01",
    "end": "1980-12-31"
  },
  "anomalies": [
    { "date": "2023-07-01", "value": 1.17, "anomaly": 1.17 },
    { "date": "2023-08-01", "value": 1.24, "anomaly": 1.24 }
  ]
}
```

---

## 3. Simulations-Endpunkte

### POST /api/v1/simulation/run

Führt eine didaktische Klimasimulation aus.

**Request Body (JSON):**
```json
{
  "scenario": "temperature_rcp",
  "parameters": {
    "rcp_path": "rcp45",
    "years": 50
  }
}
```

**Verfügbare Szenarien:**

| `scenario` | Beschreibung | Parameter |
|---|---|---|
| `temperature_rcp` | Temperaturentwicklung nach RCP-Pfad | `rcp_path`: `rcp26`, `rcp45`, `rcp85`; `years`: 1–100 |
| `co2_emission` | CO₂-Konzentration nach Emissionspfad | `emission_rate`: Zahl in ppm/Jahr; `years`: 1–100 |
| `sea_ice_decline` | Meereisveränderung bei Temperaturdelta | `temp_delta`: Zahl in °C |

**Antwort (200):**
```json
{
  "version": "v1",
  "scenario": "temperature_rcp",
  "parameters": {
    "rcp_path": "rcp45",
    "years": 50
  },
  "data": [
    { "year": 2025, "value": 0.0 },
    { "year": 2050, "value": 0.9 },
    { "year": 2075, "value": 1.8 }
  ],
  "unit": "°C (Anomalie gegenüber 2025)",
  "disclaimer": "Dies ist eine stark vereinfachte didaktische Simulation. Sie ersetzt keine wissenschaftliche Klimamodellierung.",
  "explanation": "Bei RCP 4.5 stabilisieren sich die Emissionen bis ca. 2050. Die Erwärmung setzt sich danach verlangsamt fort."
}
```

**Fehlerfälle:**
- `400` – Unbekanntes Szenario oder ungültige Parameter
- `422` – Pflichtparameter fehlen

---

### GET /api/v1/simulation/scenarios

Gibt alle verfügbaren Szenarien zurück.

**Antwort (200):**
```json
{
  "version": "v1",
  "scenarios": [
    {
      "id": "temperature_rcp",
      "name": "Temperaturentwicklung (RCP-Pfade)",
      "description": "Zeigt, wie sich die globale Temperatur bei verschiedenen Emissionsszenarien entwickelt.",
      "parameters": [
        { "name": "rcp_path", "type": "string", "options": ["rcp26", "rcp45", "rcp85"] },
        { "name": "years", "type": "integer", "min": 1, "max": 100 }
      ]
    }
  ]
}
```

---

## 4. Artikel-Endpunkte

### GET /api/v1/articles

Gibt alle Artikelentwürfe zurück (nur status: "draft" oder "approved").

**Parameter (Query-String):**

| Parameter | Typ | Pflicht | Standard | Beschreibung |
|---|---|---|---|---|
| `status` | string | ❌ | `approved` | `draft` oder `approved` |
| `limit` | integer | ❌ | `10` | Max. Anzahl Ergebnisse |
| `offset` | integer | ❌ | `0` | Für Paginierung |

**Antwort (200):**
```json
{
  "version": "v1",
  "total": 3,
  "articles": [
    {
      "id": "art_001",
      "title": "Temperaturanstieg in Europa 1980–2024",
      "summary": "Die Analyse zeigt einen Anstieg von 0.18°C pro Jahrzehnt...",
      "status": "draft",
      "created_at": "2025-01-15T08:00:00Z",
      "based_on_analysis": "ana_042",
      "review_required": true
    }
  ]
}
```

---

### GET /api/v1/articles/{id}

Gibt einen einzelnen Artikel zurück.

**Antwort (200):**
```json
{
  "version": "v1",
  "id": "art_001",
  "title": "Temperaturanstieg in Europa 1980–2024",
  "content_markdown": "## Einleitung\n\nDie globale Durchschnittstemperatur...",
  "status": "draft",
  "created_at": "2025-01-15T08:00:00Z",
  "based_on_analysis": "ana_042",
  "sources": [
    { "name": "NASA GISS", "url": "https://data.giss.nasa.gov/gistemp/" }
  ],
  "language": "de",
  "review_required": true
}
```

**Fehlerfälle:**
- `404` – Artikel nicht gefunden

---

### POST /api/v1/articles/generate

Startet die KI-Generierung eines Artikelentwurfs.

**Request Body (JSON):**
```json
{
  "analysis_id": "ana_042",
  "language": "de"
}
```

**Antwort (202 – Accepted):**
```json
{
  "version": "v1",
  "job_id": "job_007",
  "status": "processing",
  "estimated_seconds": 15,
  "message": "Artikelentwurf wird generiert. Status abrufbar unter /api/v1/articles/jobs/job_007"
}
```

---

### GET /api/v1/articles/jobs/{job_id}

Prüft den Status eines laufenden Generierungsauftrags.

**Antwort (200):**
```json
{
  "version": "v1",
  "job_id": "job_007",
  "status": "completed",
  "article_id": "art_002"
}
```

`status` kann sein: `processing`, `completed`, `failed`

---

## Änderungshistorie

| Version | Datum | Team | Änderung |
|---|---|---|---|
| v1.0 | 2025-01-01 | Architect | Initiale API-Verträge definiert |

---

## Regeln für API-Änderungen

1. API-Änderungen dürfen NICHT eigenständig von einzelnen Teams vorgenommen werden
2. Änderungsvorschlag als Pull Request mit Begründung
3. Eintrag in `memory/project_memory.json` (impact-Feld ausfüllen)
4. Alle betroffenen Teams müssen zustimmen
5. Breaking Changes erhöhen die Versionsnummer (`v2`)