import xarray as xr
from era5_basics.config.settings import LOCATIONS

def explore_netcdf(file_path: str) -> None:
    """Opens a NetCDF file and prints basic statistics and sample data."""
    print(f"\n--- Exploring {file_path} ---")
    try:
        with xr.open_dataset(file_path, engine='h5netcdf') as ds:
            print("\nDataset Info:")
            print(ds)
            
            mid_lat = float(ds.latitude.mean())
            mid_lon = float(ds.longitude.mean())
            
            time_dim = 'valid_time' if 'valid_time' in ds.dims else 'time'
            
            sample = ds.sel(latitude=mid_lat, longitude=mid_lon, method='nearest').isel({time_dim: 0})
            t2m = float(sample['t2m'])
            tp = float(sample['tp'])
            
            print(f"\nSample Point (Lat: {mid_lat:.2f}, Lon: {mid_lon:.2f})")
            print(f"Time: {sample[time_dim].values}")
            print(f"2m Temp: {t2m:.2f} K ({t2m - 273.15:.2f} C)")
            print(f"Total Precip: {tp:.6f} m")
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Run download_data.py first.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def run_exploration() -> None:
    for name, config in LOCATIONS.items():
        explore_netcdf(config["file"])
