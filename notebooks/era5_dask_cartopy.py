import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Geospatial Learning: ERA5 Data Analysis & Dask Integration

    In this tutorial, we will:
    1.  Load **real ERA5 data** (NetCDF files) for Chicago and NYC.
    2.  Use **Dask** to handle "large" data (lazily loaded).
    3.  Combine multiple datasets into one using `xr.concat`.
    4.  Calculate statistics and create comparative plots.
    """)
    return


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import xarray as xr

    return Path, mo, plt, xr


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 1. Loading Data with Dask

    We have two files in the project root:
    - `era5_chicago_jan2023.nc`
    - `era5_nyc_jan2023.nc`

    We use the `chunks` argument in `open_dataset` to tell Xarray to use **Dask**.
    Even though these files are small, this workflow scales to Terabytes of data.
    """)
    return


@app.cell
def _(Path, xr):
    # Path to the data files (current directory)
    base_dir = Path(".")

    # helper function to load and preprocess
    def load_location_data(filename, city_name):
        ds = xr.open_dataset(
            base_dir / filename,
            engine="h5netcdf",
            chunks={"valid_time": 24},  # Chunk by day (24 hours)
        )
        # Assign a new coordinate "city" to help us combine them later
        return ds.assign_coords(city=city_name)

    ds_chi = load_location_data("era5_chicago_jan2023.nc", "Chicago")
    ds_nyc = load_location_data("era5_nyc_jan2023.nc", "NYC")
    return ds_chi, ds_nyc


@app.cell
def _(ds_chi, mo):
    mo.vstack(
        [
            mo.md("Inspect the Dask array structure. Notice `Values` says 'dask.array' instead of raw numbers."),
            ds_chi.t2m,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2. Combining Datasets

    Instead of working with two separate variables, let's combine them into a single Dataset using `xr.concat`.
    """)
    return


@app.cell
def _(ds_chi, ds_nyc, xr):
    # Concatenate along the 'city' dimension/coordinate we created
    ds = xr.concat([ds_chi, ds_nyc], dim="city")
    ds
    return (ds,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 3. Data Cleaning (Lazy Evaluation)

    We will convert units:
    - **Temperature**: Kelvin -> Celsius
    - **Precip**: Meters -> Millimeters

    Note: Since we are using Dask, these calculations are **lazy**. No data is processed until we plot or explicitly call `.compute()`.
    """)
    return


@app.cell
def _(ds):
    # Create new variables with better units
    # Don't forget to update metadata!

    ds["t2m_c"] = ds.t2m - 273.15
    ds.t2m_c.attrs = ds.t2m.attrs
    ds.t2m_c.attrs["units"] = "degC"
    ds.t2m_c.attrs["long_name"] = "2m Temperature (C)"

    ds["tp_mm"] = ds.tp * 1000
    ds.tp_mm.attrs = ds.tp.attrs
    ds.tp_mm.attrs["units"] = "mm"
    ds.tp_mm.attrs["long_name"] = "Total Precipitation (mm)"

    ds
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 4. Spatially Aggregated Analysis
    """)
    return


@app.cell
def _(ds):
    # Calculate spatial mean for each city at each time step
    # We average over latitude and longitude, visualizing the 'city' difference
    spatial_mean = ds.mean(dim=["latitude", "longitude"])
    spatial_mean
    return (spatial_mean,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Temperature Time Series
    """)
    return


@app.cell
def _(plt, spatial_mean):
    fig, ax = plt.subplots(figsize=(10, 5))

    # Xarray plotting handles the 'city' dimension by creating a legend if we use 'hue'
    spatial_mean.t2m_c.plot(ax=ax, hue="city")

    ax.set_title("ERA5 Hourly Temperature: Chicago vs NYC (Jan 2023)")
    ax.grid(True, alpha=0.3)
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Daily Patterns (GroupBy)
    """)
    return


@app.cell
def _(plt, spatial_mean):
    # Group by hour of day to see diurnal cycle
    daily_cycle = spatial_mean.groupby("valid_time.hour").mean()

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    daily_cycle.t2m_c.plot(ax=ax2, hue="city", marker="o")

    ax2.set_title("Average Diurnal Cycle (Jan 2023)")
    ax2.set_xticks(range(0, 24, 3))
    ax2.grid(True, alpha=0.3)
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Precipitation Accumulation
    """)
    return


@app.cell
def _(plt, spatial_mean):
    # Cumulative sum over time
    precip_accum = spatial_mean.tp_mm.cumsum(dim="valid_time")

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    precip_accum.plot(ax=ax3, hue="city")

    ax3.set_title("Cumulative Precipitation (Jan 2023)")
    ax3.set_ylabel("Accumulated Rain/Snow (mm)")
    ax3.grid(True, alpha=0.3)
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 5. Temporal & Spatial Distributions
    """)
    return


@app.cell
def _(ds):
    # Average across time to get a single map per city
    time_mean = ds.mean(dim="valid_time")
    time_mean
    return (time_mean,)


@app.cell
def _(mo):
    mo.md("""
    ### Distribution of Spatial Averages (Histogram)
    """)
    return


@app.cell
def _(plt, time_mean):
    fig4, ax4 = plt.subplots(figsize=(8, 5))

    # Histogram of average temps across the grid points
    # hue="city" automatically creates distinct histograms
    time_mean.t2m_c.plot.hist(ax=ax4, bins=10, alpha=0.7)

    ax4.set_title("Distribution of Time-Averaged Temperatures over Grid Points")
    ax4.set_xlabel("Temperature (C)")
    plt.gcf()
    return


@app.cell
def _(mo):
    mo.md("""
    ### Spatial Maps of Average Temperature
    """)
    return


@app.cell
def _(ds, plt, time_mean):
    # We plot each city separately because they have different lat/lon ranges
    _cities = ds.city.values
    fig5, _axes = plt.subplots(1, len(_cities), figsize=(12, 5))

    for _ax, _city in zip(_axes, _cities, strict=False):
        # Select data for the specific city
        # dropna removes the nan-filled coordinates from the other city
        _city_data = time_mean.sel(city=_city).dropna(dim="latitude", how="all").dropna(dim="longitude", how="all")

        _city_data.t2m_c.plot(ax=_ax, cmap="RdBu_r")
        _ax.set_title(f"{_city} Average Temp")

    plt.tight_layout()
    plt.gcf()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 6. Mapping with Cartopy

    Since these are geospatial data, we should plot them on a map!

    We use **Cartopy** (a Python mapping library) which integrates with matplotlib.

    ### Concepts: Map Layers
    1.  **Base Layer** (or basemap): The "canvas". e.g. coastlines, borders, roads, land cover, etc. These various geographic features are read as shapefiles (vector format usually generated by GIS software). https://en.wikipedia.org/wiki/Shapefile
    2.  **Data Layer**: Your actual values (Temperature in our case!) painted on top.

    **Projections & Transforms**:
    - **Projection**: How the map is shown on screen (e.g., `PlateCarree` for flat lat/lon, or `Orthographic` for a globe).
    - **Transform**: Tells the code "My data is simple lat/lon points" so it can be wrapped onto whatever projection you choose.

    I suppose you always could ask the LLMs, but in the interest of some nostalgic, old-fashioned learning, I'm linking some additional reading from a course webpage I came across on a Google search that I thought gave a pretty good intro: https://www.atmos.albany.edu/daes/atmclasses/atm350_2025/core/week8/01_Cartopy_Introduction.html
    """)
    return


@app.cell
def _(ds, plt):
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    from geospatial_learning.utils import get_city_extent

    _cities = ds.city.values

    # LAYER 1: The Base Map
    # We create a plot just to show the geography of our region
    fig_base, axes_base = plt.subplots(1, len(_cities), figsize=(12, 5), subplot_kw={"projection": ccrs.PlateCarree()})

    for _ax, _city in zip(axes_base, _cities, strict=False):
        # Add Features (The "Geography")
        _ax.add_feature(cfeature.LAND, facecolor="#e0e0e0")  # Gray land
        _ax.add_feature(cfeature.OCEAN, facecolor="#cceeff")  # Blue ocean
        _ax.add_feature(cfeature.LAKES, facecolor="#cceeff")
        _ax.coastlines(resolution="10m", linewidth=1)
        _ax.add_feature(cfeature.BORDERS, linestyle=":")
        _ax.add_feature(cfeature.STATES, linestyle=":")

        # Limit map area to the relevant lat/lon from our data to zoom in on the area of interest
        if _city == "Chicago":
            _chi_extent = get_city_extent(dataset=ds, city=_city)
            _ax.set_extent(_chi_extent)
        elif _city == "NYC":
            _nyc_extent = get_city_extent(dataset=ds, city=_city)
            _ax.set_extent(_nyc_extent)

        _ax.set_title(f"{_city} Base Map (Context)")

    plt.tight_layout()
    plt.gcf()
    return ccrs, cfeature


@app.cell
def _(ccrs, cfeature, ds, plt, time_mean):
    _cities = ds.city.values

    # LAYER 2: Data Overlay
    fig6, axes = plt.subplots(1, len(_cities), figsize=(12, 5), subplot_kw={"projection": ccrs.PlateCarree()})

    for _ax, _city in zip(axes, _cities, strict=False):
        # Select data
        _city_data = time_mean.sel(city=_city).dropna(dim="latitude", how="all").dropna(dim="longitude", how="all")

        # 1. Draw minimal context
        _ax.coastlines(linewidth=1.2, color="black")  # Thicker coastlines for visibility
        _ax.add_feature(cfeature.BORDERS, linestyle=":", alpha=0.5)
        _ax.add_feature(cfeature.STATES, linestyle=":", alpha=0.5)

        # 2. Paint Data
        # transform=ccrs.PlateCarree() is CRITICAL.
        _city_data.t2m_c.plot(
            ax=_ax,
            cmap="RdBu_r",
            transform=ccrs.PlateCarree(),
            cbar_kwargs={"shrink": 0.7, "label": "Temp (C)"},
            alpha=0.3,  # Slight transparency to see major geographic features if needed
        )

        _ax.set_title(f"{_city} Average Temp (Overlay)")

    plt.tight_layout()
    plt.gcf()
    return


if __name__ == "__main__":
    app.run()
