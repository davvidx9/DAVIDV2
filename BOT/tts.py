"""Generate TTS audio files for Asterisk playback."""

from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

from config import DEFAULT_TTS_LANG, SOUNDS_DIR, TTS_ENGINE

logger = logging.getLogger(__name__)

# Subdir under Asterisk sounds (mounted in Docker)
ASTERISK_SOUND_SUBDIR = "ivr_custom"


def _slug(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", text[:40])
    return f"{safe}_{h}"


def synthesize(text: str, lang: str | None = None) -> str:
    """
  Return Asterisk sound name (without extension) relative to sounds root.
  Writes ulaw/wav into SOUNDS_DIR/ivr_custom/.
  """
    lang = lang or DEFAULT_TTS_LANG
    out_dir = SOUNDS_DIR / ASTERISK_SOUND_SUBDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    name = _slug(f"{lang}:{text}")
    wav_path = out_dir / f"{name}.wav"

    if wav_path.exists():
        return f"{ASTERISK_SOUND_SUBDIR}/{name}"

    if TTS_ENGINE == "pyttsx3":
        import pyttsx3

        engine = pyttsx3.init()
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()
    else:
        from gtts import gTTS

        gTTS(text=text, lang=lang[:2] if len(lang) > 2 else lang).save(str(wav_path))

    # Asterisk prefers gsm/ulaw; wav works with format module in many builds
    logger.info("TTS written %s", wav_path)
    return f"{ASTERISK_SOUND_SUBDIR}/{name}"
