# Development Guide

This document provides information for developers who want to contribute to the `open-cinema-index` project.

## Getting Started

### Prerequisites

- Python 3.10+
- `pip`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/project-watchlist/open-cinema-index.git
   cd open-cinema-index
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables as described in the `README.md`.

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations. The database is a SQLite file located at `data/open_cinema_index.db`.

### Running Migrations

To bring your local database up to date with the latest schema, run:

```bash
alembic upgrade head
```

### Creating New Migrations

If you make changes to the models in `src/open_cinema_index/models/`, you should generate a new migration script:

```bash
alembic revision --autogenerate -m "description of changes"
```

Then, apply the migration as described above.

### Troubleshooting

If migrations fail due to the `data/` directory missing, ensure it exists:

```bash
mkdir -p data
```

## Running Tests

Testing is highly recommended for validating model relationships and ensuring data integrity.

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests using `pytest`:
   ```bash
   pytest
   ```

## Technical Documentation

Detailed documentation on specific components:

- [CLI Usage Guide](docs/cli.md)
- [Data Sources, Capabilities, Refresh Policies, Rate Limits, and Runs](docs/data-sources.md)
