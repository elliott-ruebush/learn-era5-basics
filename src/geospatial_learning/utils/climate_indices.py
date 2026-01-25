"""
Climate index calculation utilities for geospatial analysis.

This module provides wrappers around MetPy and xclim to calculate:
- Heat Index (NWS formula)
- Wind Chill (NWS formula)
- Heat Wave Index (Customizable threshold)
- Cold Snap Index (Customizable threshold)
"""

import metpy.calc as mpcalc
import xarray as xr
from xclim.indices import cold_spell_total_length, hot_spell_total_length


def _to_degf_dataarray(data) -> xr.DataArray:
    """Convert MetPy output (Quantity or DataArray) to a clean DataArray in °F."""
    if hasattr(data, "pint"):
        return data.pint.to("degF").pint.dequantify()
    return data.to("degF")


def _ensure_dequantified(da: xr.DataArray, default_units: str = "degF") -> xr.DataArray:
    """Ensure DataArray is dequantified and has units attribute for xclim."""
    if hasattr(da, "pint"):
        return da.pint.dequantify()

    if "units" not in da.attrs:
        da.attrs["units"] = default_units
    return da


def calculate_heat_index(temperature: xr.DataArray, dewpoint: xr.DataArray) -> xr.DataArray:
    """
    Calculate the Heat Index using MetPy's implementation of the NWS formula.

    Args:
        temperature: Air temperature (requires units, preferably degC or degF)
        dewpoint: Dewpoint temperature (requires units, preferably degC or degF)

    Returns:
        DataArray containing Heat Index in degrees Fahrenheit.
    """
    rh = mpcalc.relative_humidity_from_dewpoint(temperature, dewpoint)
    hi = mpcalc.heat_index(temperature, rh, mask_undefined=False)

    return _to_degf_dataarray(hi)


def calculate_wind_chill(temperature: xr.DataArray, u_wind: xr.DataArray, v_wind: xr.DataArray) -> xr.DataArray:
    """
    Calculate Wind Chill Temperature using MetPy's NWS formula.

    Args:
        temperature: Air temperature
        u_wind: U-component of wind speed
        v_wind: V-component of wind speed

    Returns:
        DataArray containing Wind Chill in degrees Fahrenheit.
        Returns Air Temperature if wind < 3mph or Temp > 50F (standard NWS rules).
    """
    wind_speed = mpcalc.wind_speed(u_wind, v_wind)
    wc = mpcalc.windchill(temperature, wind_speed, mask_undefined=False)

    return _to_degf_dataarray(wc)


def calculate_heat_waves(heat_index: xr.DataArray, threshold_f: float = 95.0, window_days: int = 2) -> xr.DataArray:
    """
    Calculate number of heat wave days per year based on a threshold and duration window.

    Uses `xclim.indices.hot_spell_total_length`.

    Args:
        heat_index: DataArray of daily maximum heat index (in degF)
        threshold_f: Temperature threshold in F (default 95.0)
        window_days: Minimum duration of the wave in days (default 2)

    Returns:
        DataArray with annual count of heat wave days.
    """
    thresh_str = f"{threshold_f} degF"
    da = _ensure_dequantified(heat_index)

    return hot_spell_total_length(da, thresh=thresh_str, window=window_days, freq="YS")


def calculate_cold_snaps(
    apparent_temp_daily_mean: xr.DataArray, threshold_f: float = 5.0, window_days: int = 1
) -> xr.DataArray:
    """
    Calculate number of cold snap days per year based on a threshold and duration window.

    Uses `xclim.indices.cold_spell_total_length` (which typically expects mean daily temperature).

    Definition: Days where the Apparent Temperature (Temp or Wind Chill)
    fails to or below, the threshold.

    Args:
        apparent_temp_daily_mean: Daily mean apparent temp (Wind Chill / Temp) in degF
        threshold_f: Threshold in F (default 5.0)
        window_days: Minimum duration to count (default 1 for "any day with T <= 5F")

    Returns:
        DataArray with annual count of cold snap days.
    """
    thresh_str = f"{threshold_f} degF"
    da = _ensure_dequantified(apparent_temp_daily_mean)

    return cold_spell_total_length(da, thresh=thresh_str, window=window_days, freq="YS")
