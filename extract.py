import requests
from bs4 import BeautifulSoup
import re
import json

# Step 1: Load the page
url = "https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/"
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Navigate to the structured content block
content = soup.select_one("div#a-content div#c-article div.grid-wide.grid-content")

# Step 3: Define categories and containers
categories = {
    "A. Under Review: Planning Commission": [],
    "A. Under Review: Board of Supervisors": [],
    "B. Approved": [],
    "C.  Under Construction": []
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
            "address": f"{address.strip()}, Lower Salford, PA 19438",
            "description": description.strip()
        }
    else:
        return {
            "address": "",
            "description": text.strip()
        }

# Step 5: Parse sections
current_category = None
for tag in content.find_all(['p', 'ul']):
    text = tag.get_text(strip=True)

    if text.startswith("A. Under Review"):
        current_category = "A. Under Review: Planning Commission"
        continue
    elif text.startswith("B") and "Approved" in text:
        current_category = "B. Approved"
        continue
    elif text.startswith("C") and "Under Construction" in text:
        current_category = "C.  Under Construction"
        continue

    if tag.name == 'ul' and current_category:
        for li in tag.find_all('li', recursive=False):
            subitems = li.find_all('li')
            if subitems:
                label = li.find('strong')
                if label and "Supervisor" in label.get_text():
                    current_category = "A. Under Review: Board of Supervisors"
                elif label and "Planning" in label.get_text():
                    current_category = "A. Under Review: Planning Commission"

                for subli in subitems:
                    entry = subli.get_text(strip=True)
                    categories[current_category].append(split_entry(entry))
            else:
                entry = li.get_text(strip=True)
                categories[current_category].append(split_entry(entry))

# Step 6: Output structured JSON
print(json.dumps(categories, indent=2))
