"""
Скрипт для автоматичного завантаження та розпакування моделей Vosk.
Запустіть один раз перед першим стартом бота: python download_models.py
"""

import os
import zipfile
import urllib.request
from pathlib import Path

MODELS_DIR = Path(__file__).parent / "models"

MODELS = [
    {
        "name": "vosk-model-uk-v3",
        "url": "https://alphacephei.com/vosk/models/vosk-model-uk-v3.zip",
    },
]


def download_with_progress(url: str, dest: Path) -> None:
    """Завантажує файл з відображенням прогресу."""
    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            mb_done = downloaded / 1_048_576
            mb_total = total_size / 1_048_576
            print(f"\r  {percent:5.1f}%  {mb_done:.1f} / {mb_total:.1f} МБ", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook)
    print()  # новий рядок після завершення


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for model in MODELS:
        model_dir = MODELS_DIR / model["name"]
        zip_path = MODELS_DIR / f"{model['name']}.zip"

        if model_dir.exists():
            print(f"✅ Модель '{model['name']}' вже існує, пропускаємо.")
            continue

        print(f"\n⬇️  Завантаження '{model['name']}'...")
        download_with_progress(model["url"], zip_path)

        print(f"📦 Розпакування '{model['name']}'...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(MODELS_DIR)

        zip_path.unlink()
        print(f"✅ '{model['name']}' готово.")

    print("\n🎉 Модель завантажено та розпаковано у папку 'models/'.")


if __name__ == "__main__":
    main()
