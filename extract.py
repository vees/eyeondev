from bs4 import BeautifulSoup
import requests
import json

# Example: loading page
response = requests.get("https://www.lowersalfordtownship.org/departments/building-zoning/eye-on-development/")
soup = BeautifulSoup(response.text, "html.parser")

# For your sample structure (pretend we already loaded soup)
# soup = BeautifulSoup(html, "html.parser")

# Navigate to the core content section
container = soup.select_one("div#a-content div#c-article div.grid-wide.grid-content")

if container:
    # Now you can parse p and ul tags inside this area
    categories = {
        "A. Under Review": [],
        "B. Approved": [],
        "C.  Under Construction": []
    }

    current_category = None
    for tag in container.find_all(['p', 'ul']):
        if tag.name == 'p':
            text = tag.get_text(strip=True)
            if text.startswith("A. Under Review"):
                current_category = "A. Under Review"
            elif text.startswith("B") and "Approved" in text:
                current_category = "B. Approved"
            elif text.startswith("C") and "Under Construction" in text:
                current_category = "C.  Under Construction"
        elif tag.name == 'ul' and current_category:
            for li in tag.find_all('li'):
                for subli in li.find_all('li'):
                    categories[current_category].append(subli.get_text(strip=True))
                if not li.find_all('li'):
                    categories[current_category].append(li.get_text(strip=True))

    print(json.dumps(categories, indent=4))

else:
    print("Could not find the main content area.")
