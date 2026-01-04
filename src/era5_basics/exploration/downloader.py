import os
import zipfile
import tempfile
import cdsapi
import xarray as xr
from era5_basics.config.settings import LOCATIONS

def get_cds_client() -> cdsapi.Client:
    return cdsapi.Client()

def download_era5_subset(client: cdsapi.Client, area: list[float], output_path: str) -> None:
    
    # Check if we need to download or if we can process an existing zip/file
    if not os.path.exists(output_path):
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': ['2m_temperature', 'total_precipitation'],
                'year': '2023',
                'month': '01',
                'day': [f"{i:02d}" for i in range(1, 32)],
                'time': [f"{i:02d}:00" for i in range(24)],
                'area': area,
            },
            output_path
        )
    else:
        print(f"  > {output_path} already exists. Skipping download.")

    # Post-processing: Check if the file is a ZIP archive (CDS often returns ZIP for mixed variables)
    if zipfile.is_zipfile(output_path):
        print(f"  > Detected ZIP archive. Extracting and merging...")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(output_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find all NetCDF files in the temp directory
                nc_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.nc')]
                
                if not nc_files:
                    print(f"  > Warning: No NetCDF files found in zip {output_path}")
                    return

                # Open and merge all files
                # using combine='by_coords' to merge different variables/streams
                ds = xr.open_mfdataset(nc_files, engine='h5netcdf', combine='by_coords', compat='identical')
                
                # Save as a single NetCDF file, overwriting the zip
                ds.to_netcdf(output_path, engine='h5netcdf')
                print(f"  > Successfully merged {len(nc_files)} files into {output_path}")
                ds.close()
        except Exception as e:
            print(f"  > Error processing zip file: {e}")
    else:
        print(f"  > {output_path} already exists. Skipping unzipping.")

def run_download() -> None:
    client = get_cds_client()
    for name, config in LOCATIONS.items():
        try:
            download_era5_subset(client, config["area"], config["file"])
        except Exception as e:
            print(f"Failed to download {name}: {e}")
            if "licences not accepted" in str(e):
                print("\nACTION REQUIRED: You must accept the ERA5 license at:")
                print("https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download#manage-licences")
