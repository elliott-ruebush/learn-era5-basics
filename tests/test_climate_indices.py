import pandas as pd
import pytest
import xarray as xr

from geospatial_learning.utils.climate_indices import (
    calculate_cold_snaps,
    calculate_heat_index,
    calculate_heat_waves,
    calculate_wind_chill,
)


@pytest.mark.parametrize(
    "temp, dewpoint, expected_hi, description",
    [
        (70, 50, 70, "Cool conditions: HI ≈ Temp"),
        (90, 70, 95.5, "Hot/Humid: HI > Temp"),
        (80, 60, 80.9, "Moderate: Small increase"),
    ],
)
def test_calculate_heat_index_values(temp, dewpoint, expected_hi, description):
    """Test heat index calculation for specific scalar-like values."""
    time = pd.date_range("2023-01-01", periods=1)
    t_da = xr.DataArray([temp], coords={"time": time}, dims="time", attrs={"units": "degF"})
    d_da = xr.DataArray([dewpoint], coords={"time": time}, dims="time", attrs={"units": "degF"})

    hi = calculate_heat_index(t_da, d_da)

    assert hi.attrs["units"] == "°F"
    # Allow loose tolerance as formula is approximation
    assert abs(hi.values[0] - expected_hi) < 2.0, f"Failed for {description}"


@pytest.mark.parametrize(
    "temp, speed_mph, expected_wc, description",
    [
        (0, 20, -22, "Cold/Windy: Significant drop"),
        (30, 5, 25, "Cool/Light Wind: Slight drop"),
        (55, 20, 50.1, "Warm: Formula applied blindly (55->50)"),
        (30, 2, 30, "Low wind speed: No wind chill (stays as temp)"),
    ],
)
def test_calculate_wind_chill_values(temp, speed_mph, expected_wc, description):
    """Test wind chill calculation for specific scalar-like values."""
    time = pd.date_range("2023-01-01", periods=1)

    # We need u/v components. For simple speed test, we can put all speed in u.
    u_mph = speed_mph
    v_mph = 0

    t_da = xr.DataArray([temp], coords={"time": time}, dims="time", attrs={"units": "degF"})
    u_da = xr.DataArray([u_mph], coords={"time": time}, dims="time", attrs={"units": "mph"})
    v_da = xr.DataArray([v_mph], coords={"time": time}, dims="time", attrs={"units": "mph"})

    wc = calculate_wind_chill(t_da, u_da, v_da)

    assert wc.attrs["units"] == "°F"
    assert abs(wc.values[0] - expected_wc) < 2.0, f"Failed for {description}"


def test_calculate_heat_waves():
    """Test heat wave duration counting."""
    times = pd.date_range("2020-01-01", periods=10, freq="D")
    # 96, 97, 98 (3 day wave)
    values = [96, 97, 98, 80, 80, 80, 80, 80, 80, 80]

    da = xr.DataArray(values, coords={"time": times}, dims="time", attrs={"units": "degF"})

    # heat_wave_index returns total length of hot spells
    days = calculate_heat_waves(da, threshold_f=95, window_days=2)
    assert days.sum() == 3


def test_calculate_cold_snaps():
    """Test cold snap duration counting."""
    times = pd.date_range("2020-01-01", periods=5, freq="D")
    # Days 0,1 are <=5 (2 days). Day 3 is <=5 (1 day).
    values = [0, 4, 10, -5, 20]

    da = xr.DataArray(values, coords={"time": times}, dims="time", attrs={"units": "degF"})

    snaps_w2 = calculate_cold_snaps(da, threshold_f=5, window_days=2)
    assert snaps_w2.sum() == 2

    snaps_w1 = calculate_cold_snaps(da, threshold_f=5, window_days=1)
    assert snaps_w1.sum() == 3


@pytest.fixture
def sample_data():
    import numpy as np

    times = pd.date_range("2023-01-01", periods=5, freq="h")
    temp = xr.DataArray(
        np.array([25.0, 26.0, 27.0, 28.0, 29.0]), dims="time", coords={"time": times}, attrs={"units": "degC"}
    )
    dew = xr.DataArray(
        np.array([15.0, 16.0, 17.0, 18.0, 19.0]), dims="time", coords={"time": times}, attrs={"units": "degC"}
    )
    u_wind = xr.DataArray(
        np.array([2.0, 3.0, 4.0, 5.0, 6.0]), dims="time", coords={"time": times}, attrs={"units": "m/s"}
    )
    v_wind = xr.DataArray(
        np.array([1.0, 1.0, 1.0, 1.0, 1.0]), dims="time", coords={"time": times}, attrs={"units": "m/s"}
    )
    return temp, dew, u_wind, v_wind


def test_calculate_heat_index_no_explicit_pint_import(sample_data):
    """Verify heat index calculation works without explicit pint-xarray import in the test."""
    temp, dew, _, _ = sample_data
    # This should succeed because climate_indices.py now imports pint_xarray
    hi = calculate_heat_index(temp, dew)
    assert isinstance(hi, xr.DataArray)
    assert hi.attrs.get("units") in ["degF", "°F"]


def test_calculate_wind_chill_no_explicit_pint_import(sample_data):
    """Verify wind chill calculation works without explicit pint-xarray import in the test."""
    temp, _, u, v = sample_data
    # This should succeed because climate_indices.py now imports pint_xarray
    wc = calculate_wind_chill(temp, u, v)
    assert isinstance(wc, xr.DataArray)
    assert wc.attrs.get("units") in ["degF", "°F"]
