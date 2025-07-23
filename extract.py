import requests
from bs4 import BeautifulSoup
import json

url = "https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/"

# Step 1: Load the page
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Step 2: Find the main content area
content = soup.select_one("div#a-content div#c-article div.grid-wide.grid-content")

# Step 3: Set up category parsing
categories = {
    "A. Under Review: Planning Commission": [],
    "A. Under Review: Board of Supervisors": [],
    "B. Approved": [],
    "C.  Under Construction": []
}

current_category = None
in_under_review = False
planning_count = 0
supervisors_count = 0

for tag in content.find_all(['p', 'ul']):
    text = tag.get_text(strip=True)

    # Detect which section we're in
    if text.startswith("A. Under Review"):
        in_under_review = True
        current_category = "A. Under Review: Planning Commission"
        continue
    elif text.startswith("B") and "Approved" in text:
        in_under_review = False
        current_category = "B. Approved"
        continue
    elif text.startswith("C") and "Under Construction" in text:
        in_under_review = False
        current_category = "C.  Under Construction"
        continue

    if tag.name == 'ul' and current_category:
        for li in tag.find_all('li', recursive=False):
            # Check if <ol> exists inside this <li> (Planning/Board split)
            subitems = li.find_all('li')
            if subitems:
                label = li.find('strong')
                if label and "Supervisor" in label.get_text():
                    current_category = "A. Under Review: Board of Supervisors"
                elif label and "Planning" in label.get_text():
                    current_category = "A. Under Review: Planning Commission"

                for subli in subitems:
                    entry = subli.get_text(strip=True)
                    categories[current_category].append(entry)
            else:
                # Regular item (non-nested)
                entry = li.get_text(strip=True)
                categories[current_category].append(entry)

# Step 4: Output as pretty JSON
print(json.dumps(categories, indent=2))

