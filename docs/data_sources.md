# Datenquellen – Klimaplattform
*Letzte Aktualisierung: 2025-01-01 | Verantwortlich: Documentation Team*

Alle auf der Klimaplattform verwendeten Daten stammen aus öffentlichen,
wissenschaftlichen Quellen. Jede Datenquelle ist hier mit Lizenz,
Nutzungsbedingungen und technischer Integration dokumentiert.

---

## Übersicht

| ID | Quelle | Variable | Lizenz | Phase |
|---|---|---|---|---|
| src_001 | NASA GISS | Globale Temperaturanomalie | Public Domain | 1 |
| src_002 | NOAA GML | CO₂-Konzentration (Mauna Loa) | Public Domain | 1 |
| src_003 | NSIDC | Meereisausdehnung (Arktis + Antarktis) | Public Domain | 1 |
| src_004 | Copernicus C3S | Europäische Klimavariablen | CC BY 4.0 | 2 |
| src_005 | IPCC | Emissionsszenarien (RCP/SSP) | CC BY 4.0 | 2 |

---

## src_001 – NASA GISS Surface Temperature Analysis (GISTEMP v4)

**Betreiber:** NASA Goddard Institute for Space Studies  
**Website:** https://data.giss.nasa.gov/gistemp/  
**Lizenz:** Public Domain (keine Einschränkungen)  
**Zitierung:** GISTEMP Team, 2024: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies.

### Was sind das für Daten?
Die NASA GISS-Daten zeigen, wie stark die globale Durchschnittstemperatur
von einem Referenzzeitraum (1951–1980) abweicht.
Ein Wert von +1.0 bedeutet: Es war 1,0 °C wärmer als im Durchschnitt von 1951–1980.

### Technische Details
- **URL:** `https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv`
- **Format:** CSV
- **Zeitraum:** ab Januar 1880
- **Auflösung:** monatlich
- **Einheit:** °C (Anomalie gegenüber 1951–1980)
- **Aktualisierung:** monatlich (ca. 2 Wochen nach Monatsende)

### Datenstruktur (Rohdatei)
```
Year,Jan,Feb,Mar,...,Dec,J-D,D-N,DJF,MAM,JJA,SON
1880,-.16,-.13,-.12,...
```
Die Spalte `J-D` enthält den Jahresmittelwert. Fehlende Werte sind mit `***` gekennzeichnet.

### Integration (Python-Beispiel)
```python
import pandas as pd

URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
df = pd.read_csv(URL, skiprows=1, na_values="***")
# Jahresspalten in Monatsspalten umwandeln (long format)
```

---

## src_002 – NOAA GML Mauna Loa CO₂-Messungen

**Betreiber:** NOAA Global Monitoring Laboratory  
**Website:** https://gml.noaa.gov/ccgg/trends/  
**Lizenz:** Public Domain  
**Zitierung:** Dr. Pieter Tans, NOAA/GML und Dr. Ralph Keeling, Scripps Institution of Oceanography

### Was sind das für Daten?
Die Mauna-Loa-Messungen sind die älteste kontinuierliche CO₂-Messreihe der Welt.
Sie begann 1958 und gilt als weltweiter Referenzstandard für atmosphärisches CO₂.
Die Einheit ppm (parts per million) gibt an, wie viele CO₂-Moleküle pro Million Luftmoleküle vorhanden sind.

### Technische Details
- **URL:** `https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv`
- **Format:** CSV (mit Kommentarzeilen beginnend mit `#`)
- **Zeitraum:** ab März 1958
- **Auflösung:** monatlich
- **Einheit:** ppm (parts per million)
- **Aktualisierung:** monatlich

### Datenstruktur (Rohdatei)
```
# year, month, decimal_date, monthly_avg, deseasonalized, ndays, sdev, unc
1958,3,1958.208,-99.99,314.44,-1,0.00,0.00
```
Fehlende Werte: `-99.99`

### Integration (Python-Beispiel)
```python
import pandas as pd

URL = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.csv"
df = pd.read_csv(URL, comment="#",
                 names=["year","month","decimal_date","co2_avg",
                        "deseasonalized","ndays","sdev","unc"])
df = df[df["co2_avg"] > 0]  # Fehlwerte entfernen
```

---

## src_003 – NSIDC Sea Ice Index

**Betreiber:** National Snow and Ice Data Center (NSIDC), University of Colorado  
**Website:** https://nsidc.org/data/seaice_index/  
**Lizenz:** Public Domain  
**Zitierung:** Fetterer, F., K. Knowles, W. N. Meier, M. Savoie, and A. K. Windnagel. 2017, updated daily. Sea Ice Index, Version 3. NSIDC.

### Was sind das für Daten?
Der Sea Ice Index zeigt die monatliche Ausdehnung des Meereises in der Arktis und Antarktis.
Gemessen wird die Fläche in Millionen Quadratkilometern, die zu mindestens 15 % mit Eis bedeckt ist.

### Technische Details
- **Arktis-URL:** `https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/N_seaice_extent_monthly_v3.0.csv`
- **Antarktis-URL:** `https://noaadata.apps.nsidc.org/NOAA/G02135/south/monthly/data/S_seaice_extent_monthly_v3.0.csv`
- **Format:** CSV
- **Zeitraum:** ab Oktober 1978 (Arktis), ab November 1978 (Antarktis)
- **Auflösung:** monatlich
- **Einheit:** Millionen km²
- **Aktualisierung:** monatlich

### Datenstruktur (Rohdatei)
```
Year, Mo, data-type, region, extent, area
1978, 10, Goddard, N, 10.60, 9.21
```

### Integration (Python-Beispiel)
```python
import pandas as pd

URL = "https://noaadata.apps.nsidc.org/NOAA/G02135/north/monthly/data/N_seaice_extent_monthly_v3.0.csv"
df = pd.read_csv(URL, skiprows=0)
df.columns = df.columns.str.strip()  # Leerzeichen in Spaltennamen entfernen
```

---

## src_004 – Copernicus Climate Change Service (C3S)

**Betreiber:** Europäisches Zentrum für mittelfristige Wettervorhersage (ECMWF)  
**Website:** https://climate.copernicus.eu/  
**Lizenz:** Creative Commons Attribution 4.0 International (CC BY 4.0)  
**Zitierung:** Copernicus Climate Change Service (C3S), Climate Data Store (CDS)

### Was sind das für Daten?
Copernicus bietet ein breites Spektrum europäischer und globaler Klimadaten,
darunter Temperatur, Niederschlag, Meeresspiegel und Extremwetterereignisse.

### Zugang (API-Registrierung erforderlich)
1. Konto erstellen auf: https://cds.climate.copernicus.eu/
2. API-Key in `.env` eintragen: `COPERNICUS_API_KEY=dein-key`
3. Python-Bibliothek installieren: `pip install cdsapi`

### Integration (Python-Beispiel)
```python
import cdsapi

client = cdsapi.Client()
client.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "monthly_averaged_reanalysis",
        "variable": "2m_temperature",
        "year": ["2020", "2021"],
        "month": ["01", "02"],
        "format": "netcdf"
    },
    "output.nc"
)
```

> ⚠️ Copernicus-Daten erfordern eine Registrierung. Die Integration ist für Phase 2 geplant.

---

## src_005 – IPCC Emissionsszenarien (RCP / SSP)

**Betreiber:** Intergovernmental Panel on Climate Change (IPCC)  
**Website:** https://www.ipcc.ch/data/  
**Lizenz:** Creative Commons Attribution 4.0 (CC BY 4.0)  
**Verwendung:** Grundlage für didaktische Simulationen (nicht als Rohdaten-Feed)

### Was sind das für Daten?
Das IPCC definiert Emissionsszenarien, die beschreiben, wie sich CO₂-Emissionen
in Zukunft entwickeln könnten. Diese werden in unseren Simulationen als Grundlage verwendet.

| Szenario | Beschreibung |
|---|---|
| RCP 2.6 | Starke Reduktion der Emissionen, Erwärmung unter 2°C |
| RCP 4.5 | Moderate Reduktion, Stabilisierung bis 2100 |
| RCP 8.5 | Keine Reduktion, starke Erwärmung |
| SSP1-2.6 | Neuere Entsprechung zu RCP 2.6 |
| SSP5-8.5 | Neuere Entsprechung zu RCP 8.5 |

> 💡 RCP-Werte werden in unseren Simulationen als vereinfachte Modellparameter verwendet.
> Die Simulationen sind didaktisch – sie ersetzen keine wissenschaftliche Klimamodellierung.

---

## Regeln für alle Datenquellen

1. **Quellenangabe:** Jeder Datensatz muss auf der Plattform mit Name und URL der Quelle angezeigt werden.
2. **Lizenzprüfung:** Vor der Integration einer neuen Quelle muss die Lizenz geprüft werden.
3. **Keine Manipulation:** Rohdaten dürfen nur normalisiert, nicht inhaltlich verändert werden.
4. **Transparenz:** Alle Verarbeitungsschritte (Normalisierung, Filterung) müssen dokumentiert sein.
5. **Aktualität:** Jeder Datensatz muss das Abrufdatum (`retrieved_at`) speichern.

---

## Neue Datenquelle hinzufügen

Um eine neue Datenquelle zu integrieren, folge diesen Schritten:

1. Lizenz prüfen (Public Domain oder CC BY bevorzugt)
2. Eintrag in dieser Datei ergänzen (nach dem Schema oben)
3. Eintrag in `memory/project_memory.json` unter `data_sources` hinzufügen
4. Client-Klasse in `backend/modules/data_ingestion/` implementieren
5. Unit Test in `backend/tests/test_data_ingestion.py` schreiben
6. Pull Request in `main` erstellen

---

*Letzte Aktualisierung: 2025-01-01 | Verantwortlich: Documentation Team*