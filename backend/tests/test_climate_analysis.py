# backend/tests/test_climate_analysis.py
"""
Unit Tests für das Climate Analysis Module (CA-08)
Verantwortlich: Climate Analysis Team
Branch: team/climate-analysis

Testabdeckung:
  - compute_trend:        positiver Trend, negativer Trend, NaN-Umgang,
                          zu wenige Punkte
  - compute_correlation:  perfekte Korrelation, negative Korrelation,
                          identische Datensätze, NaN-Umgang
  - compute_anomalies:    bekannter Referenzwert, leerer Referenzzeitraum,
                          NaN-Werte werden übersprungen
  - compute_moving_average: Basisfall, ungültige Fenstergröße
  - build_analysis_summary: vollständige Ausgabe
"""

from __future__ import annotations

import math
import pytest

from modules.climate_analysis.analysis import (
    build_analysis_summary,
    compute_anomalies,
    compute_correlation,
    compute_moving_average,
    compute_trend,
)


# ---------------------------------------------------------------------------
# Hilfsfunktionen für Test-Datensätze
# ---------------------------------------------------------------------------

def _make_dataset(
    values: list[float | None],
    start_year: int = 2000,
    variable: str = "temperature",
    unit: str = "°C",
    source: str = "test",
) -> dict:
    """
    Erstellt einen minimalen normierten Datensatz für Tests.
    Erzeugt monatliche Datenpunkte ab start_year.
    """
    data = []
    for i, v in enumerate(values):
        year = start_year + i // 12
        month = (i % 12) + 1
        data.append({"date": f"{year}-{month:02d}-01", "value": v})
    return {
        "source": source,
        "variable": variable,
        "unit": unit,
        "data": data,
        "metadata": {"source_name": "Test", "license": "Public Domain"},
    }


def _make_annual_dataset(
    values: list[float | None],
    start_year: int = 2000,
    variable: str = "temperature",
    unit: str = "°C",
) -> dict:
    """
    Erstellt einen Datensatz mit Jahresdatenpunkten (1. Januar).
    """
    data = [
        {"date": f"{start_year + i}-01-01", "value": v}
        for i, v in enumerate(values)
    ]
    return {"source": "test", "variable": variable, "unit": unit,
            "data": data, "metadata": {}}


START = "2000-01-01"
END_5Y = "2004-12-31"
END_10Y = "2009-12-31"


# ===========================================================================
# Tests: compute_trend
# ===========================================================================

class TestComputeTrend:

    def test_positiver_trend_bei_steigenden_werten(self):
        """Stetig steigende Werte müssen einen positiven Trend pro Jahrzehnt ergeben."""
        # 10 Jahreswerte: 14.0, 14.2, ..., 15.8 → klar positiver Trend
        values = [14.0 + i * 0.2 for i in range(10)]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")

        assert result["trend_per_decade"] > 0
        assert result["r_squared"] > 0.99
        assert result["p_value"] < 0.001
        assert "positiver Trend" in result["interpretation"]

    def test_negativer_trend_bei_fallenden_werten(self):
        """Stetig fallende Werte müssen einen negativen Trend ergeben."""
        values = [15.0 - i * 0.15 for i in range(10)]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")

        assert result["trend_per_decade"] < 0
        assert result["p_value"] < 0.05
        assert "negativer Trend" in result["interpretation"]

    def test_kein_signifikanter_trend_bei_konstantem_rauschen(self):
        """Rein zufällige Werte um einen Mittelwert → p > 0.05 möglich."""
        # Reproduzierbare Pseudodaten ohne Trend
        values = [0.1, -0.1, 0.2, -0.2, 0.0, 0.1, -0.1, 0.2, -0.2, 0.0]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")

        assert "interpretation" in result
        # p_value muss vorhanden sein (Wert selbst nicht gepinnt)
        assert 0.0 <= result["p_value"] <= 1.0

    def test_nan_werte_werden_ignoriert(self):
        """NaN-Werte dürfen die Trendberechnung nicht verfälschen oder abbrechen."""
        # Gerade Werte sind aufsteigend, NaN in der Mitte
        values = [14.0, None, 14.4, None, 14.8, 15.0, 15.2, 15.4, 15.6, 15.8]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")

        assert result["trend_per_decade"] > 0
        assert result["n_points"] == 8  # 2 NaN-Werte entfernt

    def test_zu_wenige_punkte_wirft_valueerror(self):
        """Weniger als 3 gültige Punkte müssen ValueError auslösen."""
        ds = _make_annual_dataset([14.0, 14.5], start_year=2000)
        with pytest.raises(ValueError, match="Zu wenige Datenpunkte"):
            compute_trend(ds, "2000-01-01", "2001-12-31")

    def test_alle_nan_wirft_valueerror(self):
        """Alle None-Werte → kein gültiger Datenpunkt → ValueError."""
        ds = _make_annual_dataset([None, None, None, None, None], start_year=2000)
        with pytest.raises(ValueError):
            compute_trend(ds, "2000-01-01", "2004-12-31")

    def test_einheit_enthält_pro_jahrzehnt(self):
        """Die Einheit im TrendResult muss '/Jahrzehnt' enthalten."""
        values = [i * 0.1 for i in range(10)]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")
        assert "/Jahrzehnt" in result["unit"]

    def test_zeitraum_in_ergebnis(self):
        """Analysezeitraum muss im Ergebnis enthalten sein."""
        values = [i * 0.1 for i in range(10)]
        ds = _make_annual_dataset(values, start_year=2000)
        result = compute_trend(ds, "2000-01-01", "2009-12-31")
        assert result["period"]["start"] == "2000-01-01"
        assert result["period"]["end"] == "2009-12-31"


# ===========================================================================
# Tests: compute_correlation
# ===========================================================================

class TestComputeCorrelation:

    def test_korrelation_identische_datensaetze_ist_eins(self):
        """Zwei identische Datensätze müssen Korrelation = 1.0 ergeben."""
        values = [float(i) for i in range(1, 25)]
        ds = _make_dataset(values, start_year=2000)
        result = compute_correlation(ds, ds, "2000-01-01", "2001-12-31")

        assert math.isclose(result["correlation"], 1.0, abs_tol=1e-6)
        assert result["p_value"] < 0.001

    def test_perfekt_negative_korrelation(self):
        """Invertierte Werte müssen Korrelation = -1.0 ergeben."""
        values_a = [float(i) for i in range(1, 13)]
        values_b = [float(-i) for i in range(1, 13)]
        ds_a = _make_dataset(values_a, start_year=2000, variable="co2")
        ds_b = _make_dataset(values_b, start_year=2000, variable="temperature")
        result = compute_correlation(ds_a, ds_b, "2000-01-01", "2000-12-31")

        assert math.isclose(result["correlation"], -1.0, abs_tol=1e-6)

    def test_methode_ist_pearson(self):
        """Methode muss immer 'pearson' sein."""
        values = [float(i) for i in range(1, 13)]
        ds = _make_dataset(values, start_year=2000)
        result = compute_correlation(ds, ds, "2000-01-01", "2000-12-31")
        assert result["method"] == "pearson"

    def test_nan_werte_werden_korrekt_behandelt(self):
        """NaN in einem Datensatz → gemeinsame Punkte (inner join) werden genutzt."""
        values_a = [1.0, None, 3.0, 4.0, 5.0, 6.0,
                    7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
        values_b = [float(i) for i in range(1, 13)]
        ds_a = _make_dataset(values_a, start_year=2000)
        ds_b = _make_dataset(values_b, start_year=2000)
        result = compute_correlation(ds_a, ds_b, "2000-01-01", "2000-12-31")

        assert result["n_points"] == 11  # 1 NaN entfernt
        assert result["correlation"] > 0.99

    def test_hinweis_auf_kausalitaet(self):
        """Ergebnis muss einen Hinweis auf fehlende Kausalität enthalten."""
        values = [float(i) for i in range(1, 13)]
        ds = _make_dataset(values, start_year=2000)
        result = compute_correlation(ds, ds, "2000-01-01", "2000-12-31")
        assert "Kausalität" in result["note"]

    def test_zu_wenige_gemeinsame_punkte_wirft_valueerror(self):
        """Weniger als 3 gemeinsame Punkte → ValueError."""
        values_a = [1.0, 2.0]
        ds = _make_dataset(values_a, start_year=2000)
        with pytest.raises(ValueError, match="Zu wenige gemeinsame"):
            compute_correlation(ds, ds, "2000-01-01", "2000-02-28")

    def test_variablen_in_ergebnis(self):
        """variable_a und variable_b müssen im Ergebnis stehen."""
        ds_a = _make_dataset([1.0, 2.0, 3.0, 4.0, 5.0, 6.0,
                               7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
                              variable="co2")
        ds_b = _make_dataset([1.0, 2.0, 3.0, 4.0, 5.0, 6.0,
                               7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
                              variable="temperature")
        result = compute_correlation(ds_a, ds_b, "2000-01-01", "2000-12-31")
        assert result["variable_a"] == "co2"
        assert result["variable_b"] == "temperature"


# ===========================================================================
# Tests: compute_anomalies
# ===========================================================================

class TestComputeAnomalies:

    def test_anomalie_bekannter_referenzwert(self):
        """
        Wenn der Referenzmittelwert 10.0 beträgt und ein Wert 11.5 ist,
        muss die Anomalie exakt 1.5 ergeben.
        """
        # Referenzzeitraum: 2000–2002 mit Mittelwert 10.0
        ref_values = [10.0] * 36  # Jan 2000 – Dez 2002
        # Analysezeitraum: 2003, Wert = 11.5
        analysis_values = [11.5] * 12
        all_values = ref_values + analysis_values

        ds = _make_dataset(all_values, start_year=2000)

        result = compute_anomalies(
            ds,
            start="2003-01-01",
            end="2003-12-31",
            ref_start="2000-01-01",
            ref_end="2002-12-31",
        )

        assert math.isclose(result["reference_period"]["mean"], 10.0, abs_tol=1e-6)
        for point in result["anomalies"]:
            assert math.isclose(point["anomaly"], 1.5, abs_tol=1e-6)

    def test_negative_anomalie_bei_kuehlerem_zeitraum(self):
        """Werte unter dem Referenzmittel → negative Anomalien."""
        ref_values = [10.0] * 36
        analysis_values = [8.0] * 12
        ds = _make_dataset(ref_values + analysis_values, start_year=2000)

        result = compute_anomalies(
            ds,
            start="2003-01-01",
            end="2003-12-31",
            ref_start="2000-01-01",
            ref_end="2002-12-31",
        )

        for point in result["anomalies"]:
            assert point["anomaly"] < 0

    def test_nan_werte_werden_uebersprungen(self):
        """NaN-Werte im Analysezeitraum dürfen nicht in den Anomalie-Output."""
        ref_values = [10.0] * 36
        analysis_values = [11.0, None, 11.0, None] + [11.0] * 8
        ds = _make_dataset(ref_values + analysis_values, start_year=2000)

        result = compute_anomalies(
            ds,
            start="2003-01-01",
            end="2003-12-31",
            ref_start="2000-01-01",
            ref_end="2002-12-31",
        )

        assert result["n_points"] == 10  # 2 NaN-Werte nicht enthalten
        for point in result["anomalies"]:
            assert point["value"] is not None

    def test_leerer_referenzzeitraum_wirft_valueerror(self):
        """Kein Referenzdaten → ValueError."""
        ds = _make_annual_dataset([14.0, 14.5, 15.0], start_year=2000)
        with pytest.raises(ValueError, match="Keine gültigen Daten im Referenzzeitraum"):
            compute_anomalies(
                ds,
                start="2000-01-01",
                end="2002-12-31",
                ref_start="1900-01-01",
                ref_end="1910-12-31",
            )

    def test_referenzperiode_in_ergebnis(self):
        """Referenzzeitraum und Mittelwert müssen im Ergebnis stehen."""
        values = [10.0] * 48  # 4 Jahre
        ds = _make_dataset(values, start_year=2000)
        result = compute_anomalies(
            ds,
            start="2002-01-01",
            end="2003-12-31",
            ref_start="2000-01-01",
            ref_end="2001-12-31",
        )
        assert "mean" in result["reference_period"]
        assert "start" in result["reference_period"]
        assert "end" in result["reference_period"]

    def test_datum_format_iso(self):
        """Datumsformat in Anomalien muss YYYY-MM-DD sein."""
        values = [10.0] * 48
        ds = _make_dataset(values, start_year=2000)
        result = compute_anomalies(
            ds,
            start="2002-01-01",
            end="2002-03-31",
            ref_start="2000-01-01",
            ref_end="2001-12-31",
        )
        for point in result["anomalies"]:
            # Prüfe Format YYYY-MM-DD
            parts = point["date"].split("-")
            assert len(parts) == 3
            assert len(parts[0]) == 4  # Jahr


# ===========================================================================
# Tests: compute_moving_average
# ===========================================================================

class TestComputeMovingAverage:

    def test_basisfall_12_monate(self):
        """Gleitender 12-Monats-Mittelwert gibt n_points > 0 zurück."""
        values = [float(i % 12) for i in range(60)]  # 5 Jahre Monatsdaten
        ds = _make_dataset(values, start_year=2000)
        result = compute_moving_average(ds, "2000-01-01", "2004-12-31", window_months=12)

        assert result["n_points"] > 0
        assert result["window_months"] == 12
        assert "data" in result

    def test_ungueltige_fenstergroesse_wirft_valueerror(self):
        """window_months < 1 → ValueError."""
        values = [1.0] * 24
        ds = _make_dataset(values, start_year=2000)
        with pytest.raises(ValueError, match="window_months muss >= 1"):
            compute_moving_average(ds, "2000-01-01", "2001-12-31", window_months=0)

    def test_konstante_zeitreihe_ergibt_gleichen_mittelwert(self):
        """Konstante Werte → Mittelwert = konstanter Wert."""
        values = [5.0] * 24
        ds = _make_dataset(values, start_year=2000)
        result = compute_moving_average(ds, "2000-01-01", "2001-12-31", window_months=3)

        for point in result["data"]:
            assert math.isclose(point["value"], 5.0, abs_tol=1e-5)


# ===========================================================================
# Tests: build_analysis_summary
# ===========================================================================

class TestBuildAnalysisSummary:

    def test_zusammenfassung_enthält_alle_schlüssel(self):
        """AnalysisSummary muss alle erwarteten Schlüssel enthalten."""
        values = [float(i) for i in range(60)]
        ds = _make_dataset(values, start_year=1951)
        result = build_analysis_summary(
            ds,
            start="1981-01-01",
            end="1985-12-31",
            ref_start="1951-01-01",
            ref_end="1980-12-31",
        )

        expected_keys = {
            "schema_version", "generated_at", "source", "variable",
            "unit", "period", "reference_period", "trend", "anomalies",
            "smoothed_series",
        }
        assert expected_keys.issubset(result.keys())

    def test_trend_in_zusammenfassung_positiv(self):
        """Steigende Ausgangsdaten → positiver Trend in der Zusammenfassung."""
        # Referenz: 1951–1980 (360 Monate, flach bei 0)
        # Analyse: 1981–1990 (steigende Werte)
        ref_values = [0.0] * 360
        analysis_values = [float(i) * 0.01 for i in range(120)]
        ds = _make_dataset(ref_values + analysis_values, start_year=1951,
                           variable="temperature")
        result = build_analysis_summary(
            ds,
            start="1981-01-01",
            end="1990-12-31",
            ref_start="1951-01-01",
            ref_end="1980-12-31",
        )

        assert result["trend"]["per_decade"] > 0