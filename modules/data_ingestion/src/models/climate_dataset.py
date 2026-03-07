# ─────────────────────────────────────────────────────────────────────────────
# Was macht diese Datei?
# Definiert die Datenmodelle (Schemas) für alle Klimadaten im Projekt.
# Ein "Datenmodell" legt fest, wie Daten aussehen müssen: welche Felder
# vorhanden sein müssen, welchen Typ sie haben, und ob sie optional sind.
#
# Wir nutzen dafür "Pydantic" — eine Python-Bibliothek, die automatisch
# überprüft, ob die Daten dem gewünschten Format entsprechen.
#
# Team: Data Pipeline Team | Branch: feature/data-pipeline
# ─────────────────────────────────────────────────────────────────────────────

# Was ist Pydantic?
# Pydantic ist eine Bibliothek, die Datenvalidierung erleichtert.
# Wenn wir ein Pydantic-Modell definieren, überprüft Python automatisch,
# ob eingehende Daten korrekt sind — z.B. ob ein Datum wirklich ein Datum ist.
from pydantic import BaseModel, Field, HttpUrl

# datetime: Ermöglicht die Arbeit mit Datum und Uhrzeit
# Optional: Kennzeichnet Felder, die auch leer (None) sein dürfen
# Literal: Erlaubt nur bestimmte festgelegte Werte für ein Feld
from datetime import datetime
from typing import Optional, Literal, List

# uuid: Erzeugt eindeutige IDs (z.B. "3f8a2b1c-...")
# Eine UUID ist eine zufällige ID, die garantiert weltweit einmalig ist.
import uuid


# ─────────────────────────────────────────────────────────────────────────────
# Modell 1: DataPoint
# Ein einzelner Messwert — z.B. "Globale Temperaturabweichung im Januar 1950"
# ─────────────────────────────────────────────────────────────────────────────
class DataPoint(BaseModel):
    """
    Repräsentiert einen einzelnen Klimamesspunkt.

    Was ist ein Messpunkt?
    Ein Messpunkt ist ein einzelner Wert zu einem bestimmten Zeitpunkt.
    Beispiel: Die globale Durchschnittstemperatur war im Juli 2023
    um +1.2°C höher als im Referenzzeitraum 1951–1980.

    Warum brauchen wir quality_flag?
    Nicht alle Messdaten sind gleich zuverlässig. Manche Daten wurden
    nachträglich korrigiert oder geschätzt. Das quality_flag hilft uns,
    unsichere Daten zu markieren.
    """

    # timestamp: Wann wurde gemessen? (ISO 8601 Format, z.B. "2023-07-01T00:00:00")
    timestamp: datetime = Field(
        description="Zeitpunkt der Messung im ISO-8601-Format"
    )

    # value: Der eigentliche Messwert (z.B. 1.2 für +1.2°C Abweichung)
    value: float = Field(
        description="Numerischer Messwert in der angegebenen Einheit"
    )

    # unit: Die Einheit des Messwerts (z.B. "°C" oder "ppm" für CO₂)
    unit: str = Field(
        description="Maßeinheit des Messwerts, z.B. '°C', 'ppm', 'm'"
    )

    # quality_flag: Gibt an, wie zuverlässig der Messwert ist
    # "good"     → Messung ist zuverlässig und geprüft
    # "estimated"→ Wert wurde aus anderen Daten berechnet/geschätzt
    # "suspect"  → Wert könnte fehlerhaft sein, bedarf Prüfung
    quality_flag: Literal["good", "estimated", "suspect"] = Field(
        default="good",
        description="Qualitätskennzeichnung: good | estimated | suspect"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Modell 2: SourceReference
# Beschreibt woher ein Datensatz stammt — wichtig für wissenschaftliche
# Nachvollziehbarkeit (Provenienz).
# ─────────────────────────────────────────────────────────────────────────────
class SourceReference(BaseModel):
    """
    Vollständige Quellenangabe für einen Klimadatensatz.

    Warum brauchen wir das?
    In der Wissenschaft ist es essenziell zu wissen, woher Daten stammen.
    Nur so können Ergebnisse überprüft und reproduziert werden.
    Diese Klasse speichert alle Informationen, die für ein Literaturzitat
    oder eine Datenquelle benötigt werden.

    Was ist ein DOI?
    Ein DOI (Digital Object Identifier) ist ein permanenter Link zu einer
    wissenschaftlichen Publikation oder einem Datensatz.
    Beispiel: "10.7289/V5T72FNM" verweist auf einen NOAA-Datensatz.
    """

    # provider: Name der Organisation, die die Daten bereitstellt
    # z.B. "NASA", "NOAA", "Copernicus Climate Change Service"
    provider: str = Field(
        description="Name der datenproduzierenden Organisation"
    )

    # dataset_name: Offizieller Name des Datensatzes
    # z.B. "GISTEMP Surface Temperature Analysis v4"
    dataset_name: str = Field(
        description="Offizieller Name des Datensatzes"
    )

    # citation: Vollständige wissenschaftliche Zitierungsangabe
    citation: str = Field(
        description="Vollständige APA/Chicago-Zitierung für Veröffentlichungen"
    )

    # doi: Eindeutiger persistenter Identifier (Digital Object Identifier)
    # Optional, da nicht alle Datensätze einen DOI haben
    doi: Optional[str] = Field(
        default=None,
        description="DOI des Datensatzes, z.B. '10.7289/V5T72FNM'"
    )

    # url: Web-Adresse, unter der der Datensatz abgerufen werden kann
    url: HttpUrl = Field(
        description="Primäre URL der Datenquelle"
    )

    # license: Unter welcher Lizenz stehen die Daten?
    # z.B. "Public Domain", "CC BY 4.0"
    license: str = Field(
        default="Public Domain",
        description="Datenlizenz, z.B. 'Public Domain', 'CC BY 4.0'"
    )

    # accessed_at: Wann haben wir die Daten abgerufen?
    # Wichtig, da Daten sich online ändern können.
    accessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Zeitpunkt des letzten Datenabrufs (UTC)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Modell 3: ClimateDataset
# Ein vollständiger Klimadatensatz — enthält Metadaten und alle Messpunkte.
# ─────────────────────────────────────────────────────────────────────────────
class ClimateDataset(BaseModel):
    """
    Ein kompletter Klimadatensatz mit Metadaten und Messwerten.

    Was ist ein Klimadatensatz?
    Ein Datensatz fasst alle Messwerte einer bestimmten Klimavariable
    (z.B. globale Oberflächentemperatur) aus einer bestimmten Quelle
    (z.B. NASA GISS) zusammen.

    Warum haben wir id und dataset_id?
    - id: interne Datenbank-ID (automatisch generiert, eindeutig)
    - dataset_id: menschenlesbarer Bezeichner, z.B. "nasa_giss_surface_temp_v4"
    """

    # id: Interne eindeutige ID (wird automatisch generiert)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Interne UUID des Datensatzes (automatisch generiert)"
    )

    # dataset_id: Menschenlesbarer Bezeichner für den Datensatz
    # Konvention: [quelle]_[variable]_[version], z.B. "nasa_giss_surface_temp_v4"
    dataset_id: str = Field(
        description="Menschenlesbarer Bezeichner, z.B. 'nasa_giss_surface_temp_v4'"
    )

    # variable: Was wird gemessen?
    # z.B. "surface_temperature_anomaly", "co2_concentration", "sea_level"
    variable: str = Field(
        description="Klimavariable, z.B. 'surface_temperature_anomaly'"
    )

    # description: Kurze Erklärung was dieser Datensatz darstellt
    description: str = Field(
        description="Kurzbeschreibung des Datensatzes in verständlicher Sprache"
    )

    # source: Vollständige Quellenangabe (siehe SourceReference oben)
    source: SourceReference = Field(
        description="Provenienzinformation — woher kommen diese Daten?"
    )

    # records: Liste aller Messpunkte in diesem Datensatz
    # Eine leere Liste ist erlaubt (Datensatz existiert, hat aber noch keine Daten)
    records: List[DataPoint] = Field(
        default_factory=list,
        description="Liste aller DataPoints dieses Datensatzes"
    )

    # temporal_coverage_start / _end: Zeitraum den der Datensatz abdeckt
    temporal_coverage_start: Optional[datetime] = Field(
        default=None,
        description="Frühester Zeitpunkt im Datensatz"
    )
    temporal_coverage_end: Optional[datetime] = Field(
        default=None,
        description="Spätester Zeitpunkt im Datensatz"
    )

    # record_count: Wie viele Datenpunkte enthält der Datensatz?
    # Wird automatisch berechnet.
    @property
    def record_count(self) -> int:
        """Gibt die Anzahl der Messwerte zurück."""
        return len(self.records)


# ─────────────────────────────────────────────────────────────────────────────
# Modell 4: IngestionJob
# Beschreibt einen Daten-Abruf-Vorgang (Job).
#
# Was ist ein "Job"?
# Wenn wir Daten von NASA abrufen, dauert das unter Umständen mehrere Minuten.
# Statt den Nutzer warten zu lassen, erstellen wir sofort einen "Job" und
# geben ihm eine ID zurück. Der Nutzer kann dann den Status abfragen.
# Das nennt man "asynchrone Verarbeitung".
# ─────────────────────────────────────────────────────────────────────────────
class IngestionJob(BaseModel):
    """
    Repräsentiert einen asynchronen Daten-Ingestion-Job.

    Was bedeutet "asynchron"?
    Asynchron bedeutet, dass eine Aufgabe im Hintergrund läuft,
    während der Nutzer bereits weiterarbeiten kann. Der Job hat
    einen Status (pending → running → completed/failed), den man
    jederzeit abfragen kann.
    """

    # job_id: Eindeutige ID des Jobs (zum späteren Nachschlagen)
    job_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Eindeutige Job-ID, z.B. 'a1b2c3d4-...'"
    )

    # source_id: Von welcher Quelle werden Daten abgerufen?
    # z.B. "nasa_giss", "noaa_global_temp"
    source_id: str = Field(
        description="ID der Datenquelle, z.B. 'nasa_giss'"
    )

    # status: Aktueller Stand des Jobs
    # "pending"   → Job wurde erstellt, läuft noch nicht
    # "running"   → Daten werden gerade abgerufen
    # "completed" → Erfolgreich abgeschlossen
    # "failed"    → Fehler aufgetreten (siehe error_message)
    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending",
        description="Job-Status: pending | running | completed | failed"
    )

    # started_at: Wann wurde der Job gestartet?
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Startzeitpunkt des Jobs (UTC)"
    )

    # completed_at: Wann wurde der Job beendet? (None = läuft noch)
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Endzeitpunkt des Jobs (UTC), None wenn noch nicht beendet"
    )

    # records_fetched: Wie viele Datenpunkte wurden abgerufen?
    records_fetched: Optional[int] = Field(
        default=None,
        description="Anzahl der erfolgreich abgerufenen Datenpunkte"
    )

    # dataset_id: ID des erzeugten Datensatzes nach erfolgreichem Abschluss
    dataset_id: Optional[str] = Field(
        default=None,
        description="ID des erzeugten ClimateDataset nach Abschluss"
    )

    # error_message: Fehlerbeschreibung, falls status == "failed"
    error_message: Optional[str] = Field(
        default=None,
        description="Fehlermeldung bei status='failed', sonst None"
    )

    # parameters: Optionale Parameter die beim Job-Start übergeben wurden
    # z.B. {"start_year": 1950, "end_year": 2025}
    parameters: Optional[dict] = Field(
        default=None,
        description="Start-Parameter des Jobs, z.B. {'start_year': 1950}"
    )