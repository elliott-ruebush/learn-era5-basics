# Geospatial Learning

## Overview

This repo is a living document for me to learn about working with geospatial data in python. It started as a simple attempt to read some ERA5 (ECMWF's climate data reanalysis) data, but has additionally involved into hodgepodge of experimenting with structuring python projects under uv, using marimo for notebooks, learning about useful libraries for geospatial data analysis like xarray, dask, and cartopy, and generally exploring geospatial.

Finally, it's also a test of using Google Antigravity as an IDE.

## Notebook Results

* [Hot and Cold: City Climate Comparison](notebooks/hot_and_cold.ipynb)

## Markdown Writeups

<!-- START_TOC -->

* **Guides**
    * [CDS API Setup Guide](docs/guides/cds-setup.md)
* **My Writeups**
    * [ARCO and Modern Geospatial](docs/my-writeups/arco-overview.md)
    * [Geospatial Data Levels](docs/my-writeups/geospatial-data-levels.md)

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
