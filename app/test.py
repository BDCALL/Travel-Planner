import os
import pandas as pd

CSV_FILE = "top100_cities_attractions.csv"
IMAGE_DIR = "images_city"  # folder where city images are stored

# Load cities from CSV
df = pd.read_csv(CSV_FILE)
cities = df["City"].unique()

missing_images = []

for city in cities:
    # Normalize city name: lowercase, remove spaces
    base_name = city.lower().replace(" ", "")
    # Check both .jpg and .jpeg
    jpg_path = os.path.join(IMAGE_DIR, base_name + ".jpg")
    jpeg_path = os.path.join(IMAGE_DIR, base_name + ".jpeg")
    png_path = os.path.join(IMAGE_DIR, base_name + ".png")
    
    if not (os.path.exists(jpg_path) or os.path.exists(jpeg_path) or os.path.exists(png_path)):
        missing_images.append(city)

if missing_images:
    print("Cities missing images:", missing_images)
else:
    print("All cities have images!")