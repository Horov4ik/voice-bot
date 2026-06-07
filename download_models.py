import os
import urllib.request
import zipfile

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

URL = "https://huggingface.co/Yehor/vosk-uk/resolve/main/uk_v3_dynamic_nano.zip"
ZIP_PATH = os.path.join(MODELS_DIR, "model.zip")

print("Завантаження моделі...")
urllib.request.urlretrieve(URL, ZIP_PATH)
print("Розпакування...")

with zipfile.ZipFile(ZIP_PATH, "r") as z:
    names = {n.split("/")[0] for n in z.namelist()}
    print(f"Folders in zip: {names}")
    z.extractall(MODELS_DIR)

os.remove(ZIP_PATH)
print("Done!")
