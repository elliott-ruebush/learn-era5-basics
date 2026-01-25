import marimo

__generated_with = "0.19.6"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    ∑Before jumping into reading any actual data, let's take a brief moment for an overview of some of the cool tooling out there for efficiently teasing out answers to big geospatial data problems without needing an [AWS Snowmobile](https://aws.amazon.com/blogs/aws/aws-snowmobile-move-exabytes-of-data-to-the-cloud-in-weeks/)* truck's trove of hard-drives to store the data on

    ## What is ARCO ([Article by Lobelia Earth](https://blog.lobelia.earth/arco-the-smartest-way-to-access-big-geospatial-data-eaf689eff3c9))
    One of the acronyms that's gaining a lot of hype in the geospatial community these days is ARCO, which stands for Analysis-Ready, Cloud-Optimized.
    ### Analysis-Ready (AR)
    Analysis-ready means that the data is cleaned, standardized, and ready to answer whatever research or business questions your heart desires.
    * Dealing with non-AR data might involve processing raw satellite data, doing geographic projections, or merging non-uniform datasets.
    * Dealing with AR data in a geospatial context means you can expect standard variables, time-scales, and latitude/longitude (and perhaps pressure levels in an atmospheric context).

    ### Cloud-Optimized (CO)
    Cloud-optimized means that the data is stored in a format that makes data retrieval and processing across various different dimensions efficient.
    #### Zarr and friends!
    * A popular file format for cloud-optimized geospatial data is [Zarr](https://zarr.dev/), which structures "cubes" of data into smaller "chunks". E.g. if I have a 8x8 cube of data, I can decompose it into four 4x4 chunks. This generalizes to higher dimensions and meshes well with object storage systems common to cloud providers (e.g. Amazon S3).
    * To further converge on an ecosystem where everything is cloud-optimized Zarr datacubes, one can make use of [VirtualiZarr](https://virtualizarr.readthedocs.io/en/stable/) (or its spiritual predecessor [Kerchunk](https://fsspec.github.io/kerchunk/)) to create "virtual" (zero-copy!) Zarr datacubes with chunks pointing directly to the relevant bytes of various other file formats like NetCDF, GRIB, and HDF5.
      * This virtual Zarr abstraction is powerful because it lets you build towards a unified cloud-native interface even when working with various different datasources that might not have the capability to migrate their source data to a cloud-native format.
      * Question to ponder: what about going the opposite way? What if I'm running legacy systems that expect different input formats? Can I cheaply convert Zarr to NetCDF and then run a model that expects NetCDF inputs?
    * A relatively new option to further productionize cloud-optimized datacubes as a first-class database is an open-source technology called [Icechunk](https://icechunk.io/en/stable/overview/) which provides commit history and transaction guarantees. This is important because it makes auditing changes and executing rollbacks possible. Icechunk plays nicely alongside virtual Zarr files too. If I have an operational forecasting system, I'd ideally want my data to be robust to issues with models, partial failures, and the general suite of data integrity problems one can expect when running something in the real world.


    \* *sidenote: where are these AWS Snowmobile trucks living these days...? And is a multi-petabyte climate-controlled storage container a valid combined winter camping/winter weather modeling setup...?*
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Geospatial Data Levels ([NASA EOS Article](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/data-processing-levels))
    What kinds of geospatial data are out there? How do we get from a satellite orbiting the earth and broadcasting some sensor outputs to a prediction for the temperature in Chicago tomorrow?

    There are obviously whole fields of science and modeling behind that second question, but let's think briefly about the hierarchy of geospatial data to start. NASA clearly outlines the generally accepted levels in an article from their Earth Observing System (EOS) team. Below are my brief attempts at summarizing each level (see NASA's article for a more robust explanation).
    #### Level 0
    Straight-up bytes in a signal from your favorite satellite
    #### Level 1
    Raw sensor with a few annotations/adjustments
    #### Level 2
    Raw data, but converted to geophysical variables (e.g. your L1 thermal infrared sensor output could be converted to a temperature value)
    #### Level 3
    Geophysical variables on a nice, uniform grid and timescale. Friendly level for analysis!
    #### Level 4
    Derived or modeled output based on lower level data
    """)
    return


@app.cell
def _():
    import os
    import tempfile
    import zipfile
    from pathlib import Path

    import cdsapi
    import marimo as mo
    import matplotlib.pyplot as plt
    import xarray as xr

    # Configuration
    CHI_LAT, CHI_LON = 41.88, -87.63
    NYC_LAT, NYC_LON = 40.75, -74
    return (
        CHI_LAT,
        CHI_LON,
        NYC_LAT,
        NYC_LON,
        Path,
        cdsapi,
        mo,
        os,
        plt,
        tempfile,
        xr,
        zipfile,
    )


@app.cell
def _(mo):
    mo.md("""
    ## 1. Spatial Snapshot (Global/Regional Map)
    **Source:** Google ARCO Zarr (Analysis Ready)
    **Link:** [Google Cloud Public Datasets](https://cloud.google.com/storage/docs/public-datasets/era5)

    **Scenario:** You need a map of the entire US for *one specific hour*.

    **Research Starter:**
    *   **Coordinates**: ERA5 uses `[0, 360)` for longitude. To get US coordinates (e.g., -87°), you calculate `360 - 87 = 273°`.
    *   **Performance**: Why does the first run take ~1 minute? (Hint: Check the size of the consolidated metadata file and the startup cost of a GCS handshake).
    *   **Metadata alternatives**: If you only need one variable, can you open it directly without the root `.zmetadata`? (See the 'Direct Variable' example below).
    """)
    return


@app.cell
def _(xr):
    # Single Level Forecast
    # This dataset contains single-level forecast fields on ERA5's native reduced Gaussian grid.
    ds = xr.open_zarr(
        "gs://gcp-public-data-arco-era5/co/single-level-forecast.zarr-v2/",
        chunks=None,
        storage_options={"token": "anon"},
        decode_timedelta=False,
    )
    single_level_forecasts = ds.sel(time=slice(ds.attrs["valid_time_start"], ds.attrs["valid_time_stop"]))
    return (single_level_forecasts,)


@app.cell
def _(single_level_forecasts):
    single_level_forecasts
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Temporal Deep Dive (Long History)
    **Source:** CDS Timeseries (Beta)
    **Link:** [CDS ERA5 Timeseries](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-timeseries)

    **Scenario:** You need 40 years of temperature history for *one specific point* (e.g., Chicago O'Hare).

    **Research Starter:**
    *   How does this dataset's internal structure differ from the Google ARCO one?
    *   Why is this "point retrieval" so much faster than downloading NetCDF files?
    """)
    return


@app.cell
def _(
    CHI_LAT,
    CHI_LON,
    NYC_LAT,
    NYC_LON,
    Path,
    cdsapi,
    os,
    tempfile,
    xr,
    zipfile,
):
    # NOTE: Requires ~/.cdsapirc file to be configured
    client = cdsapi.Client()

    def fetch_point_history(lat: float, lon: float, start_year: int, end_year: int):
        output_dir = Path("data/era5")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"timeseries_{lat}_{lon}_{start_year}_{end_year}.nc"
        output_path = output_dir / filename

        if output_path.exists():
            return xr.open_dataset(output_path)

        dataset = "reanalysis-era5-single-levels-timeseries"
        request = {
            "location": {"latitude": lat, "longitude": lon},
            "variable": ["2m_temperature"],
            "date": f"{start_year}-01-01/{end_year}-12-31",
            "format": "netcdf",
        }

        # This triggers the remote fetch
        result = client.retrieve(dataset, request)
        result.download(output_path)

        # Check if the result is a ZIP archive
        if zipfile.is_zipfile(output_path):
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(output_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Find NetCDF files
                nc_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".nc")]
                if not nc_files:
                    raise FileNotFoundError(f"No NetCDF files found in downloaded zip: {output_path}")

                # Merge if multiple, otherwise open single
                if len(nc_files) > 1:
                    ds = xr.open_mfdataset(nc_files, combine="by_coords")
                else:
                    ds = xr.open_dataset(nc_files[0])

                # Save as a clean NetCDF and overwrite the ZIP
                ds.to_netcdf(output_path)
                return ds

        return xr.open_dataset(output_path)

    # Button to execute (prevents accidental API hits on load)
    # Uncomment to run:
    chi_ds = fetch_point_history(CHI_LAT, CHI_LON, 1983, 2023)
    nyc_ds = fetch_point_history(NYC_LAT, NYC_LON, 1983, 2023)
    return chi_ds, nyc_ds


@app.cell
def _(chi_ds, nyc_ds):
    def add_t2m_c_from_t2m_k(ds):
        ds["t2m_c"] = ds.t2m - 273.15
        ds.t2m_c.attrs = ds.t2m.attrs
        ds.t2m_c.attrs["units"] = "degC"
        ds.t2m_c.attrs["long_name"] = "2m Temperature (C)"

    add_t2m_c_from_t2m_k(chi_ds)
    add_t2m_c_from_t2m_k(nyc_ds)
    return


@app.cell
def _(chi_ds, plt):
    # Plotting with xarray
    plt.figure(figsize=(10, 5))
    chi_ds["t2m_c"].plot()
    plt.title("40-Year History: Chicago (CDS Timeseries)")
    plt.show()
    return


@app.cell
def _(nyc_ds, plt):
    # Plotting with xarray
    plt.figure(figsize=(10, 5))
    nyc_ds["t2m_c"].plot()
    plt.title("40-Year History: NYC (CDS Timeseries)")
    plt.show()
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3. Spatiotemporal Hybrid (Regional Cube)
    **Source:** Traditional NetCDF (CDS API)
    **Link:** [CDS ERA5 Single Levels](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels)

    **Scenario:** You need a full year of data for a city's metro area (Lat x Lon x Time).

    **Research Starter:**
    *   Why is "downloading a file" sometimes better than streaming?
    *   What happens to your local disk space if you try to do this for the whole globe?
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    *Reference implementation for this pattern is in `src/era5_basics/scripts/downloader.py`*
    """)
    return


if __name__ == "__main__":
    app.run()
