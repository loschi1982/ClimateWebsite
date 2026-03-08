# Data Ingestion Module
# Verantwortlich für den Abruf, die Validierung und Normalisierung
# von Klimadaten aus externen wissenschaftlichen Quellen.

from .nasa_client import NasaGissClient
from .noaa_client import NoaaClient
from .nsidc_client import NsidcClient
from .cache import DataCache
from .validator import DataValidator
from .normalizer import DataNormalizer

__all__ = [
    "NasaGissClient",
    "NoaaClient",
    "NsidcClient",
    "DataCache",
    "DataValidator",
    "DataNormalizer",
]