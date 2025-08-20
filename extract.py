import requests
from bs4 import BeautifulSoup
import re
import json

class ExtractFeature:
    def extract(self, 
                url="https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/"):
        # Step 1: Load the page
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Step 2: Navigate to the new content block
        content = soup.select_one("div.row.grid-row div.grid-wide.grid-content")
        if not content:
            raise Exception("Could not find main content block.")

        # Step 3: Define categories
        categories = {
            "Under Review: Planning Commission": [],
            "Under Review: Board of Supervisors": [],
            "Approved": [],
            "Under Construction": []
        }

        # Step 4: Address parsing helper
        street_types = [
            "St", "Street", "Ave", "Avenue", "Rd", "Road", "Ln", "Lane", "Pike", "Pk",
            "Dr", "Drive", "Ct", "Court", "Blvd", "Way", "Circle", "Cir", "Terrace"
        ]
        street_pattern = re.compile(rf"^(.+?\b(?:{'|'.join(street_types)})\b)[\.\s]*(.*)$")

        def split_entry(text):
            match = street_pattern.match(text.strip())
            if match:
                address, description = match.groups()
                return {
                    "key": text,
                    "address": address.strip(),
                    "description": description.strip()
                }
            else:
                return {
                    "key": text,
                    "address": "",
                    "description": text.strip()
                }

        # Step 5: Parse the new structure
        # Find all <ol> blocks directly under grid-content
        ols = content.find_all("ol", recursive=False)
        for ol in ols:
            # Each <li> in top-level <ol> is a category
            for li in ol.find_all("li", recursive=False):
                strong = li.find("strong")
                if not strong:
                    continue
                category_text = strong.get_text(strip=True)
                # Under Review is special: has subcategories
                if "Under Review" in category_text:
                    ul = li.find("ul")
                    if ul:
                        for subli in ul.find_all("li", recursive=False):
                            substrong = subli.find("strong")
                            if not substrong:
                                continue
                            subcat_text = substrong.get_text(strip=True)
                            subol = subli.find("ol")
                            if subol:
                                for entry_li in subol.find_all("li", recursive=False):
                                    entry = entry_li.get_text(strip=True)
                                    if "Planning Commission" in subcat_text:
                                        categories["Under Review: Planning Commission"].append(split_entry(entry))
                                    elif "Board of Supervisors" in subcat_text:
                                        categories["Under Review: Board of Supervisors"].append(split_entry(entry))
                elif "Approved" in category_text:
                    ul = li.find("ul")
                    if ul:
                        for entry_li in ul.find_all("li", recursive=False):
                            entry = entry_li.get_text(strip=True)
                            categories["Approved"].append(split_entry(entry))
                elif "Under Construction" in category_text:
                    ul = li.find("ul")
                    if ul:
                        for entry_li in ul.find_all("li", recursive=False):
                            entry = entry_li.get_text(strip=True)
                            categories["Under Construction"].append(split_entry(entry))

        # Step 6: Output structured JSON
        with open("development_entries.json", "w") as f:
            json.dump(categories, f, indent=2)

        return categories

if __name__ == "__main__":
    extractor = ExtractFeature()
    result = extractor.extract()
    print(json.dumps(result, indent=2))