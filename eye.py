from nominatim import NominatimFeature
from extract import ExtractFeature
from render import RenderFeature

class EyeOnDev:
    def __init__(self):
        self.nominatim = NominatimFeature()
        self.extractor = ExtractFeature()
        self.renderer = RenderFeature()

    def run_all(self, url, corrections):
        print("Starting extraction...")
        extract_result = self.extractor.extract(url)
        print(extract_result)

        print("Starting geocoding...")
        geocode_result = self.nominatim.geocode_all(extract_result, corrections)
        print(geocode_result)

        print("Starting rendering...")
        render_result = self.renderer.render(geocode_result)

        return render_result
    
if __name__ == "__main__":
    eod = EyeOnDev()
    url = "https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/"
    corrections = {
        # Example correction
        # "Some Address": {"address": "Corrected Address, Lower Salford, PA", "latitude": 40.123, "longitude": -75.123}
    }
    result = eod.run_all(url, corrections)
    print(result)