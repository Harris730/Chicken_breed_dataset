import pandas as pd
from PIL import Image
import os
import matplotlib.pyplot as plt

df = pd.read_csv("chicken_breeds.csv")
print(df.head())

row = df.iloc[0]

if pd.notna(row["image"]):
    img_path = os.path.join("images", row["image"])
    img = Image.open(img_path)
    plt.imshow(img)
    plt.axis("off")
    plt.title(row["breed_name"])
    plt.show()
else:
    print("No image available for:", row["breed_name"])
