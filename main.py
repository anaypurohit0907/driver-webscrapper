import requests
from bs4 import BeautifulSoup
import csv

csv_filename = "manufacturers.csv"
base_url = "https://www.driverscape.com/manufacturers"

all_rows = []

for page_num in range(1, 25):
    url = base_url if page_num == 1 else f"{base_url}/page{page_num}"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    # Assuming manufacturers are listed within <a href="..."> tags in a specific section
    # Look for the table or list containing manufacturer links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Filter links that match device/manufacturer detail pages
        if href.startswith("/manufacturers/") and not '/page' in href:
            name = a.get_text(strip=True)
            full_link = f"https://www.driverscape.com{href}"
            all_rows.append([name, full_link])

# Save to CSV
with open(csv_filename, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Manufacturer", "Link"])
    writer.writerows(all_rows)
print(f"Saved {len(all_rows)} manufacturers in {csv_filename}")

