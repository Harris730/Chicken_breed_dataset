import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import re

# ===============================
# CONFIG
# ===============================
URL = "https://starmilling.com/poultry-chicken-breeds/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

IMAGE_DIR = "images"
CSV_FILE = "chicken_breeds.csv"

os.makedirs(IMAGE_DIR, exist_ok=True)

# ===============================
# UTILS
# ===============================
def safe_filename(text):
    """Make filename OS-safe"""
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    return text.replace(" ", "_").lower()

# ===============================
# SESSION
# ===============================
session = requests.Session()
session.headers.update(HEADERS)

# ===============================
# FETCH PAGE
# ===============================
response = session.get(URL, timeout=20)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

results = []

# ===============================
# SCRAPE EACH BREED
# ===============================
rows = soup.find_all("div", class_="et_pb_row")

for row in rows:

    # Breed unique ID (used as stable key)
    breed_id = row.get("id")
    if not breed_id:
        continue

    # Breed name
    title_tag = row.find("h2")
    if not title_tag:
        continue

    breed_name = title_tag.get_text(strip=True)

    # Description
    paragraphs = row.find_all("p")
    description = " ".join(
        p.get_text(" ", strip=True) for p in paragraphs
    )

    # Image extraction
    img_tag = row.find("img")
    image_url = None
    image_filename = None

    if img_tag:
        image_url = (
            img_tag.get("data-lazy-src") or
            img_tag.get("src")
        )

    # Download image if valid
    if image_url and image_url.startswith("http"):
        image_filename = f"{breed_id}.jpg"
        img_path = os.path.join(IMAGE_DIR, image_filename)

        try:
            img_response = session.get(image_url, timeout=15)
            img_response.raise_for_status()

            with open(img_path, "wb") as f:
                f.write(img_response.content)

            time.sleep(0.4)  # be polite
        except Exception as e:
            print(f"Image failed for {breed_name}: {e}")
            image_filename = None

    # Save linked record
    results.append({
        "breed_id": breed_id,
        "breed_name": breed_name,
        "description": description,
        "image": image_filename
    })

# ===============================
# SAVE CSV
# ===============================
with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["breed_id", "breed_name", "description", "image"]
    )
    writer.writeheader()
    writer.writerows(results)

print("=" * 50)
print(f"Total breeds scraped : {len(results)}")
print(f"CSV saved            : {CSV_FILE}")
print(f"Images directory     : ./{IMAGE_DIR}/")
print("=" * 50)
