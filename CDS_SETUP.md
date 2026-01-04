# CDS API Setup Guide

To download ERA5 data programmatically, you need to set up the Copernicus Climate Data Store (CDS) API.
Check out https://cds.climate.copernicus.eu/how-to-api for more details from CDS (and to get your API key).

## 1. Register for an Account

1.  Go to the [CDS Registration Page](https://cds.climate.copernicus.eu/).
2.  Create an account or log in if you already have one.

## 2. Accept Terms of Use

1.  Ensure you have accepted the Terms of Use for the dataset you want to access (ERA5).
2.  You may need to try downloading a dataset manually from the web interface once to accept the license.

## 3. Get Your API Key

1.  Navigate to your user profile page (usually top right).
2.  Look for your **UID** and **API Key**.

## 4. Configure the API Client

Create a file named `.cdsapirc` in your home directory (`~/.cdsapirc` on macOS/Linux/Unix, or `C:\Users\Username\.cdsapirc` on Windows).

Add the following content, replacing the placeholders with your actual details:

```text
url: https://cds.climate.copernicus.eu/api/v2
key: <UID>:<API_KEY>
```

> [!NOTE]
> The `.cdsapirc` file should be in your home folder, NOT the project folder.

## 5. Verify Setup

Run the provided `download_and_explore.py` script. If it starts downloading (or queues the request), your setup is correct. If you get an authentication error, double-check your `.cdsapirc` file.
