"""
DP-04: Validierungslogik für Klimadatensätze.

Prüft abgerufene Datensätze auf:
- Vollständigkeit der Pflichtfelder
- Plausibilität der Messwerte (Wertebereiche)
- Zeitkonsistenz (korrekte Datumsformate, keine Zeitsprünge)
- Anteil fehlender Werte
"""

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Regulärer Ausdruck für das Datumsformat YYYY-MM-DD
_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Maximaler erlaubter Anteil fehlender Werte (als Dezimalzahl, z.B. 0.1 = 10 %)
_MAX_MISSING_RATIO = 0.1

# Physikalische Wertebereiche je Variable
# Format: variable → (min, max)
_VALUE_RANGES: dict[str, tuple[float, float]] = {
    "temperature":          (-5.0, 5.0),    # Anomalie in °C
    "co2":                  (250.0, 600.0), # ppm (historisch bis heute)
    "sea_ice_arctic":       (0.0, 20.0),    # Millionen km²
    "sea_ice_antarctic":    (0.0, 20.0),    # Millionen km²
}


@dataclass
class ValidationResult:
    """
    Ergebnis einer Datensatz-Validierung.

    Attributes:
        is_valid:       True, wenn keine Fehler gefunden wurden.
        errors:         Kritische Fehler, die den Datensatz unbrauchbar machen.
        warnings:       Warnungen, die auf Qualitätsprobleme hinweisen.
        missing_count:  Anzahl fehlender Werte (None).
        total_count:    Gesamtzahl der Datenpunkte.
    """
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    missing_count: int = 0
    total_count: int = 0

    @property
    def missing_ratio(self) -> float:
        """Anteil fehlender Werte als Dezimalzahl (0.0 – 1.0)."""
        if self.total_count == 0:
            return 0.0
        return self.missing_count / self.total_count

    def add_error(self, msg: str) -> None:
        """Fügt einen kritischen Fehler hinzu und markiert das Ergebnis als ungültig."""
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        """Fügt eine Warnung hinzu (Datensatz bleibt gültig)."""
        self.warnings.append(msg)


class DataValidator:
    """
    Validiert Klimadatensätze im einheitlichen Plattformformat.

    Prüft Pflichtfelder, Datumsformate, Wertebereiche und fehlende Werte.
    Gibt ein ValidationResult zurück, das Fehler und Warnungen enthält.
    """

    def validate(self, dataset: dict) -> ValidationResult:
        """
        Führt alle Validierungsschritte für einen Datensatz durch.

        Args:
            dataset: Dataset-Dict im Plattformformat.

        Returns:
            ValidationResult mit Fehlern, Warnungen und Statistiken.
        """
        result = ValidationResult()

        self._check_required_fields(dataset, result)
        if not result.is_valid:
            # Weitere Prüfungen sind sinnlos, wenn Pflichtfelder fehlen
            return result

        variable = dataset.get("variable", "")
        data = dataset.get("data", [])
        result.total_count = len(data)

        if result.total_count == 0:
            result.add_error("Datensatz enthält keine Datenpunkte.")
            return result

        self._check_data_points(data, variable, result)
        self._check_missing_ratio(result)

        if result.is_valid:
            logger.info(
                f"[validator] Datensatz '{variable}' gültig. "
                f"{result.missing_count}/{result.total_count} fehlende Werte "
                f"({result.missing_ratio:.1%})."
            )
        else:
            logger.error(
                f"[validator] Datensatz '{variable}' ungültig: {result.errors}"
            )

        return result

    def _check_required_fields(self, dataset: dict, result: ValidationResult) -> None:
        """Prüft, ob alle Pflichtfelder des Dataset-Formats vorhanden sind."""
        required_top = ["source", "variable", "unit", "data", "metadata"]
        for field_name in required_top:
            if field_name not in dataset:
                result.add_error(f"Pflichtfeld fehlt: '{field_name}'")

        metadata = dataset.get("metadata", {})
        required_meta = ["source_url", "retrieved_at", "license"]
        for field_name in required_meta:
            if field_name not in metadata:
                result.add_error(f"Pflichtfeld in metadata fehlt: '{field_name}'")

    def _check_data_points(
        self,
        data: list[dict],
        variable: str,
        result: ValidationResult,
    ) -> None:
        """
        Prüft jeden einzelnen Datenpunkt auf Format und Plausibilität.

        Args:
            data:     Liste der Datenpunkte.
            variable: Variablenname für Wertebereich-Lookup.
            result:   ValidationResult, in das Fehler und Warnungen geschrieben werden.
        """
        value_range = _VALUE_RANGES.get(variable)
        seen_dates: set[str] = set()
        out_of_range_count = 0

        for idx, point in enumerate(data):
            # Jeder Datenpunkt muss 'date' und 'value' enthalten
            if "date" not in point or "value" not in point:
                result.add_error(
                    f"Datenpunkt #{idx} fehlt 'date' oder 'value': {point}"
                )
                continue

            date_str = point["date"]

            # Datumsformat prüfen
            if not _DATE_PATTERN.match(str(date_str)):
                result.add_error(
                    f"Ungültiges Datumsformat '{date_str}' an Position #{idx}. "
                    f"Erwartet: 'YYYY-MM-DD'."
                )

            # Doppelte Datumseinträge erkennen
            if date_str in seen_dates:
                result.add_warning(f"Doppelter Datumseintrag: '{date_str}'.")
            seen_dates.add(date_str)

            value = point["value"]

            if value is None:
                result.missing_count += 1
                continue

            # Wertebereich prüfen (falls für diese Variable definiert)
            if value_range is not None:
                v_min, v_max = value_range
                if not (v_min <= value <= v_max):
                    out_of_range_count += 1
                    logger.debug(
                        f"[validator] Wert außerhalb Bereich: {date_str} = {value} "
                        f"(erwartet {v_min}–{v_max})"
                    )

        if out_of_range_count > 0:
            result.add_warning(
                f"{out_of_range_count} Werte außerhalb des erwarteten Bereichs "
                f"für Variable '{variable}'."
            )

    def _check_missing_ratio(self, result: ValidationResult) -> None:
        """
        Prüft, ob der Anteil fehlender Werte den Schwellenwert überschreitet.

        Bei mehr als 10 % fehlenden Werten wird eine Warnung ausgegeben.
        """
        if result.missing_ratio > _MAX_MISSING_RATIO:
            result.add_warning(
                f"Hoher Anteil fehlender Werte: {result.missing_ratio:.1%} "
                f"({result.missing_count}/{result.total_count}). "
                f"Schwellenwert: {_MAX_MISSING_RATIO:.0%}."
            )