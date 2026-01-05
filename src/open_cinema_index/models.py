from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True)
    kind = Column(String, nullable=True)
    runtime_minutes = Column(Integer, nullable=True)
    original_language = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    titles = relationship("Title", back_populates="film", cascade="all, delete-orphan")
    releases = relationship("Release", back_populates="film", cascade="all, delete-orphan")
    credits = relationship("Credit", back_populates="film", cascade="all, delete-orphan")
    identifiers = relationship("Identifier", back_populates="film", cascade="all, delete-orphan")
    assertions = relationship("MetadataAssertion", back_populates="film", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="film", cascade="all, delete-orphan")


class Title(Base):
    __tablename__ = "titles"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    language = Column(String, nullable=True)
    region = Column(String, nullable=True)
    is_original = Column(Boolean, default=False)
    is_primary = Column(Boolean, default=False)
    source = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)  # Optional confidence score 0-100

    __table_args__ = (UniqueConstraint("film_id", "title", "language", "region", name="uq_title_film_details"),)

    film = relationship("Film", back_populates="titles")


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    release_type = Column(String, nullable=True)  # theatrical, festival, home_video
    region = Column(String, nullable=True)
    date = Column(Date, nullable=True)
    runtime_minutes = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("film_id", "release_type", "region", "date", name="uq_release_film_details"),)

    film = relationship("Film", back_populates="releases")


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=True)
    death_date = Column(Date, nullable=True)
    source = Column(String, nullable=True)

    credits = relationship("Credit", back_populates="person", cascade="all, delete-orphan")
    alternate_names = relationship("AlternateName", back_populates="person", cascade="all, delete-orphan")


class AlternateName(Base):
    __tablename__ = "alternate_names"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    source = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("person_id", "name", name="uq_alternate_name_person"),)

    person = relationship("Person", back_populates="alternate_names")


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=True)
    order = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    source = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("film_id", "person_id", "role", name="uq_credit_film_person_role"),)

    film = relationship("Film", back_populates="credits")
    person = relationship("Person", back_populates="credits")


class Identifier(Base):
    __tablename__ = "identifiers"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    scheme = Column(String, nullable=False)  # imdb, tmdb, wikidata
    value = Column(String, nullable=False)
    source = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint("scheme", "value", name="uq_identifier_scheme_value"),)

    film = relationship("Film", back_populates="identifiers")


class MetadataAssertion(Base):
    __tablename__ = "metadata_assertions"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # genre, keyword, synopsis, rating
    value = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    source = Column(String, nullable=True)
    confidence = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint("film_id", "type", "value", "language", name="uq_metadata_assertion_details"),)

    film = relationship("Film", back_populates="assertions")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("films.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)  # poster, backdrop, trailer
    url = Column(String, nullable=False)
    language = Column(String, nullable=True)
    region = Column(String, nullable=True)
    source = Column(String, nullable=True)
    license = Column(String, nullable=True)
    checksum = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("film_id", "url", name="uq_asset_film_url"),)

    film = relationship("Film", back_populates="assets")


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    kind = Column(String, nullable=True)  # rest, graphql, file
    base_url = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    last_run_started_at = Column(DateTime(timezone=True), nullable=True)
    last_run_completed_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    credentials = relationship("DataSourceCredential", back_populates="data_source", cascade="all, delete-orphan")
    rate_limits = relationship("DataSourceRateLimit", back_populates="data_source", cascade="all, delete-orphan")
    refresh_policy = relationship(
        "DataSourceRefreshPolicy",
        back_populates="data_source",
        uselist=False,
        cascade="all, delete-orphan",
    )
    capabilities = relationship("DataSourceCapability", back_populates="data_source", cascade="all, delete-orphan")
    runs = relationship("DataSourceRun", back_populates="data_source", cascade="all, delete-orphan")


class DataSourceCredential(Base):
    __tablename__ = "data_source_credentials"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String, nullable=False)  # api_key, oauth, x-auth-token
    token = Column(String, nullable=False)  # Encrypted/hashed secret blob
    expired_at = Column(DateTime(timezone=True), nullable=True)
    rotated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("data_source_id", "kind", "token", name="uq_data_source_credential_unique"),)

    data_source = relationship("DataSource", back_populates="credentials")

    @property
    def is_expired(self) -> bool:
        if not self.expired_at:
            return False
        expired_at = self.expired_at
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)
        return bool(expired_at <= datetime.now(timezone.utc))


class DataSourceRateLimit(Base):
    __tablename__ = "data_source_rate_limits"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    window_seconds = Column(Integer, nullable=False)  # e.g., 60, 3600
    max_calls = Column(Integer, nullable=False)
    burst = Column(Integer, nullable=True)
    retry_delay_seconds = Column(Integer, nullable=True)

    __table_args__ = (UniqueConstraint("data_source_id", "window_seconds", name="uq_data_source_rate_limit_window"),)

    data_source = relationship("DataSource", back_populates="rate_limits")


class DataSourceRefreshPolicy(Base):
    __tablename__ = "data_source_refresh_policies"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    default_refresh_interval_minutes = Column(Integer, nullable=True)
    max_record_age_days = Column(Integer, nullable=True)
    incremental_cursor_field = Column(String, nullable=True)
    supports_webhook = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("data_source_id", name="uq_data_source_refresh_policy_unique"),)

    data_source = relationship("DataSource", back_populates="refresh_policy")


class DataSourceCapability(Base):
    __tablename__ = "data_source_capabilities"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    capability = Column(String, nullable=False)  # films, people, assets, updates
    endpoint_path = Column(String, nullable=True)  # e.g., /movie/{id} or ?query={query}
    payload_mapping = Column(Text, nullable=True)  # JSON mapping of external fields to OCI fields

    __table_args__ = (UniqueConstraint("data_source_id", "capability", name="uq_data_source_capability_unique"),)

    data_source = relationship("DataSource", back_populates="capabilities")


class DataSourceRun(Base):
    __tablename__ = "data_source_runs"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="started")  # started, success, failed
    error = Column(Text, nullable=True)
    items_fetched = Column(Integer, nullable=True)
    items_processed = Column(Integer, nullable=True)

    data_source = relationship("DataSource", back_populates="runs")

    @property
    def duration(self) -> timedelta:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return timedelta()
