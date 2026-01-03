from typing import Any

# Configuration for cities and their small bounding boxes
LOCATIONS: dict[str, dict[str, Any]] = {
    "Chicago": {
        "area": [42.1, -87.8, 41.6, -87.3],
        "file": "era5_chicago_jan2023.nc"
    },
    "NYC": {
        "area": [41.0, -74.2, 40.5, -73.7],
        "file": "era5_nyc_jan2023.nc"
    }
}
