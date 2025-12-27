"""add default data sources with configs

Revision ID: b92f2865ef96
Revises: 2a3e579f9916
Create Date: 2026-01-04 22:46:00.000000

"""
from collections.abc import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b92f2865ef96'
down_revision: str | Sequence[str] | None = '2a3e579f9916'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    now = datetime.now(timezone.utc)
    
    # Define table objects
    data_sources_table = sa.table(
        "data_sources",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("kind", sa.String),
        sa.column("base_url", sa.String),
        sa.column("enabled", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    
    rate_limits = sa.table(
        "data_source_rate_limits",
        sa.column("data_source_id", sa.Integer),
        sa.column("window_seconds", sa.Integer),
        sa.column("max_calls", sa.Integer),
    )
    
    refresh_policies = sa.table(
        "data_source_refresh_policies",
        sa.column("data_source_id", sa.Integer),
        sa.column("default_refresh_interval_minutes", sa.Integer),
        sa.column("max_record_age_days", sa.Integer),
    )
    
    capabilities = sa.table(
        "data_source_capabilities",
        sa.column("data_source_id", sa.Integer),
        sa.column("capability", sa.String),
    )

    # 1. Insert Data Sources
    op.bulk_insert(
        data_sources_table,
        [
            {
                "name": "tmdb",
                "kind": "rest",
                "base_url": "https://api.themoviedb.org/3",
                "enabled": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "name": "wikidata",
                "kind": "rest",
                "base_url": "https://query.wikidata.org/sparql",
                "enabled": True,
                "created_at": now,
                "updated_at": now,
            },
        ]
    )

    # Fetch source IDs
    res = bind.execute(
        sa.select(
            data_sources_table.c.id,
            data_sources_table.c.name
        )
        .where(data_sources_table.c.name.in_(["tmdb", "wikidata"]))
    )
    source_ids = {name: source_id for source_id, name in res}
    # 2. Insert Configs for TMDB
    if "tmdb" in source_ids:
        tmdb_id = source_ids["tmdb"]
        # TMDB removed hard rate limits in 2019, but 40/10s remains a recommended safe default
        op.bulk_insert(rate_limits, [{"data_source_id": tmdb_id, "window_seconds": 10, "max_calls": 40}])
        op.bulk_insert(refresh_policies, [{
            "data_source_id": tmdb_id, 
            "default_refresh_interval_minutes": 14 * 24 * 60,
            "max_record_age_days": 30
        }])
        op.bulk_insert(capabilities, [
            {"data_source_id": tmdb_id, "capability": c} 
            for c in ["films", "people", "assets", "updates"]
        ])

    # 3. Insert Configs for Wikidata
    if "wikidata" in source_ids:
        wikidata_id = source_ids["wikidata"]
        # Wikidata Query Service (WDQS) recommends max 60 requests per minute
        op.bulk_insert(rate_limits, [{"data_source_id": wikidata_id, "window_seconds": 1, "max_calls": 1}])
        op.bulk_insert(refresh_policies, [{
            "data_source_id": wikidata_id, 
            "default_refresh_interval_minutes": 30 * 24 * 60,
            "max_record_age_days": 60
        }])
        op.bulk_insert(capabilities, [
            {"data_source_id": wikidata_id, "capability": c} 
            for c in ["films", "people", "updates"]
        ])


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    data_sources = sa.table("data_sources", sa.column("id", sa.Integer), sa.column("name", sa.String))
    
    res = bind.execute(sa.select(data_sources.c.id).where(data_sources.c.name.in_(["tmdb", "wikidata"])))
    source_ids = [row[0] for row in res]
    
    if source_ids:
        ids_tuple = tuple(source_ids)

        where_clause = f"= {ids_tuple[0]}" if len(ids_tuple) == 1 else f"IN {ids_tuple}"

        op.execute(f"DELETE FROM data_source_rate_limits WHERE data_source_id {where_clause}")
        op.execute(f"DELETE FROM data_source_refresh_policies WHERE data_source_id {where_clause}")
        op.execute(f"DELETE FROM data_source_capabilities WHERE data_source_id {where_clause}")
        op.execute(f"DELETE FROM data_sources WHERE id {where_clause}")
