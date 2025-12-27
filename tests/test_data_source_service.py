from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from open_cinema_index.models import (
    Base,
    DataSource,
    DataSourceCredential,
    DataSourceRateLimit,
    DataSourceRun,
)
from open_cinema_index.services.data_sources import (
    DataSourceDisabledError,
    DataSourceNotConfiguredError,
    DataSourceService,
    RateLimitExceededError,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


def test_prepare_fetch_creates_run_and_returns_plan(session):
    source = DataSource(name="tmdb")
    session.add(source)
    session.commit()

    service = DataSourceService(session)
    plan = service.prepare_fetch("tmdb")

    assert plan.data_source.name == "tmdb"
    assert plan.run.status == "started"
    assert session.query(DataSourceRun).count() == 1


def test_prepare_fetch_requires_enabled_source(session):
    source = DataSource(name="imdb", enabled=False)
    session.add(source)
    session.commit()

    service = DataSourceService(session)
    with pytest.raises(DataSourceDisabledError):
        service.prepare_fetch("imdb")


def test_prepare_fetch_enforces_rate_limits(session):
    source = DataSource(name="wikidata")
    session.add(source)
    session.commit()

    limit = DataSourceRateLimit(
        data_source_id=source.id,
        window_seconds=60,
        max_calls=1,
    )
    session.add(limit)
    session.commit()

    service = DataSourceService(session)
    service.prepare_fetch("wikidata")

    with pytest.raises(RateLimitExceededError):
        service.prepare_fetch("wikidata")


def test_prepare_fetch_picks_active_credential(session):
    source = DataSource(name="archive")
    session.add(source)
    session.commit()

    valid_cred = DataSourceCredential(
        data_source_id=source.id,
        kind="api_key",
        token="valid",
        expired_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    expired_cred = DataSourceCredential(
        data_source_id=source.id,
        kind="api_key",
        token="expired",
        expired_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    session.add_all([valid_cred, expired_cred])
    session.commit()

    service = DataSourceService(session)
    plan = service.prepare_fetch("archive")

    assert plan.credential.token == "valid"


def test_prepare_fetch_unknown_source(session):
    service = DataSourceService(session)
    with pytest.raises(DataSourceNotConfiguredError):
        service.prepare_fetch("missing")


def test_rate_limits_are_isolated_per_source(session):
    tmdb = DataSource(name="tmdb")
    wikidata = DataSource(name="wikidata")
    session.add_all([tmdb, wikidata])
    session.commit()

    tmdb_limit = DataSourceRateLimit(
        data_source_id=tmdb.id,
        window_seconds=60,
        max_calls=1,
    )
    wikidata_limit = DataSourceRateLimit(
        data_source_id=wikidata.id,
        window_seconds=60,
        max_calls=2,
    )
    session.add_all([tmdb_limit, wikidata_limit])
    session.commit()

    service = DataSourceService(session)
    service.prepare_fetch("tmdb")
    with pytest.raises(RateLimitExceededError):
        service.prepare_fetch("tmdb")

    # Wikidata has its own window and quota; the TMDB calls above should not affect it.
    service.prepare_fetch("wikidata")
    service.prepare_fetch("wikidata")