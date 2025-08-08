import json
import requests
import time

class NominatimFeature:
    """
    Geocoding helper using OSM Nominatim, with support for manual corrections.
    """

    def __init__(self,
                 entries_file="development_entries.json",
                 corrections_file="development_corrections.json",
                 output_file="development_entries_geocoded.json",
                 township_suffix="Lower Salford, PA 19438",
                 user_agent="LowerSalfordGeocoderBot/1.0 (your_email@example.com)"):
        self.entries_file = entries_file
        self.corrections_file = corrections_file
        self.output_file = output_file
        self.township_suffix = township_suffix
        self.headers = {"User-Agent": user_agent}

        # Load corrections and index by entry key
        try:
            with open(self.corrections_file) as cf:
                corrections = json.load(cf)
        except FileNotFoundError:
            corrections = []
        self.correction_map = {c["key"]: c for c in corrections}

    def geocode(self, address):
        """
        Query Nominatim for a given address.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "addressdetails": 0, "limit": 1}
        resp = requests.get(url, params=params, headers=self.headers)
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}
        return {"lat": None, "lon": None}

    def geocode_all(self):
        """
        Load entries, apply corrections, geocode missing coords, and save output.
        """
        # Load entries
        with open(self.entries_file) as ef:
            data = json.load(ef)

        # Process each entry
        for category, entries in data.items():
            for entry in entries:
                key = entry.get("key")
                corr = self.correction_map.get(key, {})

                # If manual lat/lon provided, use and skip geocoding
                if corr.get("latitude") is not None and corr.get("longitude") is not None:
                    entry["latitude"] = corr["latitude"]
                    entry["longitude"] = corr["longitude"]
                    print(f"Applied manual coords for '{key}': {entry['latitude']}, {entry['longitude']}")
                    continue

                # If manual address override, apply it
                if corr.get("address"):
                    orig = entry.get("address")
                    entry["address"] = corr["address"]
                    print(f"Overrode address for '{key}': '{orig}' -> '{entry['address']}'")

                entry["address"] = f"{entry["address"]} {self.township_suffix}"

                # Geocode using Nominatim
                coords = self.geocode(entry["address"])
                entry["latitude"] = coords.get("lat")
                entry["longitude"] = coords.get("lon")
                print(f"Geocoded: {entry['address']} -> {coords}")
                time.sleep(1)  # throttle

        # Save results
        with open(self.output_file, "w") as of:
            json.dump(data, of, indent=2)

        return {"result": f"Saved to {self.output_file}"}

if __name__ == "__main__":
    nf = NominatimFeature()
    result = nf.geocode_all()
    print(result)
