"""Unit tests for xarray_helpers module."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from geospatial_learning.utils import get_city_extent


class TestGetCityExtent:
    """Tests for the get_city_extent function."""

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset with two cities (simulating concatenated ERA5 data)."""
        # Combined coordinates (outer join - all unique values)
        all_lats = np.array([40.5, 40.75, 41.0, 41.6, 41.85, 42.1])
        all_lons = np.array([-87.8, -87.55, -87.3, -74.2, -73.95, -73.7])

        # Create temperature data with NaN padding
        # Shape: (2 cities, 6 lats, 6 lons)
        temp_data = np.full((2, 6, 6), np.nan)

        # Chicago data (last 3 lats, first 3 lons)
        temp_data[0, 3:6, 0:3] = np.random.randn(3, 3) + 273.15

        # NYC data (first 3 lats, last 3 lons)
        temp_data[1, 0:3, 3:6] = np.random.randn(3, 3) + 273.15

        # Create the dataset
        return xr.Dataset(
            {
                "t2m": (["city", "latitude", "longitude"], temp_data),
            },
            coords={
                "city": ["Chicago", "NYC"],
                "latitude": all_lats,
                "longitude": all_lons,
            },
        )

    @pytest.fixture
    def simple_dataset(self):
        """Create a simpler dataset for basic testing."""
        lats = np.array([40.0, 40.5, 41.0])
        lons = np.array([-75.0, -74.5, -74.0, -73.5])
        temp_data = np.ones((1, 3, 4)) * 280.0

        return xr.Dataset(
            {"temp": (["city", "latitude", "longitude"], temp_data)},
            coords={
                "city": ["TestCity"],
                "latitude": lats,
                "longitude": lons,
            },
        )

    def test_get_city_extent_basic(self, simple_dataset):
        """Test basic functionality with a simple dataset."""
        lon_w, lon_e, lat_s, lat_n = get_city_extent(simple_dataset, "TestCity")

        assert lon_w == -75.0
        assert lon_e == -73.5
        assert lat_s == 40.0
        assert lat_n == 41.0

    def test_get_city_extent_invalid_city(self, simple_dataset):
        """Test that ValueError is raised for non-existent city."""
        with pytest.raises(ValueError, match="City 'NonExistent' not found"):
            get_city_extent(simple_dataset, "NonExistent")

    def test_get_city_extent_missing_city_coord(self):
        """Test that KeyError is raised when 'city' coordinate is missing."""
        ds = xr.Dataset(
            {"temp": (["latitude", "longitude"], np.ones((3, 4)))},
            coords={
                "latitude": [40.0, 40.5, 41.0],
                "longitude": [-75.0, -74.5, -74.0, -73.5],
            },
        )

        with pytest.raises(KeyError, match="Dataset must have a 'city' coordinate"):
            get_city_extent(ds, "TestCity")

    def test_get_city_extent_missing_latitude_coord(self):
        """Test that KeyError is raised when 'latitude' coordinate is missing."""
        ds = xr.Dataset(
            {"temp": (["city", "longitude"], np.ones((1, 4)))},
            coords={
                "city": ["TestCity"],
                "longitude": [-75.0, -74.5, -74.0, -73.5],
            },
        )

        with pytest.raises(KeyError, match="Dataset must have a 'latitude' coordinate"):
            get_city_extent(ds, "TestCity")

    def test_get_city_extent_missing_longitude_coord(self):
        """Test that KeyError is raised when 'longitude' coordinate is missing."""
        ds = xr.Dataset(
            {"temp": (["city", "latitude"], np.ones((1, 3)))},
            coords={
                "city": ["TestCity"],
                "latitude": [40.0, 40.5, 41.0],
            },
        )

        with pytest.raises(KeyError, match="Dataset must have a 'longitude' coordinate"):
            get_city_extent(ds, "TestCity")

    def test_get_city_extent_no_data_variables(self):
        """Test that ValueError is raised when dataset has no data variables."""
        ds = xr.Dataset(
            coords={
                "city": ["TestCity"],
                "latitude": [40.0, 40.5],
                "longitude": [-75.0, -74.5],
            }
        )

        with pytest.raises(ValueError, match="Dataset has no data variables"):
            get_city_extent(ds, "TestCity")

    def test_get_city_extent_all_nan_data(self):
        """Test that ValueError is raised when city has only NaN data."""
        ds = xr.Dataset(
            {"temp": (["city", "latitude", "longitude"], np.full((1, 3, 4), np.nan))},
            coords={
                "city": ["TestCity"],
                "latitude": [40.0, 40.5, 41.0],
                "longitude": [-75.0, -74.5, -74.0, -73.5],
            },
        )

        with pytest.raises(ValueError, match="No valid data found for city"):
            get_city_extent(ds, "TestCity")

    def test_get_city_extent_with_time_dimension(self):
        """Test with temporal dimension (realistic ERA5 structure)."""
        ds = xr.Dataset(
            {
                "temp": (
                    ["city", "time", "latitude", "longitude"],
                    np.ones((1, 5, 3, 4)) * 280.0,
                )
            },
            coords={
                "city": ["TestCity"],
                "time": pd.date_range("2023-01-01", periods=5, freq="h"),
                "latitude": [40.0, 40.5, 41.0],
                "longitude": [-75.0, -74.5, -74.0, -73.5],
            },
        )

        lon_w, lon_e, lat_s, lat_n = get_city_extent(ds, "TestCity")

        assert lon_w == -75.0
        assert lon_e == -73.5
        assert lat_s == 40.0
        assert lat_n == 41.0

    def test_get_city_extent_multi_city_selection(self, sample_dataset):
        """Test that correct city is selected from multi-city dataset."""
        chi_extent = get_city_extent(sample_dataset, "Chicago")
        nyc_extent = get_city_extent(sample_dataset, "NYC")

        # Extents should be different
        assert chi_extent != nyc_extent

        # Chicago should be further west (more negative longitude)
        assert chi_extent[0] < nyc_extent[0]  # lonW
        assert chi_extent[1] < nyc_extent[1]  # lonE

        # Chicago should be further north
        assert chi_extent[2] > nyc_extent[2]  # latS
        assert chi_extent[3] > nyc_extent[3]  # latN

    def test_get_city_extent_single_point(self):
        """Test with a city that has only one grid point."""
        ds = xr.Dataset(
            {"temp": (["city", "latitude", "longitude"], np.array([[[280.0]]]))},
            coords={
                "city": ["TestCity"],
                "latitude": [40.0],
                "longitude": [-75.0],
            },
        )

        lon_w, lon_e, lat_s, lat_n = get_city_extent(ds, "TestCity")

        # All should be the same point
        assert lon_w == lon_e == -75.0
        assert lat_s == lat_n == 40.0

    def test_get_city_extent_with_real_era5_data(self):
        """Integration test with actual ERA5 data files if available."""
        from pathlib import Path

        # Check if ERA5 data files exist
        base_dir = Path()
        chicago_file = base_dir / "era5_chicago_jan2023.nc"
        nyc_file = base_dir / "era5_nyc_jan2023.nc"

        if not (chicago_file.exists() and nyc_file.exists()):
            pytest.skip("ERA5 data files not found")

        # Load and concatenate data (mimicking the notebook)
        def load_location_data(filename, city_name):
            return xr.open_dataset(base_dir / filename, engine="h5netcdf", chunks={"valid_time": 24}).assign_coords(
                city=city_name
            )

        ds_chi = load_location_data("era5_chicago_jan2023.nc", "Chicago")
        ds_nyc = load_location_data("era5_nyc_jan2023.nc", "NYC")
        ds = xr.concat([ds_chi, ds_nyc], dim="city")

        # Test Chicago extent
        chi_lon_w, chi_lon_e, chi_lat_s, chi_lat_n = get_city_extent(ds, "Chicago")
        assert chi_lon_w < chi_lon_e
        assert chi_lat_s < chi_lat_n

        # Test NYC extent
        nyc_lon_w, nyc_lon_e, nyc_lat_s, nyc_lat_n = get_city_extent(ds, "NYC")
        assert nyc_lon_w < nyc_lon_e
        assert nyc_lat_s < nyc_lat_n

        # Verify cities are in different locations
        assert chi_lon_w < nyc_lon_w  # Chicago is west of NYC
