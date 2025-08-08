# Eye on Development

## Overview 

These scripts will scrape the Lower Salford Township page [Eye on Development](https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/) for locations in various states of the process of devlopment, make a best-effort attempt at GPS location, and render a map of the township with borders and basemap tiles including marked locations of development color coded by process stage.

## How to Use

Using Python 3:

Load necessary modules from `requirements.txt` with

`pip install -r requirements.txt`

Use Python 3 to run the following files:

`python3 extract.py > development_entries.json` 

This will scrape the Eye on Development page and save to a file called `development_entries.json`.

`python3 nominatim.py`

This will load the file `development_entries.json` and politely request the longitude and latitude of the addresses inside it from nominatim.openstreetmap.org. It will output file with this information to `development_entries_geocoded.json`.

`python3 render.py`

This will load the file `lower_salford_boundary.geojson` (included in this repository or you can grab from https://overpass-turbo.eu/ using the `overpass.txt` file) and `development_entries_geocoded.json` and combine the two into a JPG output of `development_map_with_basemap.jpg`.

The resulting file should look something like the included sample below:

![Development Map with Basemap](sample_map.jpg)

## Troubleshooting Notes

On Mac OS the `pyproj` library may require running `brew install proj` first. If Homebrew is not installed, consult the installation instructions for that.