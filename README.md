# ERA5 Basics

## Overview

This repo is a living document for me to learn about working with ERA5 (ECMWF's climate data reanalysis). It's also a hodgepodge of experimenting with structuring python projects under uv, using marimo for notebooks, and learning about useful libraries for geospatial data analysis like xarray, dask, and cartopy. Finally, it's also a first attempt at using Google Antigravity as an IDE.

## Setup

Install dependencies:
```bash
uv sync --dev
```

Run marimo notebooks:
```bash
uv run marimo edit notebooks/era5_analysis.py
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