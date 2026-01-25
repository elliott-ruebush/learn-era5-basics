# ERA5 Basics

## Overview

This repo is a living document for me to learn about working with ERA5 (ECMWF's climate data reanalysis). It's also a hodgepodge of experimenting with structuring python projects under uv, using marimo for notebooks, and learning about useful libraries for geospatial data analysis like xarray, dask, and cartopy. Finally, it's also a first attempt at using Google Antigravity as an IDE.

## Documentation

<!-- START_TOC -->

* **Guides**
    * [CDS API Setup Guide](docs/guides/cds-setup.md)
* **Reference**
    * [ARCO and Modern Geospatial](docs/reference/arco-overview.md)
    * [Geospatial Data Levels](docs/reference/geospatial-data-levels.md)

<!-- END_TOC -->

## Setup

Install dependencies and setup pre-commit:
```bash
uv sync --dev
uv run pre-commit install
```

Run marimo notebooks:
```bash
uv run marimo edit notebooks/data_access_patterns.py
```

Run scripts:
```bash
uv run download-era5  # Download ERA5 data
uv run explore-era5   # Explore ERA5 data
```

Run tests:
```bash
uv run pytest tests/
```

## Development

This project uses **pre-commit** with with a very astral-y code quality setup of ruff and ty. See pre-commit-config.yaml for details.

### Manual Checks
You can run the full suite of checks manually at any time:
```bash
# Run all pre-commit hooks
uv run pre-commit run --all-files

# Or run individual tools
uv run ruff check .
uv run ty check
```
