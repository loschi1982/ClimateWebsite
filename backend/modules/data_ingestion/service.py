"""
Service-Schicht des Data Ingestion Module.

Koordiniert den Datenabruf, die Validierung, Normalisierung und das Caching.
Wird von den API-Endpunkten aufgerufen.
Stellt auch die Quellen-Metadaten für den /sources-Endpunkt bereit.
"""

import logging

from .cache import DataCache
from .nasa_client import NasaGissClient
from .noaa_client import NoaaClient
from .nsidc_client import NsidcClient
from .normalizer import DataNormalizer
from .validator import DataValidator

logger = logging.getLogger(__name__)

# Registrierung aller verfügbaren Quellen und Variablen
# Format: (source_id, variable) → Client-Klasse und Abruf-Parameter
_SOURCE_REGISTRY = {
    ("nasa", "temperature"): {
        "client_cls": NasaGissClient,
        "fetch_kwargs": {},
    },
    ("noaa", "co2"): {
        "client_cls": NoaaClient,
        "fetch_kwargs": {},
    },
    ("nsidc", "sea_ice_arctic"): {
        "client_cls": NsidcClient,
        "fetch_kwargs": {"variable": "sea_ice_arctic"},
    },
    ("nsidc", "sea_ice_antarctic"): {
        "client_cls": NsidcClient,
        "fetch_kwargs": {"variable": "sea_ice_antarctic"},
    },
}

# Metadaten für den /data/sources Endpunkt
SOURCES_METADATA = [
    {
        "id": "nasa",
        "name": "NASA GISS",
        "variables": ["temperature"],
        "available_from": "1880-01-01",
        "update_frequency": "monthly",
    },
    {
        "id": "noaa",
        "name": "NOAA GML",
        "variables": ["co2"],
        "available_from": "1958-03-01",
        "update_frequency": "monthly",
    },
    {
        "id": "nsidc",
        "name": "NSIDC Sea Ice Index",
        "variables": ["sea_ice_arctic", "sea_ice_antarctic"],
        "available_from": "1978-10-01",
        "update_frequency": "monthly",
    },
]


class DataIngestionService:
    """
    Koordiniert den gesamten Datenabruf-Workflow:
    Abruf → Validierung → Normalisierung → Cache → Rückgabe

    Ist die zentrale Schnittstelle zwischen API-Endpunkten und den
    einzelnen Datenquellen-Clients.
    """

    def __init__(self, cache: DataCache | None = None):
        """
        Initialisiert den Service.

        Args:
            cache: DataCache-Instanz. Wird neu erstellt, wenn nicht angegeben.
        """
        self.cache = cache or DataCache()
        self.validator = DataValidator()
        self.normalizer = DataNormalizer()

    def get_dataset(
        self,
        source: str,
        variable: str,
        start: str,
        end: str,
        force_refresh: bool = False,
    ) -> dict:
        """
        Gibt einen Klimadatensatz für die angegebene Quelle und Variable zurück.

        Ablauf:
        1. Wenn Cache vorhanden und kein force_refresh: Cache zurückgeben
        2. Sonst: Daten von externer Quelle abrufen
        3. Normalisieren und validieren
        4. Im Cache speichern
        5. Auf gewünschten Zeitraum filtern und zurückgeben

        Args:
            source:        Quellen-ID (z.B. 'nasa').
            variable:      Variablenname (z.B. 'temperature').
            start:         Startdatum im Format 'YYYY-MM-DD'.
            end:           Enddatum im Format 'YYYY-MM-DD'.
            force_refresh: Falls True, wird der Cache ignoriert und neu abgerufen.

        Returns:
            Normalisiertes, gefiltertes Dataset-Dict im Plattformformat.

        Raises:
            ValueError: Wenn Quelle oder Variable unbekannt sind.
            RuntimeError: Wenn die Validierung kritische Fehler findet.
            requests.exceptions.RequestException: Bei Netzwerkfehlern.
        """
        key = (source, variable)
        if key not in _SOURCE_REGISTRY:
            raise ValueError(
                f"Unbekannte Kombination: source='{source}', variable='{variable}'. "
                f"Verfügbar: {list(_SOURCE_REGISTRY.keys())}"
            )

        # Cache-Treffer (wenn kein force_refresh)
        if not force_refresh and self.cache.is_cached(source, variable):
            logger.info(f"[service] Cache-Treffer für {source}/{variable}.")
            cached = self.cache.load_processed(source, variable)
            if cached:
                return self._filter_dataset(cached, start, end)

        # Externe Daten abrufen
        logger.info(f"[service] Abruf von externer Quelle: {source}/{variable}")
        registry_entry = _SOURCE_REGISTRY[key]
        client = registry_entry["client_cls"]()
        fetch_kwargs = registry_entry["fetch_kwargs"]

        # Vollständigen Datensatz abrufen (Filterung erst nach dem Caching)
        # Um den Cache sinnvoll nutzen zu können, fragen wir immer den vollen
        # verfügbaren Zeitraum ab. Die Filterung erfolgt danach.
        dataset = client.fetch(start="1800-01-01", end="2100-12-31", **fetch_kwargs)

        # Normalisieren
        dataset = self.normalizer.normalize(dataset)

        # Validieren
        validation = self.validator.validate(dataset)
        if not validation.is_valid:
            raise RuntimeError(
                f"Validierung fehlgeschlagen für {source}/{variable}: "
                f"{validation.errors}"
            )
        if validation.warnings:
            for w in validation.warnings:
                logger.warning(f"[service] Validierungswarnung: {w}")

        # Im Cache speichern
        self.cache.save_processed(dataset)

        # Auf gewünschten Zeitraum filtern
        return self._filter_dataset(dataset, start, end)

    def _filter_dataset(self, dataset: dict, start: str, end: str) -> dict:
        """
        Filtert die Datenpunkte eines Datensatzes auf einen Zeitraum.

        Gibt ein neues Dict zurück (der ursprüngliche Cache-Eintrag bleibt unverändert).

        Args:
            dataset: Vollständiges Dataset-Dict.
            start:   Startdatum inklusiv ('YYYY-MM-DD').
            end:     Enddatum inklusiv ('YYYY-MM-DD').

        Returns:
            Kopie des Dataset-Dicts mit gefilterten Datenpunkten.
        """
        filtered_data = [
            point for point in dataset.get("data", [])
            if start <= point["date"] <= end
        ]
        # Flache Kopie des Dicts mit gefilterten Daten
        result = {k: v for k, v in dataset.items() if k != "data"}
        result["data"] = filtered_data
        return result

    def get_sources(self) -> list[dict]:
        """
        Gibt die Metadaten aller verfügbaren Datenquellen zurück.

        Returns:
            Liste von Quellen-Metadaten-Dicts.
        """
        return SOURCES_METADATA