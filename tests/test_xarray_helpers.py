"""Unit tests for xarray_helpers module."""

import numpy as np
import pytest
import xarray as xr

from notebook_utils.xarray_helpers import get_city_extent


class TestGetCityExtent:
    """Tests for the get_city_extent function."""
    
    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset with two cities (simulating concatenated ERA5 data)."""
        # Chicago coordinates
        chicago_lat = np.array([41.6, 41.85, 42.1])
        chicago_lon = np.array([-87.8, -87.55, -87.3])
        
        # NYC coordinates  
        nyc_lat = np.array([40.5, 40.75, 41.0])
        nyc_lon = np.array([-74.2, -73.95, -73.7])
        
        # Combined coordinates (outer join - all unique values)
        all_lats = np.array([40.5, 40.75, 41.0, 41.6, 41.85, 42.1])
        all_lons = np.array([-87.8, -87.55, -87.3, -74.2, -73.95, -73.7])
        
        # Create temperature data with NaN padding
        # Shape: (2 cities, 6 lats, 6 lons)
        temp_data = np.full((2, 6, 6), np.nan)
        
        # Chicago data (first 3 lats, first 3 lons)
        temp_data[0, 3:6, 0:3] = np.random.randn(3, 3) + 273.15
        
        # NYC data (first 3 lats, last 3 lons)
        temp_data[1, 0:3, 3:6] = np.random.randn(3, 3) + 273.15
        
        # Create the dataset
        ds = xr.Dataset(
            {
                "t2m": (["city", "latitude", "longitude"], temp_data),
            },
            coords={
                "city": ["Chicago", "NYC"],
                "latitude": all_lats,
                "longitude": all_lons,
            }
        )
        
        return ds
    
    @pytest.fixture
    def simple_dataset(self):
        """Create a simpler dataset for basic testing."""
        # Single city with clear bounds
        lats = np.array([40.0, 40.5, 41.0])
        lons = np.array([-75.0, -74.5, -74.0, -73.5])
        
        # Create temperature data (no NaN since single city)
        temp_data = np.ones((1, 3, 4)) * 280.0
        
        ds = xr.Dataset(
            {
                "temp": (["city", "latitude", "longitude"], temp_data)
            },
            coords={
                "city": ["TestCity"],
                "latitude": lats,
                "longitude": lons,
            }
        )
        return ds
    
    def test_get_city_extent_basic(self, simple_dataset):
        """Test basic functionality with a simple dataset."""
        lonW, lonE, latS, latN = get_city_extent(simple_dataset, "TestCity")
        
        assert lonW == -75.0
        assert lonE == -73.5
        assert latS == 40.0
        assert latN == 41.0
    
    def test_get_city_extent_returns_tuple(self, simple_dataset):
        """Test that function returns a tuple of 4 floats."""
        result = get_city_extent(simple_dataset, "TestCity")
        
        assert isinstance(result, tuple)
        assert len(result) == 4
        assert all(isinstance(x, float) for x in result)
    
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
            }
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
            }
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
            }
        )
        
        with pytest.raises(KeyError, match="Dataset must have a 'longitude' coordinate"):
            get_city_extent(ds, "TestCity")
    
    def test_get_city_extent_order(self, simple_dataset):
        """Test that the returned values are in correct order (W, E, S, N)."""
        lonW, lonE, latS, latN = get_city_extent(simple_dataset, "TestCity")
        
        # West should be less than East
        assert lonW < lonE
        # South should be less than North
        assert latS < latN
    
    def test_get_city_extent_with_negative_coords(self):
        """Test with negative coordinates (common for Western hemisphere)."""
        ds = xr.Dataset(
            {"temp": (["city", "latitude", "longitude"], np.ones((1, 2, 2)))},
            coords={
                "city": ["City"],
                "latitude": [-10.0, -5.0],
                "longitude": [-120.0, -115.0],
            }
        )
        
        lonW, lonE, latS, latN = get_city_extent(ds, "City")
        
        assert lonW == -120.0
        assert lonE == -115.0
        assert latS == -10.0
        assert latN == -5.0
    
    def test_get_city_extent_with_real_era5_data(self):
        """Integration test with actual ERA5 data files if available."""
        from pathlib import Path
        
        # Check if ERA5 data files exist
        base_dir = Path(".")
        chicago_file = base_dir / "era5_chicago_jan2023.nc"
        nyc_file = base_dir / "era5_nyc_jan2023.nc"
        
        if not (chicago_file.exists() and nyc_file.exists()):
            pytest.skip("ERA5 data files not found")
        
        # Load and concatenate data (mimicking the notebook)
        def load_location_data(filename, city_name):
            ds = xr.open_dataset(
                base_dir / filename,
                engine="h5netcdf",
                chunks={"valid_time": 24}
            )
            ds = ds.assign_coords(city=city_name)
            return ds
        
        ds_chi = load_location_data("era5_chicago_jan2023.nc", "Chicago")
        ds_nyc = load_location_data("era5_nyc_jan2023.nc", "NYC")
        ds = xr.concat([ds_chi, ds_nyc], dim="city")
        
        # Test Chicago extent
        chi_lonW, chi_lonE, chi_latS, chi_latN = get_city_extent(ds, "Chicago")
        assert chi_lonW < chi_lonE
        assert chi_latS < chi_latN
        # Chicago should be around -87 to -88 longitude, 41-42 latitude
        assert -89 < chi_lonW < -86
        assert -89 < chi_lonE < -86
        assert 40 < chi_latS < 43
        assert 40 < chi_latN < 43
        
        # Test NYC extent
        nyc_lonW, nyc_lonE, nyc_latS, nyc_latN = get_city_extent(ds, "NYC")
        assert nyc_lonW < nyc_lonE
        assert nyc_latS < nyc_latN
        # NYC should be around -73 to -74 longitude, 40-41 latitude
        assert -75 < nyc_lonW < -72
        assert -75 < nyc_lonE < -72
        assert 39 < nyc_latS < 42
        assert 39 < nyc_latN < 42
