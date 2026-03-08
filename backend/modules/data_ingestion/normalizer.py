"""
Normalisierungslogik für Klimadatensätze.

Stellt sicher, dass alle Datenpunkte ein einheitliches Format haben:
- Datumsformat: 'YYYY-MM-DD'
- Werte: float oder None (keine anderen Typen)
- Sortierung: chronologisch aufsteigend
- Keine Duplikate

Hinweis: Inhalte werden NICHT verändert – nur Format und Typen werden vereinheitlicht.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Normalisiert die Datenpunkte eines Klimadatensatzes.

    Aufgaben:
    - Datumsformate vereinheitlichen (verschiedene Eingabeformate → 'YYYY-MM-DD')
    - Werte in float umwandeln (oder None belassen)
    - Chronologisch sortieren
    - Duplikate entfernen (bei Konflikten: erster Wert gewinnt)
    """

    # Unterstützte Eingabe-Datumsformate
    _DATE_FORMATS = [
        "%Y-%m-%d",   # Standard: 2024-01-01
        "%Y/%m/%d",   # Alternativ: 2024/01/01
        "%d.%m.%Y",   # Deutsch: 01.01.2024
        "%Y-%m",      # Nur Jahr-Monat: 2024-01 → wird zu 2024-01-01
    ]

    def normalize(self, dataset: dict) -> dict:
        """
        Normalisiert alle Datenpunkte im Dataset-Dict.

        Verändert die Datenpunkte in-place und gibt das aktualisierte
        Dataset-Dict zurück.

        Args:
            dataset: Dataset-Dict im Plattformformat.

        Returns:
            Normalisiertes Dataset-Dict (selbes Objekt, aktualisiert).
        """
        data = dataset.get("data", [])
        normalized = []
        seen_dates: set[str] = set()
        skipped = 0

        for point in data:
            date_str = self._normalize_date(point.get("date", ""))
            if date_str is None:
                logger.warning(
                    f"[normalizer] Datum '{point.get('date')}' konnte nicht "
                    f"normalisiert werden – Datenpunkt wird übersprungen."
                )
                skipped += 1
                continue

            # Duplikate entfernen (erster Wert gewinnt)
            if date_str in seen_dates:
                logger.debug(
                    f"[normalizer] Doppelter Eintrag für '{date_str}' – wird übersprungen."
                )
                skipped += 1
                continue
            seen_dates.add(date_str)

            value = self._normalize_value(point.get("value"))
            normalized.append({"date": date_str, "value": value})

        # Chronologisch sortieren
        normalized.sort(key=lambda r: r["date"])

        if skipped > 0:
            logger.info(
                f"[normalizer] {skipped} Datenpunkte übersprungen (Duplikate oder ungültige Daten)."
            )

        dataset["data"] = normalized
        return dataset

    def _normalize_date(self, raw: str) -> str | None:
        """
        Konvertiert ein Datum aus verschiedenen Formaten nach 'YYYY-MM-DD'.

        Args:
            raw: Datums-String in einem der unterstützten Formate.

        Returns:
            Normalisierter Datums-String ('YYYY-MM-DD') oder None bei Fehler.
        """
        raw = str(raw).strip()

        for fmt in self._DATE_FORMATS:
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None

    def _normalize_value(self, raw) -> float | None:
        """
        Konvertiert einen Rohwert in float oder None.

        None-Werte und ungültige Werte bleiben None.

        Args:
            raw: Rohwert (float, int, str oder None).

        Returns:
            float-Wert oder None.
        """
        if raw is None:
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            logger.warning(f"[normalizer] Ungültiger Wert '{raw}' → wird als None gespeichert.")
            return None