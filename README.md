# Open Cinema Index

*Open Cinema Index (OCI)* is a data ingestion and enrichment pipeline for building a structured, open index of films and related entities. It is designed for research, recommendation engines, and archival purposes. The repository contains scripts to fetch film data from open sources, enrich it with metadata, and prepare it for downstream applications.

It is *not* a recommendation engine, a rating platform, or an editorial system.
Its sole responsibility is to build a reliable, inspectable index of film knowledge that other systems can depend on.

OCI is designed to treat cinema as it actually exists: messy, disputed, multilingual, and full of partial truths.

## Features

- Fetch films from Wikidata by year and retrieve basic metadata
- Enrich films with properties such as genre, language, and age ratings
- Designed for offline processing, production applications consume pre-built datasets

## How OCI Thinks About Films

OCI is built around a few guiding ideas:

- Films are stable entities; facts about them are not
- Titles, genres, runtimes, and even credits are _claims_, not facts
- Different sources disagree, and that disagreement is meaningful

Rather than flattening every into a single record, OCI keeps track of:

- who said what
- when they said it
- and how confident we are

Ambiguity is preserved, not "cleaned up".

## The Ingestion Pipeline

OCI is structured as a pipeline of explicit, repeatable steps:

```text
fetch -> normalize -> resolve -> enrich -> export
```

Each step has a narrow responsibility.

### Fetch

Retrieves raw data from a source without interpretation or transformation.

### Default Data Sources

OCI ships with two preconfigured sources:

- **tmdb** — REST (`https://api.themoviedb.org/3`), seeded with a safe 40-requests-per-10-seconds limit (matching historical official limits).
- **wikidata** — REST (`https://query.wikidata.org/sparql`), seeded with a 1-request-per-1-second limit (matching WDQS usage policy).

You can adjust limits, capabilities, refresh policies, credentials, or disable them by editing the corresponding rows after running migrations.

### Normalize

Maps raw data into OCI's canonical schema.

### Resolve

Handles duplicates, identity collisions, and uncertainty between entities.

### Enrich

Adds secondary metadata (genres, assets, keywords, etc.) additively.

### Export

Emits the indexed data in formats suitable for downstream systems.

## Provenance and Confidence

Every piece of data stored by OCI is associated with:

- a source
- a fetch timestamp
- an optional confidence level

Conflicting data is expected and preserved.
"Unknown" and "uncertain" are valid outcomes.

## Why This Exists

Film culture is broader and stranger than most databases allow.

Many existing systems:

- flatten ambiguity
- privilege a single source
- erase minority or regional perspectives

OCI exists to preserve the richness of cinema history without pretending it's tidy.

## Project Status

Open Cinema Index is under active development.

The schema and CLI are expected to evolve.

Contributions are welcome, especially those that respect the project's archival philosophy.
