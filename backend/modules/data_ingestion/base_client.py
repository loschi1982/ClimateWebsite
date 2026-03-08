"""
Basisklasse für alle Datenquellen-Clients.

Definiert die gemeinsame Schnittstelle und stellt
grundlegende HTTP-Funktionalität bereit.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import requests

logger = logging.getLogger(__name__)

# Netzwerk-Einstellungen
REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 3


class DatasetDict(dict):
    """
    Typalias für das einheitliche Dataset-Format der Plattform.
    Alle Clients geben Dicts in diesem Format zurück.
    """
    pass


class BaseClient(ABC):
    """
    Abstrakte Basisklasse für alle Datenquellen-Clients.

    Jeder Client erbt von dieser Klasse und implementiert
    die Methoden fetch() und parse().
    """

    # Zu überschreiben in der Unterklasse
    SOURCE_ID: str = ""
    SOURCE_NAME: str = ""
    SOURCE_URL: str = ""
    LICENSE: str = ""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KlimaplattformBot/1.0 (https://github.com/loschi1982/ClimateWebsite)"
        })

    def _get(self, url: str, **kwargs) -> requests.Response:
        """
        Führt einen HTTP-GET-Request mit Timeout und Fehlerbehandlung durch.

        Args:
            url: Die abzurufende URL.
            **kwargs: Weitere Argumente für requests.get().

        Returns:
            Das Response-Objekt bei Erfolg.

        Raises:
            requests.exceptions.Timeout: Bei Zeitüberschreitung.
            requests.exceptions.HTTPError: Bei HTTP-Fehlerstatuscodes (4xx, 5xx).
            requests.exceptions.RequestException: Bei sonstigen Netzwerkfehlern.
        """
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        logger.info(f"[{self.SOURCE_ID}] Abruf von: {url}")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response

    def _now_iso(self) -> str:
        """Gibt den aktuellen Zeitstempel im ISO-8601-Format (UTC) zurück."""
        return datetime.now(timezone.utc).isoformat()

    def _build_dataset(
        self,
        variable: str,
        unit: str,
        data: list[dict],
        reference_period: Optional[str] = None,
    ) -> DatasetDict:
        """
        Erstellt ein Dataset-Dict im einheitlichen Plattformformat.

        Args:
            variable: Bezeichner der Klimavariablen (z.B. 'temperature').
            unit: Einheit der Messwerte (z.B. '°C').
            data: Liste von {'date': 'YYYY-MM-DD', 'value': float} Dicts.
            reference_period: Optionaler Referenzzeitraum (z.B. '1951-1980').

        Returns:
            Dataset-Dict im Plattformformat.
        """
        dataset = DatasetDict(
            source=self.SOURCE_ID,
            variable=variable,
            unit=unit,
            data=data,
            metadata={
                "source_name": self.SOURCE_NAME,
                "source_url": self.SOURCE_URL,
                "retrieved_at": self._now_iso(),
                "license": self.LICENSE,
            },
        )
        if reference_period:
            dataset["reference_period"] = reference_period
        return dataset

    @abstractmethod
    def fetch(self, start: str, end: str) -> DatasetDict:
        """
        Ruft Daten für den angegebenen Zeitraum ab und gibt ein
        normalisiertes Dataset-Dict zurück.

        Args:
            start: Startdatum im Format 'YYYY-MM-DD'.
            end: Enddatum im Format 'YYYY-MM-DD'.

        Returns:
            Normalisiertes Dataset-Dict.
        """
        ...