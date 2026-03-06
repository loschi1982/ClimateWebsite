# ClimateInsight — Projektbeschreibung
## Version 1.0 | Pflichtlektüre für alle Teams

---

## Was ist ClimateInsight?

ClimateInsight ist eine Open-Source-Webplattform zur wissenschaftlichen
Aufklärung über Klimaveränderungen. Sie richtet sich an interessierte
Bürger, Schüler, Studierende und Fachleute gleichermaßen.

Die Plattform macht echte wissenschaftliche Klimadaten zugänglich,
verständlich und interaktiv erlebbar — ohne dabei wissenschaftliche
Korrektheit zu opfern.

---

## Ziele der Plattform

- Wissenschaftliche Klimadaten integrieren und aktuell halten
- Historische und aktuelle Messdaten analysieren
- Zusammenhänge zwischen Klimafaktoren erklären
- Daten anschaulich visualisieren
- Interaktive Exploration ermöglichen
- Verständliche Artikel generieren und veröffentlichen

---

## Inhaltliche Themen

Die Plattform behandelt folgende Themenbereiche:

| Thema | Beschreibung |
|-------|--------------|
| Temperaturentwicklung | Globale und regionale Temperaturveränderungen seit 1880 |
| Treibhausgase | CO₂, Methan, Lachgas — Konzentration und Quellen |
| Meeresspiegel | Anstieg, Ursachen, regionale Unterschiede |
| Eisbedeckung der Pole | Arktis, Antarktis, Gletscher |
| Meeresströmungen | Thermohaline Zirkulation, Veränderungen |
| Extremwetterereignisse | Häufigkeit, Intensität, Trends |
| Biodiversität | Auswirkungen des Klimawandels auf Tier- und Pflanzenwelt |

Weitere Themen können jederzeit ergänzt werden.

---

## Datenquellen

Alle Daten stammen aus wissenschaftlich anerkannten Quellen:

| Quelle | Beschreibung |
|--------|--------------|
| NASA GISS | Globale Oberflächentemperatur (GISTEMP v4) |
| NOAA | CO₂-Messungen (Mauna Loa), Ozean- und Atmosphärendaten |
| Copernicus C3S | Europäischer Klimadatendienst |
| IPCC | Klimaszenarien und Projektionen (AR6) |
| NSIDC | Meeres- und Gletschereis-Daten |

**Pflichtregeln für alle Daten:**
- Vollständige Quellenangabe (Zitation + DOI wenn verfügbar)
- Abrufdatum dokumentieren
- Lizenz prüfen und dokumentieren
- Rohdaten unveränderlich speichern

---

## Systemfunktionen

Das System bietet folgende Funktionen:

**Automatisiert:**
- Regelmäßiger Datenabruf von allen Quellen
- Zeitreihenanalyse und Trenderkennung
- Hypothesengenerierung aus Analyseergebnissen
- Artikelentwürfe erstellen (immer mit menschlicher Prüfung)

**Interaktiv für Nutzer:**
- Datensätze auswählen und vergleichen
- Zeiträume frei wählen
- Korrelationen zwischen Variablen entdecken
- Klimaszenarien simulieren
- Visualisierungen exportieren

---

## Interaktive Explorationsseiten

Die Kernfunktion der Plattform sind Explorationsseiten unter `/explore`.

Nutzer können dort:
- Verschiedene Klimavariablen auswählen
- Mehrere Variablen gleichzeitig vergleichen
- Trends über beliebige Zeiträume berechnen lassen
- Korrelationen zwischen Variablen visualisieren
- Eigene Szenarien mit Parameterschiebereglern simulieren
- Ansichten als Link teilen

Das Ziel: Nutzer entdecken Zusammenhänge selbst, anstatt sie
nur erklärt zu bekommen.

---

## Visualisierung

Die Plattform unterstützt:

- **Zeitreihendiagramme** — Entwicklung über Zeit
- **Korrelationsdiagramme** — Beziehungen zwischen Variablen
- **Kartenvisualisierungen** — Räumliche Verteilung
- **Trendanalysen** — Mit Konfidenzintervallen
- **Didaktische Simulationen** — Vereinfachte Klimamodelle

Jede Visualisierung enthält die Quellenangabe und ist exportierbar
(SVG, PNG, CSV).

---

## Design-Prinzipien

Die Plattform wirkt:
- **Wissenschaftlich** — nicht reißerisch oder alarmistisch
- **Freundlich** — einladend, nicht abschreckend
- **Aufgeräumt** — keine Informationsüberladung

Konkrete Design-Regeln:
- Ruhige Farbpalette (kein grelles Rot/Grün)
- Klare Typografie, großzügige Abstände
- Hohe Lesbarkeit (WCAG 2.1 AA)
- Intuitive Bedienung ohne Einführung

---

## Redaktioneller Prozess

**KI-generierte Inhalte werden niemals automatisch veröffentlicht.**

Jeder Artikel durchläuft diesen Prozess:

```
KI generiert Entwurf
        ↓
  status: pending_review
        ↓
  Menschliche Prüfung
  (wissenschaftliche Korrektheit,
   Quellenangaben, Sprache)
        ↓
  Entscheidung: approved / rejected / revision_required
        ↓
  Veröffentlichung (nur bei approved)
```

Diese Regel gilt absolut und ist nicht verhandelbar.

---

## Technische Grundsätze

- **Modular** — alle Komponenten sind austauschbar
- **Open Source** — MIT-Lizenz, Community-Beiträge willkommen
- **Reproduzierbar** — alle Analysen nachvollziehbar dokumentiert
- **Transparent** — Unsicherheiten werden immer kommuniziert
- **Barrierefrei** — WCAG 2.1 AA Standard

---

## Repository

GitHub: **loschi1982/ClimateWebsite**
Lizenz: MIT
Sprache (Code): Englisch
Sprache (Inhalte): Deutsch und Englisch

---

*Stand: 2026-03-05 | Alle Teams lesen dieses Dokument zu Beginn jeder Session.*
