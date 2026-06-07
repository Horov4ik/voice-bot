import os
import logging
import tempfile
import subprocess

from dotenv import load_dotenv
import imageio_ffmpeg
from faster_whisper import WhisperModel

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

LANGUAGE_FLAGS = {
    "uk": "🇺🇦",
    "ru": "🇷🇺",
    "en": "🇬🇧",
}

logger.info("Завантаження моделі Whisper (tiny)...")
MODEL = WhisperModel("small", device="cpu", compute_type="int8")
logger.info("Модель завантажено.")


def transcribe(wav_path: str) -> tuple[str, str]:
    """Транскрибує WAV-файл. Повертає (language, text)."""
    segments, info = MODEL.transcribe(wav_path, language="uk")
    text = " ".join(s.text.strip() for s in segments).strip()
    logger.info("Мова: %s, текст: '%s'", info.language, text)
    return info.language, text


def convert_to_wav(input_path: str, output_path: str) -> None:
    """Конвертує аудіо/відео у WAV моно 16000 Гц через ffmpeg."""
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace"))


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if message.voice:
        file_obj = message.voice
        suffix = ".ogg"
    elif message.video_note:
        file_obj = message.video_note
        suffix = ".mp4"
    else:
        return

    status_msg = await message.reply_text("🎙️ Розпізнаю...")

    tmp_input = None
    tmp_wav = None
    try:
        tg_file = await context.bot.get_file(file_obj.file_id)

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            tmp_input = f.name
        await tg_file.download_to_drive(tmp_input)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_wav = f.name

        convert_to_wav(tmp_input, tmp_wav)
        lang, text = transcribe(tmp_wav)

        flag = LANGUAGE_FLAGS.get(lang, "🌐")
        first_name = user.first_name if user else "Unknown"

        if text:
            reply = f"🗣 *{first_name}* {flag}\n_{text}_"
        else:
            reply = "🤷 Не вдалося розпізнати"

        await status_msg.edit_text(reply, parse_mode=ParseMode.MARKDOWN)

    except Exception as exc:
        logger.error("Помилка обробки аудіо: %s", exc, exc_info=True)
        await status_msg.edit_text("❌ Помилка обробки аудіо")
    finally:
        for path in (tmp_input, tmp_wav):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN не знайдено у .env або змінних середовища")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE | filters.VIDEO_NOTE, handle_audio))

    logger.info("Бот запущено. Очікуємо повідомлення...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
