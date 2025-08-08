import json
import requests
import time
import os

class NominatimFeature:
    """
    Geocoding helper using OSM Nominatim, with support for manual corrections and caching.
    """

    def __init__(self,
                 entries_file="development_entries.json",
                 output_file="development_entries_geocoded.json",
                 township_suffix="Lower Salford, PA 19438",
                 user_agent="LowerSalfordGeocoderBot/1.0 (your_email@example.com)"):
        self.entries_file = entries_file
        self.output_file = output_file
        self.township_suffix = township_suffix
        self.headers = {"User-Agent": user_agent}

    def geocode(self, address, cache=None):
        """
        Query Nominatim for a given address, using cache if available.
        """
        # Try cache first
        if cache:
            for cached_entry in cache.values():
                if cached_entry.get("address") == address and \
                   cached_entry.get("latitude") is not None and \
                   cached_entry.get("longitude") is not None:
                    print(f"Used cached geocode for '{address}': {cached_entry['latitude']}, {cached_entry['longitude']}")
                    return {"lat": cached_entry["latitude"], "lon": cached_entry["longitude"]}
        # Otherwise, geocode
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "addressdetails": 0, "limit": 1}
        resp = requests.get(url, params=params, headers=self.headers)
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return {"lat": float(results[0]["lat"]), "lon": float(results[0]["lon"])}
        return {"lat": None, "lon": None}

    def geocode_all(self, entries=[], corrections=[]):
        """
        Load entries, apply corrections, geocode missing coords, and save output.
        Uses cached geocoded results if available for matching keys.
        """
        # Load geocoded cache if available
        geocoded_cache = {}
        if os.path.exists(self.output_file):
            with open(self.output_file) as of:
                cached_data = json.load(of)
                for category, cached_entries in cached_data.items():
                    for entry in cached_entries:
                        key = entry.get("key")
                        if key:
                            geocoded_cache[key] = entry

        # Load current entries
        with open(self.entries_file) as ef:
            data = json.load(ef)

        self.correction_map = {c["key"]: c for c in corrections}

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

                # If cached geocoded coords for this key, use them
                cached = geocoded_cache.get(key)
                if cached and cached.get("latitude") is not None and cached.get("longitude") is not None:
                    entry["latitude"] = cached["latitude"]
                    entry["longitude"] = cached["longitude"]
                    entry["address"] = cached.get("address", entry.get("address"))
                    print(f"Used cached coords for '{key}': {entry['latitude']}, {entry['longitude']}")
                    continue

                # If manual address override, apply it
                if corr.get("address"):
                    orig = entry.get("address")
                    entry["address"] = corr["address"]
                    print(f"Overrode address for '{key}': '{orig}' -> '{entry['address']}'")

                entry["address"] = f"{entry['address']} {self.township_suffix}"

                # Geocode using Nominatim (with cache by address)
                coords = self.geocode(entry["address"], cache=geocoded_cache)
                entry["latitude"] = coords.get("lat")
                entry["longitude"] = coords.get("lon")
                print(f"Geocoded: {entry['address']} -> {coords}")
                time.sleep(1)  # throttle

        # Save results
        with open(self.output_file, "w") as of:
            json.dump(data, of, indent=2)

        return data

if __name__ == "__main__":
    nf = NominatimFeature()
    result = nf.geocode_all()
    print(result)
