from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from open_cinema_index.models import (
    DataSource,
    DataSourceCredential,
    DataSourceRun,
)


class DataSourceNotConfiguredError(Exception):
    """Raised when a requested data source is not configured."""


class DataSourceDisabledError(Exception):
    """Raised when a requested data source is disabled."""


class RateLimitExceededError(Exception):
    """Raised when a data source rate limit would be exceeded."""


@dataclass
class FetchPlan:
    """Context for executing a fetch against a data source."""

    data_source: DataSource
    credential: DataSourceCredential | None
    run: DataSourceRun


class DataSourceService:
    """Business logic for preparing and tracking data source fetches."""

    def __init__(self, session):
        self.session = session

    def prepare_fetch(self, source_name: str) -> FetchPlan:
        """
        Prepare a fetch against the given data source.

        Sequence:
        1. Load the source and ensure it's enabled.
        2. Enforce configured rate limits.
        3. Select an active credential (if any).
        4. Record start of run for audit and throttling.
        """
        data_source = self._load_data_source(source_name)
        self._enforce_rate_limits(data_source)
        credential = self._select_active_credential(data_source)
        run = self._record_run(data_source, status="started")
        return FetchPlan(data_source=data_source, credential=credential, run=run)

    def _load_data_source(self, source_name: str) -> DataSource:
        data_source = self.session.query(DataSource).filter_by(name=source_name).one_or_none()
        if data_source is None:
            raise DataSourceNotConfiguredError(f"Data source '{source_name}' is not configured.")
        if not data_source.enabled:
            raise DataSourceDisabledError(f"Data source '{source_name}' is disabled.")
        return data_source

    def _enforce_rate_limits(self, data_source: DataSource) -> None:
        now = datetime.now(timezone.utc)
        for rate_limit in data_source.rate_limits:
            window_start = now - timedelta(seconds=rate_limit.window_seconds)
            recent_runs = (
                self.session.query(DataSourceRun)
                .filter(DataSourceRun.data_source_id == data_source.id)
                .filter(DataSourceRun.started_at >= window_start)
                .count()
            )
            if recent_runs >= rate_limit.max_calls:
                window_label = f"{rate_limit.window_seconds}s window"
                raise RateLimitExceededError(
                    f"Rate limit exceeded for '{data_source.name}' ({rate_limit.max_calls} calls per {window_label})."
                )

    @staticmethod
    def _select_active_credential(data_source: DataSource) -> DataSourceCredential | None:
        active_credentials = [cred for cred in data_source.credentials if not cred.is_expired]
        if not active_credentials:
            return None
        return sorted(active_credentials, key=lambda cred: cred.expired_at or datetime.max)[0]

    def _record_run(self, data_source: DataSource, status: str, error: str | None = None) -> DataSourceRun:
        run = DataSourceRun(
            data_source_id=data_source.id,
            status=status,
            error=error,
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(run)
        self.session.flush()
        return run
