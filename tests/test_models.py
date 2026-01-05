from datetime import date, datetime

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from open_cinema_index.models import (
    AlternateName,
    Asset,
    Base,
    Credit,
    DataSource,
    DataSourceCapability,
    DataSourceCredential,
    DataSourceRateLimit,
    DataSourceRefreshPolicy,
    DataSourceRun,
    Film,
    Identifier,
    Person,
    Release,
    Title,
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


def test_create_film(session):
    film = Film(kind="movie", original_language="en")
    session.add(film)
    session.commit()

    saved_film = session.query(Film).first()
    assert saved_film is not None
    assert saved_film.kind == "movie"
    assert saved_film.original_language == "en"
    assert isinstance(saved_film.created_at, datetime)


def test_create_person(session):
    person = Person(name="Christopher Nolan")
    session.add(person)
    session.commit()

    saved_person = session.query(Person).filter_by(name="Christopher Nolan").first()
    assert saved_person is not None
    assert saved_person.name == "Christopher Nolan"


def test_film_title_relationship(session):
    film = Film()
    session.add(film)
    session.commit()

    title = Title(film_id=film.id, title="Inception", is_primary=True)
    session.add(title)
    session.commit()

    assert len(film.titles) == 1
    assert film.titles[0].title == "Inception"


def test_title_unique_constraint(session):
    f = Film()
    session.add(f)
    session.commit()

    t1 = Title(film_id=f.id, title="Inception", language="en", region="US")
    session.add(t1)
    session.commit()

    t2 = Title(film_id=f.id, title="Inception", language="en", region="US")
    session.add(t2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_release_unique_constraint(session):
    f = Film()
    session.add(f)
    session.commit()

    r1 = Release(film_id=f.id, release_type="theatrical", region="US", date=date(2010, 7, 16))
    session.add(r1)
    session.commit()

    r2 = Release(film_id=f.id, release_type="theatrical", region="US", date=date(2010, 7, 16))
    session.add(r2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_alternate_name_unique_constraint(session):
    p = Person(name="Nolan")
    session.add(p)
    session.commit()

    a1 = AlternateName(person_id=p.id, name="Chris Nolan")
    session.add(a1)
    session.commit()

    a2 = AlternateName(person_id=p.id, name="Chris Nolan")
    session.add(a2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_credit_unique_constraint(session):
    f = Film()
    p = Person(name="Nolan")
    session.add_all([f, p])
    session.commit()

    c1 = Credit(film_id=f.id, person_id=p.id, role="director")
    session.add(c1)
    session.commit()

    c2 = Credit(film_id=f.id, person_id=p.id, role="director")
    session.add(c2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_identifier_unique_constraint(session):
    f1 = Film()
    f2 = Film()
    session.add_all([f1, f2])
    session.commit()

    i1 = Identifier(film_id=f1.id, scheme="imdb", value="tt0123456")
    session.add(i1)
    session.commit()

    # Should fail even for different film if scheme/value is same
    i2 = Identifier(film_id=f2.id, scheme="imdb", value="tt0123456")
    session.add(i2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_asset_unique_constraint(session):
    f = Film()
    session.add(f)
    session.commit()

    a1 = Asset(film_id=f.id, type="poster", url="http://example.com/p.jpg")
    session.add(a1)
    session.commit()

    a2 = Asset(film_id=f.id, type="backdrop", url="http://example.com/p.jpg")
    session.add(a2)
    with pytest.raises(IntegrityError):
        session.commit()


def test_cascade_delete_film(session):
    f = Film()
    session.add(f)
    session.commit()

    t = Title(film_id=f.id, title="Inception")
    session.add(t)
    session.commit()

    assert session.query(Title).count() == 1

    session.delete(f)
    session.commit()

    assert session.query(Title).count() == 0


def test_cascade_delete_person(session):
    p = Person(name="Nolan")
    session.add(p)
    session.commit()

    a = AlternateName(person_id=p.id, name="Chris Nolan")
    session.add(a)
    session.commit()

    assert session.query(AlternateName).count() == 1

    session.delete(p)
    session.commit()

    assert session.query(AlternateName).count() == 0


def test_data_source_unique_name(session):
    source = DataSource(name="tmdb", enabled=True)
    session.add(source)
    session.commit()

    duplicate = DataSource(name="tmdb", enabled=False)
    session.add(duplicate)
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_source_capability_unique(session):
    source = DataSource(name="wikidata")
    session.add(source)
    session.commit()

    cap1 = DataSourceCapability(
        data_source_id=source.id,
        capability="films",
        payload_mapping='{"title": "name"}'
    )
    cap2 = DataSourceCapability(data_source_id=source.id, capability="films")
    session.add_all([cap1, cap2])
    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
    
    saved_cap = session.query(DataSourceCapability).filter_by(data_source_id=source.id, capability="films").first()
    if saved_cap:
        # This part depends on if cap1 was added before exception
        # But actually IntegrityError happens at commit.
        pass
    
    # Test saving and reading payload_mapping
    cap3 = DataSourceCapability(
        data_source_id=source.id,
        capability="people",
        payload_mapping='{"name": "fullname"}'
    )
    session.add(cap3)
    session.commit()
    
    fetched = session.query(DataSourceCapability).filter_by(data_source_id=source.id, capability="people").one()
    assert fetched.payload_mapping == '{"name": "fullname"}'


def test_data_source_credential_expiry_and_uniqueness(session):
    source = DataSource(name="imdb")
    session.add(source)
    session.commit()

    cred = DataSourceCredential(
        data_source_id=source.id,
        kind="api_key",
        token="secret-token",
    )
    session.add(cred)
    session.commit()

    assert cred.is_expired is False

    duplicate = DataSourceCredential(
        data_source_id=source.id,
        kind="api_key",
        token="secret-token",
    )
    session.add(duplicate)
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_source_rate_limit_unique_window(session):
    source = DataSource(name="archive")
    session.add(source)
    session.commit()

    limit1 = DataSourceRateLimit(data_source_id=source.id, window_seconds=60, max_calls=10)
    limit2 = DataSourceRateLimit(data_source_id=source.id, window_seconds=60, max_calls=20)
    session.add_all([limit1, limit2])
    with pytest.raises(IntegrityError):
        session.commit()


def test_data_source_rate_limit_retry_config(session):
    source = DataSource(name="retry_test")
    session.add(source)
    session.commit()

    limit = DataSourceRateLimit(
        data_source_id=source.id,
        window_seconds=60,
        max_calls=10,
        max_retries=5,
        backoff_multiplier=3
    )
    session.add(limit)
    session.commit()

    fetched = session.query(DataSourceRateLimit).filter_by(data_source_id=source.id).one()
    assert fetched.max_retries == 5
    assert fetched.backoff_multiplier == 3


def test_data_source_refresh_policy_one_to_one(session):
    source = DataSource(name="festival")
    session.add(source)
    session.commit()

    policy = DataSourceRefreshPolicy(
        data_source_id=source.id,
        default_refresh_interval_minutes=60,
        max_record_age_days=7,
    )
    session.add(policy)
    session.commit()

    fetched_policy = session.query(DataSourceRefreshPolicy).filter_by(data_source_id=source.id).one()
    assert fetched_policy.max_record_age_days == 7


def test_data_source_run_records(session):
    source = DataSource(name="webhook_source")
    session.add(source)
    session.commit()

    run = DataSourceRun(
        data_source_id=source.id,
        status="success",
        items_fetched=10,
        items_processed=10,
    )
    session.add(run)
    session.commit()

    saved_run = session.query(DataSourceRun).filter_by(data_source_id=source.id).one()
    assert saved_run.status == "success"

def test_data_source_refresh_policy_etags(session):
    source = DataSource(name="etag_test")
    session.add(source)
    session.commit()

    policy = DataSourceRefreshPolicy(
        data_source_id=source.id,
        default_refresh_interval_minutes=60,
        supports_etags=True
    )
    session.add(policy)
    session.commit()

    fetched = session.query(DataSourceRefreshPolicy).filter_by(data_source_id=source.id).one()
    assert fetched.supports_etags is True
