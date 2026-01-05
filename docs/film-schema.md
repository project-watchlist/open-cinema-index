# Film Schema & Design Decisions

The Open Cinema Index (OCI) film schema is not just a storage format; it is a manifestation of our core philosophy about cinematic data. It is designed to handle the inherent messiness, subjectivity, and evolution of film history.

## Design Principles

### 1. Stability vs. Claims
We distinguish between the **Film** (the abstract concept of the work) and **Claims** (data about that work). 
- A `Film` record is a stable anchor.
- Titles, runtimes, and credits are treated as "claims" provided by specific sources.
- This is why almost every entity in OCI has a `source` field.

### 2. Preserving Ambiguity
Most databases "clean" data by picking a winner when sources disagree. OCI rejects this.
- We store multiple values for the same attribute (e.g., three different runtimes from three different sources).
- Disagreement is considered valuable data, not a bug.

### 3. Provenance as a First-Class Citizen
Data without a source is noise. 
- Every piece of metadata is tied to a `source`.
- `confidence` scores allow us to weight these claims during export or resolution without deleting the underlying "less confident" data.

### 4. Additive Enrichment
The schema is designed to grow. We start with a "skeleton" (usually from Wikidata) and add layers of assertions from other sources (TMDB, IMDb, etc.) over time.

---

## Core Entities

### Film
The central anchor. It contains almost no descriptive metadata itself, serving primarily to group claims together.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Internal OCI identifier (Primary Key). |
| `kind` | String | Categorization (e.g., movie, tv_series). This is one of the few fields on the anchor, used for high-level filtering. |
| `runtime_minutes` | Integer | A "canonical" runtime if resolved, though specific releases may vary. |
| `original_language` | String | ISO 639-1 code. |

### Title
Instead of a single "Title" field on the Film, we use a separate table.
**Design Decision:** Allow for infinite variations. A film can have an original title, multiple translated titles, and regional "working titles".
- `is_original`: Marks the title as the one used in the production's home country.
- `is_primary`: Used to designate which title should be displayed by default for a specific language/region pair.

### MetadataAssertion
This is the "catch-all" for descriptive attributes like genres, synopses, or keywords.
**Design Decision:** Use a Key-Value pair approach for non-structural data.
- This allows us to support new types of metadata (e.g., "color palette" or "shooting format") without migrating the database schema.
- Multiple sources can make the same type of assertion with different values.

### Credit
Links people to films.
**Design Decision:** Credits are source-specific. If Source A says John Doe was the Director and Source B says he was the Producer, we store both.
- `order`: Preserves the "billing order" which is often culturally or contractually significant.

### Identifier
The "glue" that allows OCI to bridge different worlds.
**Design Decision:** Store every known external ID (IMDb, TMDB, Wikidata).
- This enables the "Resolve" step of the pipeline to connect disparate data streams into a single OCI Film entity.

### Release
**Design Decision:** Treat releases as distinct events in time and space.
- A film doesn't have "a" release date; it has many.
- Includes `release_type` (theatrical, digital, etc.) because a film's "identity" often changes between a festival cut and a home video release.

---

## Technical Reference Tables

### Person & AlternateName
People, like films, are stable entities with disputed attributes. `AlternateName` handles stage names, pseudonyms, and transliterations.

### Asset
References to external media (posters, trailers).
- Includes `checksum` to detect when a remote asset has changed or been corrupted.

## Relationships

- A **Film** is the root of a tree containing **Titles**, **Releases**, **Credits**, **Identifiers**, **MetadataAssertions**, and **Assets**.
- A **Person** exists independently and is linked to Films via **Credits**.
- All peripheral entities (except `Film` and `Person` anchors) must have a `source`.
