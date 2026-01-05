# CLI Usage Guide

The Open Cinema Index (OCI) provides a Command Line Interface (CLI) to manage the film ingestion and indexing pipeline.

## Installation

The CLI is installed as part of the `open-cinema-index` package. Ensure you have installed the package in your environment:

```bash
pip install -e .
```

You can then run the CLI using the `oci` command.

## Commands

### `fetch`

Retrieves raw data from a source without interpretation or transformation.

**Usage:**
```bash
oci fetch [SOURCE] [OPTIONS]
```

**Arguments:**
- `SOURCE`: The name of the data source (e.g., `tmdb`, `wikidata`).

**Options:**
- `--film-id TEXT`: Fetch a specific film by its source identifier.
- `--since TEXT`: Fetch items updated since this date (format: `YYYY-MM-DD`).
- `--help`: Show this message and exit.

---

### `normalize`

Maps raw source data into OCI's canonical film schema.

**Usage:**
```bash
oci normalize [OPTIONS]
```

**Options:**
- `--source TEXT`: Normalize data from a specific source. If omitted, all pending raw data will be normalized.
- `--help`: Show this message and exit.

---

### `resolve`

Handles duplicates, identity collisions, and uncertainty between entities.

**Usage:**
```bash
oci resolve [ENTITY] [OPTIONS]
```

**Arguments:**
- `ENTITY`: The type of entity to resolve (e.g., `films`, `people`).

**Options:**
- `--help`: Show this message and exit.

---

### `enrich`

Adds secondary metadata (genres, assets, keywords, etc.) additively to canonical entities.

**Usage:**
```bash
oci enrich [TARGET] [OPTIONS]
```

**Arguments:**
- `TARGET`: The enrichment target (e.g., `genres`, `assets`, `credits`).

**Options:**
- `--limit INTEGER`: Limit the number of items to enrich in this run.
- `--help`: Show this message and exit.

---

### `inspect`

View canonical data and its provenance for specific entities.

**Usage:**
```bash
oci inspect [ENTITY] [ENTITY_ID] [OPTIONS]
```

**Arguments:**
- `ENTITY`: The type of entity (e.g., `film`, `person`, `conflict`).
- `ENTITY_ID`: The internal OCI identifier for the entity.

**Options:**
- `--help`: Show this message and exit.

---

### `export`

Emits the indexed data in formats suitable for downstream systems.

**Usage:**
```bash
oci export [FORMAT] [OPTIONS]
```

**Arguments:**
- `FORMAT`: The export format (e.g., `json`, `sqlite`, `graph`).

**Options:**
- `--output PATH`: The file path to save the exported data.
- `--help`: Show this message and exit.
