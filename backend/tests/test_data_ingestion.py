"""
DP-08: Unit Tests für das Data Ingestion Module.

Testfälle pro Klasse:
  NasaGissClient  – Parsing, Filterung, Netzwerkfehler
  NoaaClient      – Parsing, fehlende Werte, Netzwerkfehler
  NsidcClient     – Parsing, unbekannte Variable, Wertebereich
  DataValidator   – Pflichtfelder, Wertebereiche, fehlende Werte, Datumsformate
  DataNormalizer  – Datumsformate, Duplikate, ungültige Werte
  DataCache       – Speichern, Laden, Prüfen
  DataIngestionService – Vollständiger Workflow mit Mocks

Alle Netzwerkaufrufe werden mit unittest.mock.patch gemockt.
"""

import json
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from backend.modules.data_ingestion.cache import DataCache
from backend.modules.data_ingestion.nasa_client import NasaGissClient
from backend.modules.data_ingestion.noaa_client import NoaaClient
from backend.modules.data_ingestion.normalizer import DataNormalizer
from backend.modules.data_ingestion.nsidc_client import NsidcClient
from backend.modules.data_ingestion.service import DataIngestionService
from backend.modules.data_ingestion.validator import DataValidator

# ---------------------------------------------------------------------------
# Fixtures – Beispiel-CSV-Inhalte
# ---------------------------------------------------------------------------

NASA_CSV_SAMPLE = textwrap.dedent("""\
    Global Surface Temperature Change (°C) — GISTEMP v4
    Year,Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec,J-D,D-N,DJF,MAM,JJA,SON
    2020,.80,.91,1.05,.93,.92,.93,.93,.88,.97,.99,1.09,1.16,.96,***,***,.97,.91,1.02
    2021,.96,.75,.93,.76,.80,.89,.98,.87,.91,1.05,.92,.88,.89,***,.98,.83,.91,.96
    2022,.89,.87,.89,.94,.92,.88,.88,1.00,.86,.99,.87,.78,.90,***,.90,.92,.92,.91
""")

NOAA_CSV_SAMPLE = textwrap.dedent("""\
    # CO2 Mole Fraction (ppm) — Mauna Loa monthly averages
    # year, month, decimal_date, monthly_avg, deseasonalized, ndays, sdev, unc
    2020,1,2020.042,413.39,413.74,26,0.26,0.11
    2020,2,2020.126,414.11,413.55,28,0.20,0.09
    2020,3,2020.208,-99.99,414.10,-1,0.00,0.00
    2020,4,2020.292,416.21,413.66,28,0.22,0.09
""")

NSIDC_CSV_SAMPLE = textwrap.dedent("""\
    Year, Mo, data-type, region,  extent,     area
    2020,  1, Goddard,   N,       13.58,      12.10
    2020,  2, Goddard,   N,       14.52,      13.01
    2020,  3, Goddard,   N,       14.78,      13.44
    2020,  4, Goddard,   N,       -9.99,      12.20
""")


def _make_mock_response(text: str, status_code: int = 200) -> MagicMock:
    """Erstellt ein Mock-Response-Objekt, das requests.Response imitiert."""
    mock = MagicMock()
    mock.text = text
    mock.status_code = status_code
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock
        )
    return mock


# ---------------------------------------------------------------------------
# NasaGissClient
# ---------------------------------------------------------------------------

class TestNasaGissClient:

    def test_fetch_gibt_dataset_im_richtigen_format_zurueck(self):
        """Erfolgreicher Abruf gibt Dataset-Dict mit Pflichtfeldern zurück."""
        client = NasaGissClient()
        with patch.object(client, "_get", return_value=_make_mock_response(NASA_CSV_SAMPLE)):
            result = client.fetch("2020-01-01", "2021-12-31")

        assert result["source"] == "nasa"
        assert result["variable"] == "temperature"
        assert result["unit"] == "°C"
        assert result["reference_period"] == "1951-1980"
        assert "data" in result
        assert "metadata" in result

    def test_parse_erkennt_fehlende_werte_als_none(self):
        """Sternchen (***) in der NASA-CSV müssen als None normalisiert werden."""
        client = NasaGissClient()
        records = client._parse(NASA_CSV_SAMPLE)
        # Der J-D Jahreswert 2020 enthält ***, aber die Monatsdaten sind vorhanden.
        # Wir prüfen nur, dass keine Ausnahme ausgelöst wird und None-Werte vorkommen.
        values = [r["value"] for r in records]
        # Alle Werte sind entweder float oder None
        for v in values:
            assert v is None or isinstance(v, float)

    def test_filter_by_date_begrenzt_zeitraum(self):
        """Filterung auf Zeitraum gibt nur Datenpunkte innerhalb des Bereichs zurück."""
        client = NasaGissClient()
        records = client._parse(NASA_CSV_SAMPLE)
        filtered = client._filter_by_date(records, "2021-01-01", "2021-12-31")
        for r in filtered:
            assert "2021-01-01" <= r["date"] <= "2021-12-31"

    def test_fetch_bei_timeout_wirft_exception(self):
        """Bei Netzwerk-Timeout wird eine RequestException weitergegeben."""
        client = NasaGissClient()
        with patch.object(
            client, "_get", side_effect=requests.exceptions.Timeout("Timeout")
        ):
            with pytest.raises(requests.exceptions.Timeout):
                client.fetch("2020-01-01", "2020-12-31")

    def test_fetch_bei_http_404_wirft_exception(self):
        """Bei HTTP 404 wird eine HTTPError weitergegeben."""
        client = NasaGissClient()
        with patch.object(
            client, "_get", side_effect=requests.exceptions.HTTPError("404")
        ):
            with pytest.raises(requests.exceptions.HTTPError):
                client.fetch("2020-01-01", "2020-12-31")

    def test_parse_ungueltige_csv_struktur_wirft_valueerror(self):
        """Unbekannte CSV-Struktur (fehlende Spalten) löst ValueError aus."""
        client = NasaGissClient()
        with pytest.raises(ValueError, match="fehlende Spalten"):
            client._parse("Spalte1,Spalte2\n1,2\n")

    def test_datenpunkte_sind_chronologisch_sortiert(self):
        """Datenpunkte müssen aufsteigend nach Datum sortiert sein."""
        client = NasaGissClient()
        records = client._parse(NASA_CSV_SAMPLE)
        dates = [r["date"] for r in records]
        assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# NoaaClient
# ---------------------------------------------------------------------------

class TestNoaaClient:

    def test_fetch_gibt_co2_dataset_zurueck(self):
        """Erfolgreicher Abruf gibt CO₂-Dataset mit korrekten Feldern zurück."""
        client = NoaaClient()
        with patch.object(client, "_get", return_value=_make_mock_response(NOAA_CSV_SAMPLE)):
            result = client.fetch("2020-01-01", "2020-12-31")

        assert result["source"] == "noaa"
        assert result["variable"] == "co2"
        assert result["unit"] == "ppm"

    def test_fehlwert_minus_9999_wird_als_none_gespeichert(self):
        """CO₂-Fehlwert -99.99 muss als None normalisiert werden."""
        client = NoaaClient()
        records = client._parse(NOAA_CSV_SAMPLE)
        # März 2020 hat Fehlwert -99.99
        maerz = next((r for r in records if r["date"] == "2020-03-01"), None)
        assert maerz is not None
        assert maerz["value"] is None

    def test_gueltige_werte_werden_korrekt_uebernommen(self):
        """Gültige CO₂-Werte werden als float gespeichert."""
        client = NoaaClient()
        records = client._parse(NOAA_CSV_SAMPLE)
        januar = next(r for r in records if r["date"] == "2020-01-01")
        assert januar["value"] == pytest.approx(413.39)

    def test_fetch_bei_timeout_wirft_exception(self):
        """Bei Netzwerk-Timeout wird eine RequestException weitergegeben."""
        client = NoaaClient()
        with patch.object(
            client, "_get", side_effect=requests.exceptions.Timeout()
        ):
            with pytest.raises(requests.exceptions.Timeout):
                client.fetch("2020-01-01", "2020-12-31")


# ---------------------------------------------------------------------------
# NsidcClient
# ---------------------------------------------------------------------------

class TestNsidcClient:

    def test_fetch_arctic_gibt_korrektes_dataset_zurueck(self):
        """Abruf der Arktis-Daten gibt Dataset mit korrekten Metadaten zurück."""
        client = NsidcClient()
        with patch.object(client, "_get", return_value=_make_mock_response(NSIDC_CSV_SAMPLE)):
            result = client.fetch("2020-01-01", "2020-12-31", variable="sea_ice_arctic")

        assert result["source"] == "nsidc"
        assert result["variable"] == "sea_ice_arctic"
        assert result["unit"] == "Millionen km²"

    def test_unbekannte_variable_wirft_valueerror(self):
        """Unbekannte Variable löst ValueError aus."""
        client = NsidcClient()
        with pytest.raises(ValueError, match="Unbekannte Variable"):
            client.fetch("2020-01-01", "2020-12-31", variable="unbekannt")

    def test_unplausibler_wert_wird_als_none_markiert(self):
        """Werte außerhalb des physikalischen Bereichs werden als None gespeichert."""
        client = NsidcClient()
        records = client._parse(NSIDC_CSV_SAMPLE)
        # April 2020 hat -9.99 → außerhalb [0, 20]
        april = next((r for r in records if r["date"] == "2020-04-01"), None)
        assert april is not None
        assert april["value"] is None

    def test_gueltige_werte_korrekt_gelesen(self):
        """Gültige Eisausdehnungswerte werden als float gespeichert."""
        client = NsidcClient()
        records = client._parse(NSIDC_CSV_SAMPLE)
        januar = next(r for r in records if r["date"] == "2020-01-01")
        assert januar["value"] == pytest.approx(13.58)


# ---------------------------------------------------------------------------
# DataValidator
# ---------------------------------------------------------------------------

def _minimal_dataset(**overrides) -> dict:
    """Erstellt ein minimales gültiges Dataset-Dict für Tests."""
    base = {
        "source": "nasa",
        "variable": "temperature",
        "unit": "°C",
        "reference_period": "1951-1980",
        "data": [
            {"date": "2020-01-01", "value": 0.5},
            {"date": "2020-02-01", "value": 0.6},
        ],
        "metadata": {
            "source_name": "NASA GISS",
            "source_url": "https://example.com",
            "retrieved_at": "2024-01-01T00:00:00Z",
            "license": "Public Domain",
        },
    }
    base.update(overrides)
    return base


class TestDataValidator:

    def test_gueltiger_datensatz_ist_valid(self):
        """Ein vollständiger, plausibler Datensatz muss als gültig erkannt werden."""
        validator = DataValidator()
        result = validator.validate(_minimal_dataset())
        assert result.is_valid
        assert result.errors == []

    def test_fehlende_pflichtfelder_erzeugen_fehler(self):
        """Fehlende Pflichtfelder müssen als Fehler markiert werden."""
        validator = DataValidator()
        dataset = _minimal_dataset()
        del dataset["source"]
        result = validator.validate(dataset)
        assert not result.is_valid
        assert any("source" in e for e in result.errors)

    def test_leerer_datensatz_ist_ungueltig(self):
        """Ein Datensatz ohne Datenpunkte ist ungültig."""
        validator = DataValidator()
        result = validator.validate(_minimal_dataset(data=[]))
        assert not result.is_valid

    def test_ungueltige_datums_format_erzeugt_fehler(self):
        """Datenpunkte mit falschem Datumsformat müssen als Fehler erkannt werden."""
        validator = DataValidator()
        dataset = _minimal_dataset(data=[{"date": "01.01.2020", "value": 0.5}])
        result = validator.validate(dataset)
        assert not result.is_valid

    def test_none_werte_werden_als_fehlend_gezaehlt(self):
        """None-Werte müssen als fehlende Messung gezählt werden."""
        validator = DataValidator()
        dataset = _minimal_dataset(data=[
            {"date": "2020-01-01", "value": None},
            {"date": "2020-02-01", "value": 0.5},
        ])
        result = validator.validate(dataset)
        assert result.missing_count == 1
        assert result.is_valid  # 1 von 2 fehlend = 50 % → Warnung, kein Fehler

    def test_werte_ausserhalb_bereich_erzeugen_warnung(self):
        """Werte außerhalb des definierten Bereichs erzeugen eine Warnung."""
        validator = DataValidator()
        dataset = _minimal_dataset(data=[
            {"date": "2020-01-01", "value": 99.9},  # Unmöglich für Temperaturanomalie
        ])
        result = validator.validate(dataset)
        assert result.is_valid  # Warnungen machen den Datensatz nicht ungültig
        assert any("Bereich" in w for w in result.warnings)

    def test_doppelte_datumseintraege_erzeugen_warnung(self):
        """Doppelt vorkommende Datumseinträge erzeugen eine Warnung."""
        validator = DataValidator()
        dataset = _minimal_dataset(data=[
            {"date": "2020-01-01", "value": 0.5},
            {"date": "2020-01-01", "value": 0.6},  # Duplikat
        ])
        result = validator.validate(dataset)
        assert any("Doppelter" in w for w in result.warnings)

    def test_fehlende_metadatenfelder_erzeugen_fehler(self):
        """Fehlende Pflichtfelder in metadata erzeugen Fehler."""
        validator = DataValidator()
        dataset = _minimal_dataset()
        del dataset["metadata"]["source_url"]
        result = validator.validate(dataset)
        assert not result.is_valid


# ---------------------------------------------------------------------------
# DataNormalizer
# ---------------------------------------------------------------------------

class TestDataNormalizer:

    def test_standardformat_bleibt_unveraendert(self):
        """Datenpunkte im Standardformat 'YYYY-MM-DD' werden unverändert übernommen."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset()
        result = normalizer.normalize(dataset)
        assert result["data"][0]["date"] == "2020-01-01"

    def test_alternatives_datumsformat_wird_normalisiert(self):
        """Datumstrings im Format 'YYYY/MM/DD' werden zu 'YYYY-MM-DD' konvertiert."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[{"date": "2020/03/01", "value": 0.7}])
        result = normalizer.normalize(dataset)
        assert result["data"][0]["date"] == "2020-03-01"

    def test_duplikate_werden_entfernt(self):
        """Doppelte Datumseinträge werden auf einen reduziert (erster Wert gewinnt)."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[
            {"date": "2020-01-01", "value": 0.5},
            {"date": "2020-01-01", "value": 0.9},  # Duplikat
        ])
        result = normalizer.normalize(dataset)
        assert len(result["data"]) == 1
        assert result["data"][0]["value"] == pytest.approx(0.5)

    def test_ungueltiges_datum_wird_uebersprungen(self):
        """Datenpunkte mit nicht-parsebarem Datum werden übersprungen."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[
            {"date": "kein-datum", "value": 0.5},
            {"date": "2020-02-01", "value": 0.6},
        ])
        result = normalizer.normalize(dataset)
        assert len(result["data"]) == 1
        assert result["data"][0]["date"] == "2020-02-01"

    def test_none_wert_bleibt_none(self):
        """None-Werte bleiben nach der Normalisierung None."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[{"date": "2020-01-01", "value": None}])
        result = normalizer.normalize(dataset)
        assert result["data"][0]["value"] is None

    def test_string_wert_wird_zu_float(self):
        """String-Zahlen (z.B. '0.75') werden in float konvertiert."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[{"date": "2020-01-01", "value": "0.75"}])
        result = normalizer.normalize(dataset)
        assert result["data"][0]["value"] == pytest.approx(0.75)

    def test_ergebnis_ist_chronologisch_sortiert(self):
        """Datenpunkte müssen nach der Normalisierung aufsteigend sortiert sein."""
        normalizer = DataNormalizer()
        dataset = _minimal_dataset(data=[
            {"date": "2020-03-01", "value": 0.8},
            {"date": "2020-01-01", "value": 0.5},
            {"date": "2020-02-01", "value": 0.6},
        ])
        result = normalizer.normalize(dataset)
        dates = [r["date"] for r in result["data"]]
        assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# DataCache
# ---------------------------------------------------------------------------

class TestDataCache:

    def test_save_und_load_processed(self, tmp_path):
        """Gespeicherter Datensatz kann korrekt wieder geladen werden."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        dataset = _minimal_dataset()
        cache.save_processed(dataset)
        loaded = cache.load_processed("nasa", "temperature")
        assert loaded is not None
        assert loaded["source"] == "nasa"
        assert loaded["variable"] == "temperature"

    def test_is_cached_gibt_false_bei_fehlendem_eintrag(self, tmp_path):
        """is_cached gibt False zurück, wenn kein Eintrag gespeichert wurde."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        assert not cache.is_cached("nasa", "temperature")

    def test_is_cached_gibt_true_nach_speichern(self, tmp_path):
        """is_cached gibt True zurück, nachdem ein Datensatz gespeichert wurde."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        cache.save_processed(_minimal_dataset())
        assert cache.is_cached("nasa", "temperature")

    def test_save_raw_erstellt_datei(self, tmp_path):
        """save_raw erstellt eine neue Datei in data/raw/."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        path = cache.save_raw("nasa", "temperature", "raw,csv,content")
        assert path.exists()
        assert path.read_text() == "raw,csv,content"

    def test_load_processed_gibt_none_bei_fehlendem_cache(self, tmp_path):
        """load_processed gibt None zurück, wenn kein Cache-Eintrag vorhanden ist."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        result = cache.load_processed("noaa", "co2")
        assert result is None


# ---------------------------------------------------------------------------
# DataIngestionService (Integrations-ähnliche Tests mit Mocks)
# ---------------------------------------------------------------------------

class TestDataIngestionService:

    def test_vollstaendiger_workflow_nasa(self, tmp_path):
        """
        Vollständiger Workflow: Abruf → Normalisierung → Validierung → Cache → Filterung.
        Netzwerkaufruf wird durch Mock ersetzt.
        """
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        service = DataIngestionService(cache=cache)

        with patch(
            "backend.modules.data_ingestion.nasa_client.NasaGissClient._get",
            return_value=_make_mock_response(NASA_CSV_SAMPLE),
        ):
            result = service.get_dataset("nasa", "temperature", "2020-01-01", "2020-12-31")

        assert result["source"] == "nasa"
        assert result["variable"] == "temperature"
        assert all("2020-01-01" <= r["date"] <= "2020-12-31" for r in result["data"])

    def test_cache_wird_beim_zweiten_aufruf_genutzt(self, tmp_path):
        """Beim zweiten Aufruf für dieselbe Quelle wird der Cache genutzt (kein Netzwerkaufruf)."""
        cache = DataCache(
            raw_path=tmp_path / "raw",
            processed_path=tmp_path / "processed",
        )
        service = DataIngestionService(cache=cache)

        with patch(
            "backend.modules.data_ingestion.nasa_client.NasaGissClient._get",
            return_value=_make_mock_response(NASA_CSV_SAMPLE),
        ) as mock_get:
            service.get_dataset("nasa", "temperature", "2020-01-01", "2020-12-31")
            service.get_dataset("nasa", "temperature", "2020-01-01", "2020-06-30")

        # _get darf nur einmal aufgerufen worden sein (zweiter Aufruf nutzt Cache)
        assert mock_get.call_count == 1

    def test_unbekannte_quelle_wirft_valueerror(self, tmp_path):
        """Unbekannte Quelle löst ValueError aus."""
        cache = DataCache(raw_path=tmp_path / "raw", processed_path=tmp_path / "processed")
        service = DataIngestionService(cache=cache)
        with pytest.raises(ValueError, match="Unbekannte Kombination"):
            service.get_dataset("unbekannt", "temperature", "2020-01-01", "2020-12-31")

    def test_get_sources_gibt_alle_quellen_zurueck(self, tmp_path):
        """get_sources gibt alle registrierten Quellen zurück."""
        cache = DataCache(raw_path=tmp_path / "raw", processed_path=tmp_path / "processed")
        service = DataIngestionService(cache=cache)
        sources = service.get_sources()
        source_ids = [s["id"] for s in sources]
        assert "nasa" in source_ids
        assert "noaa" in source_ids
        assert "nsidc" in source_ids

    def test_netzwerkfehler_wird_weitergegeben(self, tmp_path):
        """Netzwerkfehler beim Abruf wird als RequestException weitergegeben."""
        cache = DataCache(raw_path=tmp_path / "raw", processed_path=tmp_path / "processed")
        service = DataIngestionService(cache=cache)
        with patch(
            "backend.modules.data_ingestion.nasa_client.NasaGissClient._get",
            side_effect=requests.exceptions.ConnectionError("Verbindung fehlgeschlagen"),
        ):
            with pytest.raises(requests.exceptions.ConnectionError):
                service.get_dataset("nasa", "temperature", "2020-01-01", "2020-12-31")