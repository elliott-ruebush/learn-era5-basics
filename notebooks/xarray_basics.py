import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import xarray as xr

    return mo, np, pd, plt, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Xarray Basics: An Interactive Tutorial

    Welcome! Since you're familiar with **pandas** and **polars**, you already have a strong foundation.

    Think of **Xarray** as "pandas for N-dimensional arrays".

    - **Pandas** excels at 2D tabular data (rows and columns).
    - **Xarray** excels at N-D data (e.g., latitude, longitude, time, level).

    In this tutorial, we'll explore:
    1.  **DataStructures**: DataArray vs Dataset
    2.  **Coordinates & Dimensions**: The semantic labels that make xarray powerful
    3.  **Indexing**: `sel` vs `isel`
    4.  **Computation**: Broadcasting
    5.  **Grouping**: Split-Apply-Combine (`groupby`)
    6.  **Filtering**: Selection with `where`
    7.  **Merging**: Combining datasets
    8.  **Plotting**: Quick visualizations
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. Data Structures

    ### The `DataArray`
    The core building block. It's like a labeled numpy array.

    Let's create some synthetic temperature data for 1 year (365 days) across a small grid of 2 latitudes and 2 longitudes.
    """)
    return


@app.cell
def _(np, pd, xr):
    # Create fake data
    data = np.random.rand(365, 2, 2) * 20 + 10  # Temps between 10C and 30C

    # Create coords
    times = pd.date_range("2024-01-01", periods=365)
    lats = [40, 41]
    lons = [-100, -99]

    # Create DataArray
    temperature = xr.DataArray(
        data,
        coords={"time": times, "lat": lats, "lon": lons},
        dims=("time", "lat", "lon"),
        name="temperature",
        attrs={"units": "degC"},  # Metadata is first-class citizen!
    )
    return (temperature,)


@app.cell
def _(mo, temperature):
    mo.vstack(
        [
            mo.md("Inspect the object below. Note you can click the disk icon to verify values and metadata."),
            temperature,
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ### The `Dataset`
    A `Dataset` is like a Python dictionary of `DataArray`s (variables) that share coordinates.

    **Analogy**:
    - `DataArray` $pprox$ `pd.Series` (but N-dim)
    - `Dataset` $pprox$ `pd.DataFrame`
    """)
    return


@app.cell
def _(np, temperature, xr):
    # Add a second variable: Precipitation (sharing same coords!)
    precip_data = np.random.rand(365, 2, 2) * 5
    precipitation = xr.DataArray(
        precip_data,
        dims=("time", "lat", "lon"),
        name="precipitation",
        attrs={"units": "mm"},
    )

    # Combine into a Dataset
    ds = xr.Dataset({"temperature": temperature, "precipitation": precipitation})

    # You can also add attributes to the whole dataset
    ds.attrs["description"] = "Synthetic weather data"
    return (ds,)


@app.cell
def _(ds):
    ds
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. Indexing: Labels > Positions

    This is where Xarray shines. You rarely need to know "index 0" or "index 5". You use the coordinate values.

    - `.sel(dim=label)`: Select by value (like pandas `.loc`)
    - `.isel(dim=index)`: Select by integer position (like pandas `.iloc`)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Positional Indexing (`isel`)
    """)
    return


@app.cell
def _(ds):
    # Get the first time step
    ds.isel(time=0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Label-based Indexing (`sel`)
    """)
    return


@app.cell
def _(ds):
    # Get data for a specific date
    ds.sel(time="2024-01-02")
    return


@app.cell(hide_code=True)
def _(ds, mo):
    mo.md(f"""
    ### Nearest Match Selection

    Just like pandas `asof` joins or indexing, xarray handles "nearest" matches easily.

    Requesting lat=40.8 (which doesn't exist, we have 40 and 41):

    `ds.sel(lat=40.8, method="nearest")` returns lat={ds.sel(lat=40.8, method="nearest").lat.values}
    """)
    return


@app.cell
def _(ds, mo):
    date_slider = mo.ui.slider(0, ds.sizes["time"] - 1, label="Select Time Step (isel index)")
    return (date_slider,)


@app.cell
def _(date_slider, ds, mo):
    # Interactive slice
    selected_slice = ds.isel(time=date_slider.value)

    mo.vstack(
        [
            date_slider,
            mo.md(
                f"**Showing data for time index: {date_slider.value}** ({ds.time[date_slider.value].dt.strftime('%Y-%m-%d').item()})"
            ),
            selected_slice,
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Computation & Broadcasting

    Operations in xarray vectorize over dimensions names. You don't need to align arrays manually.
    """)
    return


@app.cell
def _(ds):
    # Calculate Mean temperature over time
    # Notice we identify the dimension by NAME, not axis=0
    mean_temp = ds.temperature.mean(dim="time")
    mean_temp
    return (mean_temp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    **Broadcasting**:
    If we subtract the mean (2D: lat, lon) from the original (3D: time, lat, lon), Xarray handles the alignment automatically.
    """)
    return


@app.cell
def _(ds, mean_temp):
    anomaly = ds.temperature - mean_temp
    anomaly
    return (anomaly,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Grouping & Resampling
    """)
    return


@app.cell
def _(ds):
    # Group by month and calculate mean
    monthly_means = ds.groupby("time.month").mean()
    monthly_means
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Filtering & Selection

    Use `.where()` to filter data based on conditions.
    """)
    return


@app.cell
def _(ds):
    # Keep only data where temperature > 15 degrees
    # Values not meeting the condition become NaN (unless drop=True is used)
    warm_days = ds.where(ds.temperature > 15)
    warm_days
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Merging & Joining

    You can combine multiple DataArrays or Datasets.
    """)
    return


@app.cell
def _(ds, np, xr):
    # Create a new DataArray with the same coordinates
    wind_data = xr.DataArray(
        np.random.rand(365, 2, 2) * 10,
        coords=ds.coords,
        name="wind_speed",
        attrs={"units": "m/s"},
    )

    # Merge into the existing dataset
    ds_extended = xr.merge([ds, wind_data])
    ds_extended
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 7. Plotting
    """)
    return


@app.cell
def _(anomaly, mo, plt):
    mo.md("Xarray wraps matplotlib. Simple plots are one line of code.")

    # Simple histogram of all values
    fig, ax = plt.subplots(figsize=(6, 4))
    anomaly.plot.hist(ax=ax)
    ax.set_title("Temperature Anomalies Distribution")
    plt.gcf()
    return


@app.cell
def _(ds, plt):
    # 2D Map plot for the first time step
    fig2, ax2 = plt.subplots(figsize=(6, 4))

    ds.temperature.isel(time=0).plot(ax=ax2)
    ax2.set_title("Temp Map (Time 0)")
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 8. Next Steps

    - **IO**: Use `xr.open_dataset('file.nc')` to read NetCDF or GRIB files (like ERA5 data!).
    - **Dask**: Xarray integrates with Dask for parallel computing on datasets larger than memory.
    - **Documentation**: [https://docs.xarray.dev/en/stable/](https://docs.xarray.dev/en/stable/)
    """)
    return


if __name__ == "__main__":
    app.run()
