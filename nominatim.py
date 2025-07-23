import json
import requests
import time

# Load the JSON from the previous output
with open("development_entries.json", "r") as f:
    data = json.load(f)

# Geocoding function using OSM Nominatim
def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 0,
        "limit": 1
    }
    headers = {
        "User-Agent": "LowerSalfordGeocoderBot/1.0 (your_email@example.com)"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            return {
                "lat": float(results[0]["lat"]),
                "lon": float(results[0]["lon"])
            }
    return {"lat": None, "lon": None}

# Loop over all entries and append lat/lon
for category, entries in data.items():
    for entry in entries:
        coords = geocode(entry["address"])
        entry["latitude"] = coords["lat"]
        entry["longitude"] = coords["lon"]
        print(f"Geocoded: {entry['address']} → {coords}")
        time.sleep(1)  # Be polite and throttle your requests!

# Save results to a new file
with open("development_entries_geocoded.json", "w") as f:
    json.dump(data, f, indent=2)
