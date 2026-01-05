# Data Sources and Ingestion

Open Cinema Index (OCI) uses a structured system to manage data ingestion from various external providers. This document explains the core components of the ingestion system: Data Sources, Capabilities, Refresh Policies, Rate Limits, and Runs.

## Data Sources

A `DataSource` represents an external entity that provides film-related data. Each source is uniquely identified by its name and has several configuration properties:

- **name**: A unique identifier for the source (e.g., `tmdb`, `wikidata`).
- **kind**: The protocol used to communicate with the source (`rest`, `graphql`, `file`).
- **base_url**: The root URL for API requests.
- **user_agent**: A custom User-Agent string to be used for requests to this source.
- **enabled**: A boolean flag to quickly enable or disable a source without deleting its configuration.

Data sources also track their execution history via `last_run_started_at`, `last_run_completed_at`, and `last_error`.

## Capabilities

`DataSourceCapability` defines what kind of data a specific `DataSource` is able to provide and how to access it. This allows the OCI pipeline to intelligently route requests to the most appropriate sources and construct correct URLs.

Properties:
- **capability**: The identifier for the type of data (e.g., `films`, `people`, `assets`, `updates`).
- **endpoint_path**: A relative path or query template that is appended to the `base_url` to fetch the data.
- **payload_mapping**: A JSON-defined mapping that tells OCI how to translate the external response into its canonical schema.

Example paths:
- `/movie/{id}` for TMDB films.
- `?query={query}` for Wikidata SPARQL.

### Response Mapping

The `payload_mapping` field allows OCI to handle "unknown" sources by defining how to extract data from their responses. It typically maps JSON paths or keys from the source to OCI fields.

Example mapping for a `films` capability:
```json
{
  "title": "original_title",
  "runtime_minutes": "runtime",
  "original_language": "iso_639_1"
}
```

This mapping is used during the `normalize` phase of the ingestion pipeline.

Common capabilities include:
- `films`: Can provide basic film metadata.
- `people`: Can provide data about cast and crew.
- `assets`: Can provide URLs for posters, backdrops, etc.
- `updates`: Can provide a stream of recently changed records.

## Refresh Policies

The `DataSourceRefreshPolicy` determines how often data from a source should be updated and how to handle incremental fetches.

- **default_refresh_interval_minutes**: The standard time to wait before re-fetching a record from this source.
- **max_record_age_days**: The maximum age a record can reach before it is considered stale, regardless of the refresh interval.
- **incremental_cursor_field**: The field used to track progress during incremental ingestion (e.g., a timestamp or an ID).
- **supports_webhook**: Indicates if the source can push updates to OCI via webhooks.

## Rate Limits

To be a good citizen of the web and avoid being blocked, OCI strictly adheres to rate limits defined in `DataSourceRateLimit`.

- **window_seconds**: The duration of the rate limit window (e.g., 60 seconds for a "per minute" limit).
- **max_calls**: The maximum number of requests allowed within the window.
- **burst**: The number of requests allowed in a single burst, even if it exceeds the average rate momentarily.
- **retry_delay_seconds**: How long to wait before retrying if a rate limit is hit.

Multiple rate limits can be applied to a single source (e.g., 40 requests per 10 seconds AND 10,000 requests per day).

## Runs

A `DataSourceRun` represents a single execution of the ingestion process for a specific source. It provides observability and audit trails for data ingestion.

- **started_at** / **completed_at**: Timestamps for the duration of the run.
- **status**: The outcome of the run (`started`, `success`, `failed`).
- **error**: If the run failed, the error message or stack trace.
- **items_fetched**: Total number of records retrieved from the source.
- **items_processed**: Total number of records successfully integrated into OCI.

The `duration` of a run is calculated as the difference between `completed_at` and `started_at`.
