# backend/modules/climate_analysis/analysis.py
"""
Climate Analysis Module – Kernfunktionen
Verantwortlich: Climate Analysis Team
Branch: team/climate-analysis

Dieses Modul berechnet Trends, Korrelationen, Anomalien und gleitende
Mittelwerte auf Basis normalisierter Klimadatensätze des Data Pipeline Teams.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _to_dataframe(dataset: dict[str, Any]) -> pd.DataFrame:
    """
    Wandelt ein normalisiertes Datensatz-Dict in einen DataFrame um.

    Args:
        dataset: Dict im einheitlichen Format des Data Pipeline Teams.
                 Erwartet Schlüssel 'data' mit Liste von
                 {'date': 'YYYY-MM-DD', 'value': float|None}.

    Returns:
        DataFrame mit DatetimeIndex, Spalte 'value' (float, NaN für None).

    Raises:
        ValueError: Wenn 'data' fehlt oder leer ist.
    """
    records = dataset.get("data")
    if not records:
        raise ValueError("Datensatz enthält keine Datenpunkte ('data' fehlt oder leer).")

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def _filter_period(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """
    Filtert einen DataFrame auf einen Zeitraum (inklusiv).

    Args:
        df:    DataFrame mit DatetimeIndex.
        start: Startdatum als ISO-String (YYYY-MM-DD).
        end:   Enddatum als ISO-String (YYYY-MM-DD).

    Returns:
        Gefilterter DataFrame. Kann leer sein.
    """
    return df.loc[start:end]


def _clean(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    Entfernt NaN-Zeilen und gibt numerische Arrays zurück.

    Args:
        df: DataFrame mit Spalte 'value' und DatetimeIndex.

    Returns:
        Tuple (timestamps_in_years, values) als float-Arrays.
        Timestamps werden in Dezimaljahreszahlen umgerechnet
        (z. B. 1980-07-01 → 1980.5), damit linregress sinnvolle
        Steigungen liefert.
    """
    clean = df["value"].dropna()
    # Datum → Dezimaljahreszahl für lineare Regression
    t = clean.index.year + (clean.index.month - 1) / 12
    return t.to_numpy(dtype=float), clean.to_numpy(dtype=float)


# ---------------------------------------------------------------------------
# CA-01: Lineare Trendberechnung
# ---------------------------------------------------------------------------

def compute_trend(
    dataset: dict[str, Any],
    start: str,
    end: str,
) -> dict[str, Any]:
    """
    Berechnet den linearen Trend eines Klimadatensatzes über scipy.stats.linregress.

    Der Trend wird in Einheit pro Jahrzehnt angegeben, da das für Klimadaten
    die übliche Darstellungsform ist.

    Args:
        dataset: Normalisierter Datensatz (Data Pipeline Format).
        start:   Startdatum des Analysezeitraums (ISO, z. B. '1980-01-01').
        end:     Enddatum des Analysezeitraums (ISO, z. B. '2024-12-31').

    Returns:
        TrendResult-Dict gemäß API-Vertrag (api_contracts.md).

    Raises:
        ValueError: Wenn weniger als 3 gültige Datenpunkte im Zeitraum vorhanden.
    """
    df = _to_dataframe(dataset)
    df = _filter_period(df, start, end)
    t, y = _clean(df)

    if len(t) < 3:
        raise ValueError(
            f"Zu wenige Datenpunkte für Trendberechnung: {len(t)} "
            f"(Minimum: 3) im Zeitraum {start} – {end}."
        )

    slope, intercept, r_value, p_value, std_err = stats.linregress(t, y)

    # Steigung pro Jahr → pro Jahrzehnt
    trend_per_decade = round(slope * 10, 6)
    r_squared = round(r_value ** 2, 6)

    # Interpretation
    if p_value > 0.05:
        interpretation = "Kein statistisch signifikanter Trend (p > 0.05)"
    elif trend_per_decade > 0:
        interpretation = "Statistisch signifikanter positiver Trend"
    else:
        interpretation = "Statistisch signifikanter negativer Trend"

    variable = dataset.get("variable", "unbekannt")
    unit = dataset.get("unit", "")

    logger.info(
        "Trend berechnet: %s | %s/Jahrzehnt | R²=%.3f | p=%.4f",
        variable, trend_per_decade, r_squared, p_value,
    )

    return {
        "variable": variable,
        "trend_per_decade": trend_per_decade,
        "unit": f"{unit}/Jahrzehnt",
        "r_squared": r_squared,
        "p_value": round(p_value, 6),
        "std_err": round(std_err * 10, 6),  # Standardfehler ebenfalls pro Jahrzehnt
        "period": {"start": start, "end": end},
        "n_points": int(len(t)),
        "interpretation": interpretation,
    }


# ---------------------------------------------------------------------------
# CA-02: Pearson-Korrelation
# ---------------------------------------------------------------------------

def compute_correlation(
    dataset_a: dict[str, Any],
    dataset_b: dict[str, Any],
    start: str,
    end: str,
) -> dict[str, Any]:
    """
    Berechnet den Pearson-Korrelationskoeffizienten zwischen zwei Klimavariablen.

    Die Datensätze werden zunächst auf den gemeinsamen Zeitraum und gemeinsame
    Datenpunkte (inner join über Datum) reduziert, bevor die Korrelation
    berechnet wird.

    Args:
        dataset_a: Normalisierter Datensatz Variable A.
        dataset_b: Normalisierter Datensatz Variable B.
        start:     Startdatum (ISO).
        end:       Enddatum (ISO).

    Returns:
        CorrelationResult-Dict gemäß API-Vertrag.

    Raises:
        ValueError: Wenn weniger als 3 gemeinsame Datenpunkte vorhanden sind.
    """
    df_a = _filter_period(_to_dataframe(dataset_a), start, end)["value"]
    df_b = _filter_period(_to_dataframe(dataset_b), start, end)["value"]

    # Gemeinsame Datenpunkte (inner join über Datum)
    combined = pd.concat(
        [df_a.rename("a"), df_b.rename("b")], axis=1, join="inner"
    ).dropna()

    if len(combined) < 3:
        raise ValueError(
            f"Zu wenige gemeinsame Datenpunkte für Korrelation: {len(combined)} "
            f"(Minimum: 3) im Zeitraum {start} – {end}."
        )

    r, p_value = stats.pearsonr(combined["a"], combined["b"])

    var_a = dataset_a.get("variable", "variable_a")
    var_b = dataset_b.get("variable", "variable_b")

    logger.info(
        "Korrelation berechnet: %s ↔ %s | r=%.3f | p=%.4f | n=%d",
        var_a, var_b, r, p_value, len(combined),
    )

    return {
        "variable_a": var_a,
        "variable_b": var_b,
        "correlation": round(r, 6),
        "method": "pearson",
        "p_value": round(p_value, 6),
        "n_points": int(len(combined)),
        "period": {"start": start, "end": end},
        "note": "Korrelation bedeutet keine Kausalität. Weitere Analyse notwendig.",
    }


# ---------------------------------------------------------------------------
# CA-03: Anomalieerkennung
# ---------------------------------------------------------------------------

def compute_anomalies(
    dataset: dict[str, Any],
    start: str,
    end: str,
    ref_start: str = "1951-01-01",
    ref_end: str = "1980-12-31",
) -> dict[str, Any]:
    """
    Berechnet Anomalien gegenüber einem Referenzzeitraum.

    Eine Anomalie ist die Abweichung eines Wertes vom Mittelwert des
    Referenzzeitraums. Diese Methode entspricht der von NASA GISS verwendeten
    Vorgehensweise für GISTEMP-Temperaturen.

    Args:
        dataset:   Normalisierter Datensatz.
        start:     Startdatum des Analysezeitraums (ISO).
        end:       Enddatum des Analysezeitraums (ISO).
        ref_start: Beginn des Referenzzeitraums (Standard: 1951-01-01).
        ref_end:   Ende des Referenzzeitraums (Standard: 1980-12-31).

    Returns:
        AnomalyResult-Dict gemäß API-Vertrag.

    Raises:
        ValueError: Wenn Referenzzeitraum keine gültigen Daten enthält.
    """
    df = _to_dataframe(dataset)

    # Referenzmittelwert berechnen
    ref_df = _filter_period(df, ref_start, ref_end)["value"].dropna()

    if len(ref_df) == 0:
        raise ValueError(
            f"Keine gültigen Daten im Referenzzeitraum {ref_start} – {ref_end}."
        )

    ref_mean = float(ref_df.mean())

    # Analysezeitraum filtern
    analysis_df = _filter_period(df, start, end)

    anomalies = []
    for date, row in analysis_df.iterrows():
        val = row["value"]
        if pd.isna(val):
            continue
        anomalies.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(float(val), 6),
            "anomaly": round(float(val) - ref_mean, 6),
        })

    variable = dataset.get("variable", "unbekannt")
    unit = dataset.get("unit", "")

    logger.info(
        "Anomalien berechnet: %s | Referenzmittel=%.4f | n=%d Punkte",
        variable, ref_mean, len(anomalies),
    )

    return {
        "variable": variable,
        "unit": unit,
        "reference_period": {
            "start": ref_start,
            "end": ref_end,
            "mean": round(ref_mean, 6),
        },
        "anomalies": anomalies,
        "n_points": len(anomalies),
    }


# ---------------------------------------------------------------------------
# CA-04: Gleitender Mittelwert
# ---------------------------------------------------------------------------

def compute_moving_average(
    dataset: dict[str, Any],
    start: str,
    end: str,
    window_months: int = 12,
) -> dict[str, Any]:
    """
    Berechnet den gleitenden Mittelwert (zentriert) über ein konfigurierbares
    Zeitfenster in Monaten.

    Der gleitende Mittelwert glättet saisonale Schwankungen und macht
    langfristige Trends in Klimazeitreihen sichtbar.

    Args:
        dataset:       Normalisierter Datensatz.
        start:         Startdatum des Analysezeitraums (ISO).
        end:           Enddatum des Analysezeitraums (ISO).
        window_months: Fenstergröße in Monaten (Standard: 12 für Jahresmittel).

    Returns:
        Dict mit geglätteten Werten und Metadaten.

    Raises:
        ValueError: Wenn window_months < 1 oder zu wenige Datenpunkte.
    """
    if window_months < 1:
        raise ValueError(f"window_months muss >= 1 sein, erhalten: {window_months}")

    df = _filter_period(_to_dataframe(dataset), start, end)
    series = df["value"]

    if len(series.dropna()) < window_months:
        raise ValueError(
            f"Zu wenige Datenpunkte ({len(series.dropna())}) für "
            f"Fenstergröße {window_months}."
        )

    # Zentrierter gleitender Mittelwert (center=True vermeidet zeitlichen Versatz)
    smoothed = series.rolling(window=window_months, center=True, min_periods=1).mean()

    result_points = []
    for date, val in smoothed.items():
        if pd.isna(val):
            continue
        result_points.append({
            "date": date.strftime("%Y-%m-%d"),
            "value": round(float(val), 6),
        })

    variable = dataset.get("variable", "unbekannt")
    unit = dataset.get("unit", "")

    logger.info(
        "Gleitender Mittelwert berechnet: %s | Fenster=%d Monate | n=%d Punkte",
        variable, window_months, len(result_points),
    )

    return {
        "variable": variable,
        "unit": unit,
        "window_months": window_months,
        "period": {"start": start, "end": end},
        "data": result_points,
        "n_points": len(result_points),
    }


# ---------------------------------------------------------------------------
# CA-09 (Vorbereitung Phase 2): AnalysisSummary für AI Explanation Team
# ---------------------------------------------------------------------------

def build_analysis_summary(
    dataset: dict[str, Any],
    start: str,
    end: str,
    ref_start: str = "1951-01-01",
    ref_end: str = "1980-12-31",
) -> dict[str, Any]:
    """
    Erstellt eine Zusammenfassung aller Analyseergebnisse für das AI Explanation Team.

    Diese Funktion fasst Trend, Anomalien und gleitenden Mittelwert in einem
    einzigen Dict zusammen, das als Input für die Artikelgenerierung genutzt wird.
    Das genaue Format wird in Phase 2 gemeinsam mit dem AI Explanation Team
    finalisiert (CA-09).

    Args:
        dataset:   Normalisierter Datensatz.
        start:     Startdatum des Analysezeitraums (ISO).
        end:       Enddatum des Analysezeitraums (ISO).
        ref_start: Beginn des Referenzzeitraums.
        ref_end:   Ende des Referenzzeitraums.

    Returns:
        AnalysisSummary-Dict (vorläufiges Format, Phase-2-Review ausstehend).
    """
    trend = compute_trend(dataset, start, end)
    anomalies_result = compute_anomalies(dataset, start, end, ref_start, ref_end)
    moving_avg = compute_moving_average(dataset, start, end)

    # Letzte Anomalie und Maximum für Zusammenfassung
    anomaly_values = [a["anomaly"] for a in anomalies_result["anomalies"]]
    latest_anomaly = anomaly_values[-1] if anomaly_values else None
    max_anomaly = max(anomaly_values) if anomaly_values else None

    return {
        "schema_version": "0.1",  # Wird in CA-09 / Phase 2 auf 1.0 angehoben
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": dataset.get("source", "unbekannt"),
        "variable": dataset.get("variable", "unbekannt"),
        "unit": dataset.get("unit", ""),
        "period": {"start": start, "end": end},
        "reference_period": {"start": ref_start, "end": ref_end},
        "trend": {
            "per_decade": trend["trend_per_decade"],
            "r_squared": trend["r_squared"],
            "p_value": trend["p_value"],
            "interpretation": trend["interpretation"],
        },
        "anomalies": {
            "latest": latest_anomaly,
            "maximum": max_anomaly,
            "reference_mean": anomalies_result["reference_period"]["mean"],
        },
        "smoothed_series": moving_avg["data"],
        "metadata": dataset.get("metadata", {}),
    }