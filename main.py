import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import re

URL = "https://starmilling.com/poultry-chicken-breeds/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
def safe_filename(text):
    # Remove invalid Windows characters
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    # Replace spaces with underscore
    return text.replace(" ", "_").lower()

IMAGE_DIR = "images"
CSV_FILE = "chicken_breeds.csv"

os.makedirs(IMAGE_DIR, exist_ok=True)

session = requests.Session()
session.headers.update(HEADERS)

# FETCH PAGE

response = session.get(URL, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

results = []

# SCRAPE EACH BREED ROW
rows = soup.find_all("div", class_="et_pb_row")

for row in rows:

    # Each breed row has an id like "australorp", "barnvelder"
    breed_id = row.get("id")
    if not breed_id:
        continue

    # BREED NAME
    title_tag = row.find("h2")
    if not title_tag:
        continue

    breed_name = title_tag.get_text(strip=True)

    # DESCRIPTION
    paragraphs = row.find_all("p")
    description = " ".join(p.get_text(" ", strip=True) for p in paragraphs)

    # IMAGE
    img_tag = row.find("img")
    image_url = None

    if img_tag:
        image_url = (
            img_tag.get("data-lazy-src") or
            img_tag.get("src")
        )

    # Download image only if valid URL
    if image_url and image_url.startswith("http"):
        img_filename = safe_filename(breed_name) + ".jpg"

        img_path = os.path.join(IMAGE_DIR, img_filename)

        try:
            img_data = session.get(image_url, timeout=15).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            time.sleep(0.4)  
        except Exception as e:
            print(f"Image failed for {breed_name}: {e}")
            image_url = None
    else:
        image_url = None

    # SAVE DATA
  
    results.append({
        "breed_id": breed_id,
        "breed_name": breed_name,
        "description": description,
        "image_url": image_url
    })


# SAVE CSV

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["breed_id", "breed_name", "description", "image_url"]
    )
    writer.writeheader()
    writer.writerows(results)

print(f"Total breeds: {len(results)}")
print(f"CSV saved: {CSV_FILE}")
print(f"Images saved in: ./{IMAGE_DIR}/")
