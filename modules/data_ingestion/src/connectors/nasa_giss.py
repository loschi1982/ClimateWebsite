# ─────────────────────────────────────────────────────────────────────────────
# Was macht diese Datei?
# Implementiert den Connector zur NASA GISS Datenbank.
# Der Connector lädt die GISTEMP v4 Daten (globale Temperaturabweichungen
# seit 1880) herunter, validiert sie und normalisiert sie in unser
# einheitliches DataPoint-Format.
#
# Was ist GISTEMP?
# GISTEMP (GISS Surface Temperature Analysis) ist ein Datensatz der NASA,
# der die Veränderung der globalen Oberflächentemperatur seit 1880 misst.
# Die Daten zeigen, um wieviel °C die Temperatur vom Durchschnitt
# des Referenzzeitraums 1951–1980 abweicht ("Anomalie").
#
# Team: Data Pipeline Team | Branch: feature/data-pipeline
# ─────────────────────────────────────────────────────────────────────────────

# logging: Ermöglicht es, Meldungen in eine Log-Datei zu schreiben,
# statt nur print() zu verwenden. Logs lassen sich später durchsuchen.
import logging

# io: Ermöglicht das Lesen von Text-Daten direkt aus dem Speicher,
# ohne sie zuerst auf die Festplatte schreiben zu müssen.
import io

# csv: Verarbeitet CSV-Dateien (Comma-Separated Values = kommagetrennte Werte)
# CSV ist ein verbreitetes Datenformat: jede Zeile = ein Datensatz.
import csv

# datetime, timezone: Arbeit mit Datum/Uhrzeit + Zeitzonen
from datetime import datetime, timezone

# List, Optional: Typangaben damit Python-Tools und Entwickler
# sofort sehen, welche Typen Funktionen erwarten und zurückgeben.
from typing import List, Optional

# requests: Ermöglicht HTTP-Anfragen an externe Server.
# Wie ein Browser, der eine Webseite aufruft — nur ohne grafische Oberfläche.
import requests

# Unsere eigenen Datenmodelle importieren (aus Aufgabe 1.2)
from models.climate_dataset import (
    DataPoint,
    ClimateDataset,
    SourceReference,
    IngestionJob,
)


# ─────────────────────────────────────────────────────────────────────────────
# Logger einrichten
# Ein Logger schreibt Statusmeldungen ("Verbindung aufgebaut",
# "Fehler beim Parsen") in eine Protokolldatei. Das ist nützlicher
# als print(), weil man Zeitstempel, Fehlerdetails und Log-Level
# (DEBUG, INFO, WARNING, ERROR) bekommt.
# ─────────────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Konstanten
# Konstanten sind Werte, die sich nie ändern. Wir definieren sie einmal
# oben in der Datei, damit sie leicht gefunden und geändert werden können.
# ─────────────────────────────────────────────────────────────────────────────

# Basis-URL der NASA GISTEMP API
# Diese URL gibt uns eine CSV-Datei mit globalen Jahresmittelwerten zurück.
# Erklärung der Parameter:
#   dt=1 → Jahresmittelwerte (nicht monatlich)
#   df=1 → Als CSV-Datei herunterladen
NASA_GISTEMP_URL = (
    "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
)

# DOI des GISTEMP v4 Datensatzes
# Ein DOI ist ein permanenter Link zu einer wissenschaftlichen Publikation.
# Dieser DOI verweist auf das offizielle NASA-Dokument zu GISTEMP v4.
NASA_GISTEMP_DOI = "10.7289/V5T72FNM"

# Timeout in Sekunden: Wie lange warten wir maximal auf eine Antwort?
# 30 Sekunden sind ein vernünftiger Wert für externe APIs.
REQUEST_TIMEOUT_SECONDS = 30

# Referenzwert für fehlende Daten in NASA GISTEMP CSV
# NASA verwendet "***" als Platzhalter für fehlende Messwerte.
NASA_MISSING_VALUE_MARKER = "***"


class NasaGissConnector:
    """
    Connector zur NASA GISS Surface Temperature Analysis (GISTEMP v4).

    Was macht dieser Connector?
    Er lädt die offiziellen globalen Temperaturanomaliedaten der NASA herunter,
    überprüft deren Integrität und überführt sie in unser einheitliches
    ClimateDataset-Format, das alle Teams im Projekt verwenden.

    Warum "Anomalie" statt Absoluttemperatur?
    Temperaturanomalien (Abweichungen vom Mittelwert) sind wissenschaftlich
    robuster als Absolutwerte, weil sie unabhängig von der genauen Lage
    der Messstationen sind. Eine Station auf einem Berg und eine im Tal
    messen unterschiedliche Temperaturen — aber ihre Trends (Abweichungen)
    sind vergleichbar.

    Wissenschaftliche Quelle:
    Lenssen, N. et al. (2019): Improvements in the GISTEMP Uncertainty Model.
    Journal of Geophysical Research: Atmospheres, 124(12), 6307–6326.
    DOI: 10.1029/2018JD029522
    """

    def __init__(self, timeout: int = REQUEST_TIMEOUT_SECONDS):
        """
        Initialisiert den Connector.

        Was passiert hier?
        Wir speichern den Timeout-Wert und erstellen die SourceReference —
        die vollständige Quellenangabe, die jedem Datensatz beigefügt wird.

        Args:
            timeout: Maximale Wartezeit für HTTP-Anfragen in Sekunden.
        """
        # Timeout speichern
        self.timeout = timeout

        # SourceReference erstellen: vollständige Quellenangabe für alle
        # Datensätze, die dieser Connector produziert.
        self.source_reference = SourceReference(
            provider="NASA Goddard Institute for Space Studies (GISS)",
            dataset_name="GISS Surface Temperature Analysis v4 (GISTEMP v4)",
            citation=(
                "GISTEMP Team (2024): GISS Surface Temperature Analysis (GISTEMP), "
                "version 4. NASA Goddard Institute for Space Studies. "
                f"DOI: {NASA_GISTEMP_DOI}"
            ),
            doi=NASA_GISTEMP_DOI,
            url=NASA_GISTEMP_URL,
            license="Public Domain",
            accessed_at=datetime.now(timezone.utc),
        )

        logger.info("NasaGissConnector initialisiert (timeout=%ds)", timeout)

    # ─────────────────────────────────────────────────────────────────────────
    # Öffentliche Methode: fetch_dataset
    # Das ist die Hauptmethode, die andere Teams aufrufen.
    # ─────────────────────────────────────────────────────────────────────────
    def fetch_dataset(
        self,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> ClimateDataset:
        """
        Lädt den kompletten GISTEMP v4 Datensatz und gibt ihn zurück.

        Was passiert hier Schritt für Schritt:
        1. Rohdaten von der NASA-URL herunterladen (HTTP GET)
        2. CSV-Text parsen (Zeilen lesen, Werte extrahieren)
        3. Jede Zeile in einen DataPoint umwandeln (normalisieren)
        4. Optional: Datenpunkte auf einen Zeitraum einschränken
        5. Alles in ein ClimateDataset verpacken und zurückgeben

        Args:
            start_year: Optional. Nur Daten ab diesem Jahr laden (z.B. 1960).
            end_year:   Optional. Nur Daten bis zu diesem Jahr laden (z.B. 2025).

        Returns:
            ClimateDataset mit allen Anomalie-Messpunkten.

        Raises:
            ConnectionError: Wenn die NASA-URL nicht erreichbar ist.
            ValueError: Wenn die CSV-Daten nicht geparst werden können.
            RuntimeError: Bei unerwarteten Fehlern.
        """
        logger.info(
            "Starte GISTEMP v4 Abruf (start_year=%s, end_year=%s)",
            start_year, end_year,
        )

        # Schritt 1: Rohdaten herunterladen
        raw_csv = self._download_raw_data()

        # Schritt 2 & 3: CSV parsen und in DataPoints umwandeln
        data_points = self._parse_and_normalize(raw_csv)

        # Schritt 4: Zeitraum einschränken (falls Parameter angegeben)
        if start_year is not None:
            data_points = [
                dp for dp in data_points
                if dp.timestamp.year >= start_year
            ]
        if end_year is not None:
            data_points = [
                dp for dp in data_points
                if dp.timestamp.year <= end_year
            ]

        logger.info(
            "GISTEMP v4 Abruf abgeschlossen: %d Datenpunkte", len(data_points)
        )

        # Schritt 5: ClimateDataset zusammenbauen und zurückgeben
        # Wir ermitteln den tatsächlichen Zeitraum der Daten
        timestamps = [dp.timestamp for dp in data_points]
        return ClimateDataset(
            dataset_id="nasa_giss_surface_temp_v4",
            variable="surface_temperature_anomaly",
            description=(
                "Globale Oberflächentemperaturabweichung (Anomalie) gegenüber "
                "dem Referenzzeitraum 1951–1980, in °C. "
                "Jahresmittelwerte ab 1880. Quelle: NASA GISS GISTEMP v4."
            ),
            source=self.source_reference,
            records=data_points,
            temporal_coverage_start=min(timestamps) if timestamps else None,
            temporal_coverage_end=max(timestamps) if timestamps else None,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Private Methode: _download_raw_data
    # Lädt die CSV-Rohdaten von der NASA-URL herunter.
    # "Privat" (erkennbar am Unterstrich _) bedeutet: nur intern verwenden.
    # ─────────────────────────────────────────────────────────────────────────
    def _download_raw_data(self) -> str:
        """
        Führt den HTTP-GET-Request zur NASA-URL aus und gibt den CSV-Text zurück.

        Was ist ein HTTP-GET-Request?
        HTTP ist das Protokoll, das Browser und Server für die Kommunikation
        nutzen. Ein GET-Request bedeutet: "Bitte schick mir diese Ressource."
        Das ist dasselbe, was passiert, wenn du eine URL im Browser öffnest.

        Returns:
            Roher CSV-Text als String.

        Raises:
            ConnectionError: Wenn Server nicht erreichbar oder Timeout.
            ValueError: Wenn HTTP-Fehler (z.B. 404 Not Found).
        """
        logger.debug("HTTP GET → %s", NASA_GISTEMP_URL)

        try:
            # HTTP-Anfrage senden
            # timeout=self.timeout → Abbrechen nach X Sekunden, damit das
            # Programm nicht ewig wartet, wenn der Server nicht antwortet.
            response = requests.get(NASA_GISTEMP_URL, timeout=self.timeout)

            # Prüfen ob der Server einen Fehler zurückgegeben hat.
            # HTTP-Statuscodes: 200 = OK, 404 = Not Found, 500 = Server Error
            # raise_for_status() wirft automatisch eine Exception bei 4xx/5xx.
            response.raise_for_status()

            logger.debug(
                "HTTP-Antwort erhalten: Status %d, Größe %d Bytes",
                response.status_code, len(response.content),
            )

            # Antwort als Text zurückgeben (UTF-8 Encoding)
            return response.text

        except requests.exceptions.Timeout:
            # Timeout: Server hat nach X Sekunden nicht geantwortet.
            msg = (
                f"Timeout nach {self.timeout}s beim Abruf von {NASA_GISTEMP_URL}. "
                "NASA-Server möglicherweise nicht erreichbar."
            )
            logger.error(msg)
            raise ConnectionError(msg) from None

        except requests.exceptions.ConnectionError as exc:
            # Netzwerkfehler: Kein Internet, DNS-Problem o.ä.
            msg = f"Netzwerkfehler beim Abruf von {NASA_GISTEMP_URL}: {exc}"
            logger.error(msg)
            raise ConnectionError(msg) from exc

        except requests.exceptions.HTTPError as exc:
            # HTTP-Fehler: Server hat mit einem Fehlercode geantwortet.
            msg = f"HTTP-Fehler {response.status_code} von NASA-Server: {exc}"
            logger.error(msg)
            raise ValueError(msg) from exc

    # ─────────────────────────────────────────────────────────────────────────
    # Private Methode: _parse_and_normalize
    # Wandelt den CSV-Text in eine Liste von DataPoints um.
    # ─────────────────────────────────────────────────────────────────────────
    def _parse_and_normalize(self, raw_csv: str) -> List[DataPoint]:
        """
        Parst den CSV-Text der NASA und normalisiert ihn in DataPoints.

        Was bedeutet "Normalisieren"?
        Verschiedene Datenquellen liefern Daten in unterschiedlichen Formaten.
        Normalisierung bedeutet: Wir überführen alle Daten in ein einheitliches
        Format (unsere DataPoint-Klasse), damit alle Teams im Projekt mit
        denselben Strukturen arbeiten können.

        Wie sieht die NASA-CSV aus?
        Die Datei beginnt mit Kommentarzeilen (die mit "YEAR" beginnen).
        Danach kommen Zeilen wie:
            1880,  -0.16,  -0.08,  -0.12, ...
        Spalte 0 = Jahr, Spalte 1-12 = monatliche Anomalie,
        Spalte 13 = Jahresmittel ("J-D"), Spalte 14 = Jun-Aug Mittel etc.
        Wir verwenden ausschließlich den Jahresmittelwert (Spalte "J-D").

        Args:
            raw_csv: Roher CSV-Text von der NASA-URL.

        Returns:
            Liste von DataPoint-Objekten, sortiert nach Zeitstempel.

        Raises:
            ValueError: Wenn das CSV-Format nicht erkannt wird.
        """
        data_points: List[DataPoint] = []

        # io.StringIO ermöglicht es, einen String wie eine Datei zu lesen.
        # csv.reader erwartet ein "dateiartiges" Objekt, keinen plain String.
        reader = csv.reader(io.StringIO(raw_csv))

        # Index der Jahresmittelwert-Spalte (wird beim Header-Parsing gesetzt)
        annual_mean_col_idx: Optional[int] = None
        header_found = False

        for row_num, row in enumerate(reader, start=1):
            # Leere Zeilen überspringen
            if not row:
                continue

            # Die erste Spalte bereinigen (NASA hat manchmal Leerzeichen)
            first_cell = row[0].strip()

            # ── Header-Zeile finden ──────────────────────────────────────────
            # Die NASA-CSV enthält eine Kopfzeile mit "Year" in der ersten Zelle.
            # Dahinter stehen die Monatsnamen und "J-D" (January–December = Jahresmittel).
            if first_cell == "Year" and not header_found:
                header_found = True
                # Suche den Index der "J-D" Spalte (= Jahresmittelwert)
                headers = [h.strip() for h in row]
                try:
                    annual_mean_col_idx = headers.index("J-D")
                    logger.debug(
                        "Header gefunden in Zeile %d. 'J-D' ist Spalte %d.",
                        row_num, annual_mean_col_idx,
                    )
                except ValueError:
                    raise ValueError(
                        "NASA GISTEMP CSV: Spalte 'J-D' (Jahresmittelwert) "
                        "nicht in Header-Zeile gefunden. "
                        "Hat die NASA das Format geändert?"
                    )
                continue  # Header-Zeile selbst nicht als Daten verarbeiten

            # ── Vor dem Header: Kommentarzeilen überspringen ─────────────────
            if not header_found:
                continue

            # ── Datenzeilen verarbeiten ──────────────────────────────────────
            # Nach dem Header erwarten wir Zeilen mit Jahr und Messwerten.
            # Zeilen, die nicht mit einer vierstelligen Jahreszahl beginnen,
            # überspringen (z.B. Leerzeilen am Ende oder Fußnoten).
            if not first_cell.isdigit() or len(first_cell) != 4:
                continue

            # Einzelne Datenzeile parsen
            data_point = self._parse_data_row(
                row=row,
                row_num=row_num,
                annual_mean_col_idx=annual_mean_col_idx,
            )

            # None bedeutet: Messwert fehlt (NASA markiert das mit "***")
            # Fehlende Werte werden nicht in den Datensatz aufgenommen.
            if data_point is not None:
                data_points.append(data_point)

        if not header_found:
            raise ValueError(
                "NASA GISTEMP CSV: Kein Header mit 'Year' gefunden. "
                "Möglicherweise hat die NASA das Format geändert."
            )

        if not data_points:
            raise ValueError(
                "NASA GISTEMP CSV: Keine Datenpunkte extrahiert. "
                "Prüfe das CSV-Format und den Parser."
            )

        logger.info("%d gültige Jahresmittelwerte extrahiert.", len(data_points))

        # Nach Zeitstempel sortieren (älteste Daten zuerst)
        data_points.sort(key=lambda dp: dp.timestamp)
        return data_points

    def _parse_data_row(
        self,
        row: List[str],
        row_num: int,
        annual_mean_col_idx: int,
    ) -> Optional[DataPoint]:
        """
        Verarbeitet eine einzelne Datenzeile der NASA-CSV.

        Was passiert hier?
        Wir lesen Jahr und Jahresmittelwert aus einer CSV-Zeile aus und
        erstellen daraus einen DataPoint.

        Args:
            row: Liste der Zellenwerte einer CSV-Zeile.
            row_num: Zeilennummer (nur für Fehlermeldungen).
            annual_mean_col_idx: Index der "J-D" Spalte im CSV.

        Returns:
            DataPoint oder None bei fehlenden/ungültigen Daten.
        """
        # Jahr aus der ersten Spalte lesen
        year_str = row[0].strip()

        # Prüfen ob die Zeile genug Spalten hat
        if len(row) <= annual_mean_col_idx:
            logger.warning(
                "Zeile %d hat zu wenige Spalten (%d < %d) — übersprungen.",
                row_num, len(row), annual_mean_col_idx + 1,
            )
            return None

        # Jahresmittelwert lesen
        value_str = row[annual_mean_col_idx].strip()

        # Fehlende Werte überspringen (NASA markiert Lücken mit "***")
        if value_str == NASA_MISSING_VALUE_MARKER or not value_str:
            logger.debug(
                "Zeile %d (Jahr %s): Fehlender Jahresmittelwert — übersprungen.",
                row_num, year_str,
            )
            return None

        # Messwert in Dezimalzahl umwandeln
        # NASA liefert z.B. "1.17" oder "-0.08"
        try:
            value = float(value_str)
        except ValueError:
            logger.warning(
                "Zeile %d (Jahr %s): Ungültiger Zahlenwert '%s' — übersprungen.",
                row_num, year_str, value_str,
            )
            return None

        # Zeitstempel erstellen: 1. Januar des jeweiligen Jahres, 00:00 UTC
        # Da NASA nur Jahresmittelwerte liefert, setzen wir den Zeitpunkt
        # auf den Anfang des Jahres.
        try:
            timestamp = datetime(int(year_str), 1, 1, tzinfo=timezone.utc)
        except (ValueError, OverflowError):
            logger.warning(
                "Zeile %d: Ungültiges Jahr '%s' — übersprungen.",
                row_num, year_str,
            )
            return None

        # DataPoint erstellen und zurückgeben
        return DataPoint(
            timestamp=timestamp,
            value=value,
            # Einheit: °C Abweichung vom Referenzzeitraum 1951–1980
            unit="°C anomaly (vs. 1951-1980 baseline)",
            # Qualität: NASA-Daten sind geprüft und kalibriert → "good"
            quality_flag="good",
        )