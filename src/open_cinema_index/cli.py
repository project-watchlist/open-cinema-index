from contextlib import contextmanager

import typer
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

app = typer.Typer(
    name="oci",
    help="Open Cinema Index — film ingestion and indexing toolkit",
)


def get_session_factory():
    engine = create_engine("sqlite:///open_cinema_index.db")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.command()
def fetch(
    source: str = typer.Argument(..., help="Source name (e.g. tmdb, imdb)"),
    film_id: str | None = typer.Option(None, "--film-id", help="Fetch a specific film by source identifier"),
    since: str | None = typer.Option(None, "--since", help="Fetch items updated since this date (YYYY-MM-DD)"),
):
    """
    Fetch raw data from a source without normalization.
    """
    pass


@app.command()
def normalize(source: str | None = typer.Option(None, "--source", help="Normalize data from a specific source")):
    """
    Normalize raw source data into canonical film entities.
    """
    pass


@app.command()
def resolve(entity: str = typer.Argument(..., help="Entity type to resolve (films, people)")):
    """
    Resolve duplicate or conflicting entities.
    """
    pass


@app.command()
def enrich(
    target: str = typer.Argument(..., help="Enrichment target (genres, assets, credits, etc.)"),
    limit: int | None = typer.Option(None, "--limit", help="Limit number of items to enrich"),
):
    """
    Enrich canonical entities with additional metadata.
    """
    pass


@app.command()
def inspect(
    entity: str = typer.Argument(..., help="Entity type (film, person, conflict)"),
    entity_id: str | None = typer.Argument(None, help="Entity identifier"),
):
    """
    Inspect canonical data and provenance.
    """
    pass


@app.command()
def export(
    export_format: str = typer.Argument(..., help="Export format (json, sqlite, graph)"),
    output: str | None = typer.Option(None, "--output", help="Output path"),
):
    """
    Export indexed data for downstream use.
    """
    pass


if __name__ == "__main__":
    app()
