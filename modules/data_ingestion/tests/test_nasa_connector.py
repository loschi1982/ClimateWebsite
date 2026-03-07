# ─────────────────────────────────────────────────────────────────────────────
# Was macht diese Datei?
# Enthält Unit Tests für den NASA GISS Connector.
#
# Was ist ein Unit Test?
# Ein Unit Test überprüft automatisch, ob eine einzelne Funktion ("Unit")
# korrekt funktioniert. Statt manuell zu testen ("ich ruf die Funktion auf
# und schaue was passiert"), definieren wir erwartete Ergebnisse und lassen
# den Computer prüfen ob sie eingehalten werden.
#
# Warum sind Tests wichtig?
# - Sie fangen Fehler früh ab (bevor sie in Produktion landen)
# - Sie dokumentieren, wie Code verwendet werden soll
# - Nach Änderungen kann man sofort prüfen ob alles noch funktioniert
#
# Wie führt man die Tests aus?
# Im Terminal: pytest modules/data_ingestion/tests/test_nasa_connector.py -v
#
# Team: Data Pipeline Team | Branch: feature/data-pipeline
# ─────────────────────────────────────────────────────────────────────────────

# pytest: Das Test-Framework für Python.
# Es findet automatisch alle Funktionen die mit "test_" beginnen und führt sie aus.
import pytest

# unittest.mock: Ermöglicht "Mocking" — das Ersetzen echter Komponenten
# durch Fake-Versionen für Tests.
#
# Was ist Mocking?
# Beim Testen des NASA-Connectors wollen wir nicht wirklich Daten von der NASA
# herunterladen (zu langsam, braucht Internet, ändert sich ständig).
# Stattdessen "mocken" wir den HTTP-Request: Wir ersetzen requests.get() durch
# eine Fake-Funktion, die vordefinierte Testdaten zurückgibt.
from unittest.mock import patch, MagicMock

# requests.exceptions: Für das Testen von Fehlerszenarien
import requests.exceptions

# datetime, timezone: Für Zeitstempel-Prüfungen
from datetime import datetime, timezone

# Unseren Connector importieren (das Modul das wir testen)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from connectors.nasa_giss import NasaGissConnector, NASA_MISSING_VALUE_MARKER
from models.climate_dataset import DataPoint, ClimateDataset


# ─────────────────────────────────────────────────────────────────────────────
# Test-Daten (Fixtures)
# Fixtures sind Testdaten oder Objekte, die von mehreren Tests verwendet werden.
# ─────────────────────────────────────────────────────────────────────────────

# Minimales CSV wie es die NASA liefern würde (vereinfacht für Tests)
SAMPLE_NASA_CSV = """
Global-mean monthly, seasonal, and annual means, 1880-present
Based on the combined land-surface air and sea-surface water temperature anomalies (LOTI)
                                                                                         
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON
1880, -0.20, -0.12, -0.15, -0.19, -0.13, -0.23, -0.15, -0.17, -0.19, -0.22, -0.21, -0.17, -0.17,  ***, ***, -0.16, -0.18, -0.21
1881, -0.19, -0.14, 0.02, 0.01, 0.07, -0.14, -0.02, -0.04, -0.07, -0.22, -0.21, -0.07, -0.08, -0.10, -0.17, 0.03, -0.07, -0.17
2023,  0.95,  1.01,  1.05,  1.04,  1.10,  1.13,  1.17,  1.23,  1.24,  1.31,  1.32,  1.36,  1.17,  1.17,  1.06,  1.06,  1.17,  1.29
"""

# CSV ohne gültige Daten (nur Header)
EMPTY_RESULT_CSV = """
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON
"""

# CSV mit fehlenden Jahresmittelwerten (alles ***)
MISSING_VALUES_CSV = """
Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON
1880, -0.20, -0.12, -0.15, -0.19, -0.13, -0.23, -0.15, -0.17, -0.19, -0.22, -0.21, -0.17, ***, ***, ***, -0.16, -0.18, -0.21
"""


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktion: Erstellt einen Mock-Response
# Ein "Mock-Response" ist ein gefälschtes requests.Response-Objekt.
# ─────────────────────────────────────────────────────────────────────────────
def _make_mock_response(text: str, status_code: int = 200) -> MagicMock:
    """
    Erstellt ein gefälschtes HTTP-Response-Objekt für Tests.

    Warum brauchen wir das?
    requests.get() gibt normalerweise ein Response-Objekt zurück.
    Für Tests mocken wir dieses Objekt, damit kein echter HTTP-Request
    gemacht werden muss.
    """
    mock = MagicMock()
    mock.text = text
    mock.status_code = status_code
    mock.content = text.encode("utf-8")
    # raise_for_status() soll bei 200 nichts tun
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
            f"HTTP Error {status_code}"
        )
    else:
        mock.raise_for_status.return_value = None
    return mock


# ─────────────────────────────────────────────────────────────────────────────
# Test-Klasse: TestNasaGissConnectorInit
# Testet die Initialisierung des Connectors
# ─────────────────────────────────────────────────────────────────────────────
class TestNasaGissConnectorInit:
    """Tests für die Initialisierung des NasaGissConnectors."""

    def test_default_timeout(self):
        """Der Connector soll den Standard-Timeout korrekt setzen."""
        connector = NasaGissConnector()
        assert connector.timeout == 30, (
            f"Erwartet timeout=30, bekommen: {connector.timeout}"
        )

    def test_custom_timeout(self):
        """Der Connector soll einen benutzerdefinierten Timeout akzeptieren."""
        connector = NasaGissConnector(timeout=60)
        assert connector.timeout == 60

    def test_source_reference_created(self):
        """Die SourceReference soll beim Init erstellt werden."""
        connector = NasaGissConnector()
        assert connector.source_reference is not None
        assert "NASA" in connector.source_reference.provider
        assert connector.source_reference.doi == "10.7289/V5T72FNM"

    def test_source_reference_has_url(self):
        """Die SourceReference soll eine gültige URL enthalten."""
        connector = NasaGissConnector()
        assert "nasa.gov" in str(connector.source_reference.url)


# ─────────────────────────────────────────────────────────────────────────────
# Test-Klasse: TestNasaGissConnectorFetchDataset
# Testet den vollständigen Datenabruf
# ─────────────────────────────────────────────────────────────────────────────
class TestNasaGissConnectorFetchDataset:
    """Tests für fetch_dataset() — den Haupt-Einstiegspunkt des Connectors."""

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_returns_climate_dataset(self, mock_get):
        """
        fetch_dataset() soll ein ClimateDataset-Objekt zurückgeben.

        Was macht @patch?
        @patch("connectors.nasa_giss.requests.get") ersetzt requests.get()
        im nasa_giss-Modul durch unsere mock_get-Funktion.
        Alle Aufrufe von requests.get() in diesem Test gehen zu mock_get.
        """
        # Arrange (Vorbereitung): Mock-Response konfigurieren
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)

        # Act (Ausführung): Connector aufrufen
        connector = NasaGissConnector()
        result = connector.fetch_dataset()

        # Assert (Prüfung): War das Ergebnis wie erwartet?
        assert isinstance(result, ClimateDataset), (
            "Ergebnis sollte ein ClimateDataset sein"
        )

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_correct_dataset_id(self, mock_get):
        """Der Datensatz soll die korrekte dataset_id haben."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        assert result.dataset_id == "nasa_giss_surface_temp_v4"

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_correct_number_of_records(self, mock_get):
        """
        Es sollen genau 3 DataPoints extrahiert werden (aus dem Sample-CSV).
        Zeile 1880, 1881, 2023 → 3 Datenpunkte.
        """
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        assert result.record_count == 3, (
            f"Erwartet 3 Datenpunkte, bekommen: {result.record_count}"
        )

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_correct_values(self, mock_get):
        """Die extrahierten Werte sollen den CSV-Werten entsprechen."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()

        # Daten sind nach Zeitstempel sortiert → Index 0 = 1880, 2 = 2023
        assert result.records[0].value == pytest.approx(-0.17, abs=0.001), (
            "Wert für 1880 soll -0.17 sein"
        )
        assert result.records[2].value == pytest.approx(1.17, abs=0.001), (
            "Wert für 2023 soll 1.17 sein"
        )

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_correct_unit(self, mock_get):
        """Die Einheit soll '°C anomaly' enthalten."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        assert "°C" in result.records[0].unit

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_quality_flag_is_good(self, mock_get):
        """Alle NASA GISTEMP Punkte sollen quality_flag='good' haben."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        for dp in result.records:
            assert dp.quality_flag == "good", (
                f"Punkt {dp.timestamp.year} hat quality_flag={dp.quality_flag}"
            )

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_timestamps_are_utc(self, mock_get):
        """Alle Zeitstempel sollen UTC-Zeitzone haben."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        for dp in result.records:
            assert dp.timestamp.tzinfo == timezone.utc, (
                f"Zeitstempel {dp.timestamp} hat keine UTC-Zeitzone"
            )

    @patch("connectors.nasa_giss.requests.get")
    def test_fetch_records_sorted_by_timestamp(self, mock_get):
        """Die Datenpunkte sollen nach Zeitstempel sortiert sein (älteste zuerst)."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        timestamps = [dp.timestamp for dp in result.records]
        assert timestamps == sorted(timestamps), (
            "Datenpunkte sollen aufsteigend nach Zeitstempel sortiert sein"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test-Klasse: TestNasaGissConnectorYearFilter
# Testet die Zeitraumfilterung
# ─────────────────────────────────────────────────────────────────────────────
class TestNasaGissConnectorYearFilter:
    """Tests für die start_year/end_year Filterung."""

    @patch("connectors.nasa_giss.requests.get")
    def test_start_year_filter(self, mock_get):
        """start_year=1881 soll Daten aus 1880 ausschließen."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset(start_year=1881)

        years = [dp.timestamp.year for dp in result.records]
        assert 1880 not in years, "1880 sollte durch start_year=1881 gefiltert werden"
        assert 1881 in years

    @patch("connectors.nasa_giss.requests.get")
    def test_end_year_filter(self, mock_get):
        """end_year=1881 soll Daten aus 2023 ausschließen."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset(end_year=1881)

        years = [dp.timestamp.year for dp in result.records]
        assert 2023 not in years, "2023 sollte durch end_year=1881 gefiltert werden"
        assert 1881 in years

    @patch("connectors.nasa_giss.requests.get")
    def test_year_range_filter(self, mock_get):
        """start_year=1881, end_year=1881 soll genau 1 Datenpunkt liefern."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset(start_year=1881, end_year=1881)

        assert result.record_count == 1
        assert result.records[0].timestamp.year == 1881

    @patch("connectors.nasa_giss.requests.get")
    def test_no_filter_returns_all(self, mock_get):
        """Ohne Filter sollen alle 3 Datenpunkte zurückgegeben werden."""
        mock_get.return_value = _make_mock_response(SAMPLE_NASA_CSV)
        connector = NasaGissConnector()
        result = connector.fetch_dataset()
        assert result.record_count == 3


# ─────────────────────────────────────────────────────────────────────────────
# Test-Klasse: TestNasaGissConnectorErrorHandling
# Testet die Fehlerbehandlung
# ─────────────────────────────────────────────────────────────────────────────
class TestNasaGissConnectorErrorHandling:
    """Tests für alle Fehlerszenarien. Fehler niemals still ignorieren!"""

    @patch("connectors.nasa_giss.requests.get")
    def test_timeout_raises_connection_error(self, mock_get):
        """
        Bei Timeout soll eine ConnectionError-Exception geworfen werden.

        Was testet side_effect?
        Statt einen Rückgabewert zu haben, soll mock_get eine Exception werfen.
        Das simuliert einen Timeout.
        """
        mock_get.side_effect = requests.exceptions.Timeout()
        connector = NasaGissConnector()

        # pytest.raises überprüft, dass die angegebene Exception geworfen wird.
        with pytest.raises(ConnectionError, match="Timeout"):
            connector.fetch_dataset()

    @patch("connectors.nasa_giss.requests.get")
    def test_connection_error_raises_connection_error(self, mock_get):
        """Bei Netzwerkfehler soll ConnectionError geworfen werden."""
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS-Fehler")
        connector = NasaGissConnector()

        with pytest.raises(ConnectionError):
            connector.fetch_dataset()

    @patch("connectors.nasa_giss.requests.get")
    def test_http_404_raises_value_error(self, mock_get):
        """Bei HTTP 404 soll ValueError geworfen werden."""
        mock_get.return_value = _make_mock_response("Not Found", status_code=404)
        connector = NasaGissConnector()

        with pytest.raises(ValueError, match="HTTP-Fehler"):
            connector.fetch_dataset()

    @patch("connectors.nasa_giss.requests.get")
    def test_missing_annual_values_are_skipped(self, mock_get):
        """
        Datenpunkte mit '***' (fehlende Jahresmittelwerte) sollen übersprungen werden.
        Das CSV MISSING_VALUES_CSV hat nur '***' als Jahresmittelwert.
        """
        mock_get.return_value = _make_mock_response(MISSING_VALUES_CSV)
        connector = NasaGissConnector()

        with pytest.raises(ValueError, match="Keine Datenpunkte"):
            connector.fetch_dataset()

    @patch("connectors.nasa_giss.requests.get")
    def test_empty_csv_raises_value_error(self, mock_get):
        """Ein CSV ohne Datenpunkte soll ValueError werfen."""
        mock_get.return_value = _make_mock_response(EMPTY_RESULT_CSV)
        connector = NasaGissConnector()

        with pytest.raises(ValueError):
            connector.fetch_dataset()

    @patch("connectors.nasa_giss.requests.get")
    def test_completely_invalid_csv_raises_value_error(self, mock_get):
        """Ein völlig ungültiges CSV soll ValueError werfen."""
        mock_get.return_value = _make_mock_response("Dies ist kein CSV")
        connector = NasaGissConnector()

        with pytest.raises(ValueError):
            connector.fetch_dataset()