# TODO: Open Cinema Index (OCI) Features & Implementation Plan

This document outlines the planned features and implementation tasks for the Open Cinema Index project, organized by the ingestion pipeline stages.

## 1. Core Ingestion Pipeline

### [ ] Fetch
- [ ] Implement generic fetcher for REST APIs using `DataSourceCapability`.
- [ ] Configure `tmdb` and `wikidata` to use the generic fetcher.
- [ ] Implement `RawData` model to store un-normalized source responses for provenance.
- [ ] Support for incremental fetching using `since` parameter.
- [ ] Support for ETag-based caching and conditional requests.
- [ ] Implementation of retry logic and exponential backoff as defined in `DataSourceRateLimit`.
- [ ] Proper error handling and logging of `DataSourceRun` results.
- [ ] Add support for Webhook-based ingestion as defined in `DataSourceRefreshPolicy`.

### [ ] Normalize
- [ ] Implement generic normalization engine using `payload_mapping` from `DataSourceCapability`.
- [ ] Configure `tmdb` and `wikidata` payload mappings for canonical schema.
- [ ] Handle normalization of `Person` and `AlternateName` entities.
- [ ] Handle multilingual titles and localized metadata during normalization.
- [ ] Implement validation of normalized entities against the [Film Schema](docs/film-schema.md).

### [ ] Resolve
- [ ] Implement `Conflict` and `Resolution` models to track disputed claims.
- [ ] Implement identity resolution between different sources (e.g., matching a TMDB record to a Wikidata record).
- [ ] Develop conflict detection and resolution strategies for overlapping claims.
- [ ] Add support for "identity collisions" and manual resolution markers.
- [ ] Implement `oci resolve films` and `oci resolve people` commands.

### [ ] Enrich
- [ ] Implement secondary metadata enrichment (genres, keywords, synopses).
- [ ] Implement asset discovery and linking (posters, backdrops, trailers).
- [ ] Implement credit enrichment (cast and crew) and person entity creation.
- [ ] Add support for confidence-based enrichment updates.

### [ ] Export
- [ ] Implement JSON export (flat and nested formats).
- [ ] Implement SQLite export (pre-built dataset for distribution).
- [ ] Implement Graph/RDF export (for linked data consumption).
- [ ] Implement confidence-weighted resolution logic for "picking a winner" during export.
- [ ] Add support for Delta-updates in exports (only exporting what changed).

## 2. Infrastructure & Operations

### [ ] CLI Enhancements
- [ ] Implement `oci inspect` to view provenance and claims for an entity.
- [ ] Implement `oci inspect conflict` to debug resolution logic.
- [ ] Add progress bars and better logging for long-running pipeline tasks.
- [ ] Support for dry-run modes in `fetch` and `normalize`.

### [ ] Data Management
- [ ] Implement database migrations for `RawData`, `Conflict`, and `Resolution` models.
- [ ] Define and implement a validation schema for `payload_mapping` JSON in `DataSourceCapability`.
- [ ] Implement logic for `max_record_age_days` enforcement in `DataSourceRefreshPolicy`.
- [ ] Implement checksum verification for `Asset` objects during the `enrich` phase.
- [ ] Add database indexes for performance (e.g., `Identifier.value`, `Title.title`, `MetadataAssertion.type`).
- [ ] Automated database cleanup for old `DataSourceRun` and `RawData` records.
- [ ] Implement data archival/versioning for previous pipeline outputs.
- [ ] Better handling of credentials (e.g., environment variable integration and encryption/decryption of stored tokens).

### [ ] Quality & Validation
- [ ] Expand test coverage for services and models.
- [ ] Implement a data validation suite to ensure index integrity.
- [ ] Implement an assertion schema registry to ensure consistency of keys/values in `MetadataAssertion`.
- [ ] Add benchmarks for large-scale ingestion runs.

## 3. Future Research & Extensions
- [ ] Integration with more open sources (IMDb, Letterboxd, etc. - via public data dumps).
- [ ] Support for user-contributed assertions and peer-to-peer index sharing.
- [ ] Web-based dashboard for inspecting the index and monitoring pipeline health.
