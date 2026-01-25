"""Helper functions for working with xarray datasets."""

import xarray as xr


def get_city_extent(dataset: xr.Dataset, city: str) -> tuple[float, float, float, float]:
    """Get the lat/long bounding box for a city in the dataset.

    Args:
        dataset: xarray Dataset containing 'city', 'latitude', and 'longitude' coordinates
        city: Name of the city to get extent for

    Returns:
        Tuple of (lonW, lonE, latS, latN) representing the bounding box

    Raises:
        ValueError: If the city is not found in the dataset or if no valid data exists
        KeyError: If required coordinates are missing from the dataset
    """
    if len(dataset.data_vars) == 0:
        raise ValueError("Dataset has no data variables to determine extent")

    if "city" not in dataset.coords:
        raise KeyError("Dataset must have a 'city' coordinate")
    if "latitude" not in dataset.coords:
        raise KeyError("Dataset must have a 'latitude' coordinate")
    if "longitude" not in dataset.coords:
        raise KeyError("Dataset must have a 'longitude' coordinate")

    if city not in dataset.city.values:
        available_cities = ", ".join(str(c) for c in dataset.city.values)
        raise ValueError(f"City '{city}' not found in dataset. Available cities: {available_cities}")

    city_data = dataset.sel(city=city)

    first_var = next(iter(dataset.data_vars.keys()))
    city_var = city_data[first_var]

    # Find coordinates where we have non-NaN data
    # We need to check across all non-spatial dimensions (e.g., time)
    # by taking any() over those dimensions
    non_spatial_dims = [d for d in city_var.dims if d not in ["latitude", "longitude"]]

    if non_spatial_dims:
        # Reduce over non-spatial dimensions to get a 2D lat/lon mask
        has_data = city_var.notnull().any(dim=non_spatial_dims)
    else:
        # Already 2D
        has_data = city_var.notnull()

    # Compute the mask if it's a dask array (required for indexing)
    # This is a small boolean array so it's safe to compute
    if hasattr(has_data.data, "compute"):
        has_data = has_data.compute()

    # Get the latitude and longitude values where we have data
    lat_with_data = city_data.latitude.where(has_data.any(dim="longitude"), drop=True)
    lon_with_data = city_data.longitude.where(has_data.any(dim="latitude"), drop=True)

    if len(lat_with_data) == 0 or len(lon_with_data) == 0:
        raise ValueError(f"No valid data found for city '{city}'")

    # Extract min/max values
    lat_s = float(lat_with_data.min().values)
    lat_n = float(lat_with_data.max().values)
    lon_w = float(lon_with_data.min().values)
    lon_e = float(lon_with_data.max().values)

    return lon_w, lon_e, lat_s, lat_n


def calculate_daily_max(hourly_data: xr.DataArray) -> xr.DataArray:
    """Resample hourly data to daily maximum, preserving units attribute."""
    daily = hourly_data.resample(time="1D").max()
    if "units" in hourly_data.attrs and "units" not in daily.attrs:
        daily.attrs["units"] = hourly_data.attrs["units"]
    return daily


def calculate_daily_mean(hourly_data: xr.DataArray) -> xr.DataArray:
    """Resample hourly data to daily mean, preserving units attribute."""
    daily = hourly_data.resample(time="1D").mean()
    if "units" in hourly_data.attrs and "units" not in daily.attrs:
        daily.attrs["units"] = hourly_data.attrs["units"]
    return daily


def calculate_daily_min(hourly_data: xr.DataArray) -> xr.DataArray:
    """Resample hourly data to daily minimum, preserving units attribute."""
    daily = hourly_data.resample(time="1D").min()
    if "units" in hourly_data.attrs and "units" not in daily.attrs:
        daily.attrs["units"] = hourly_data.attrs["units"]
    return daily
