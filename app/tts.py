import os
import re
from typing import Optional
from app.config import VOICE, AUDIO_SAMPLE_RATE, AUDIO_DIR

_pipeline_instance = None

def get_pipeline(lang_code: str = "a"):
    """
    Lazy-loads Kokoro TTS pipeline with CUDA/CPU auto-detection.
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        try:
            from kokoro import KPipeline

            print("[TTS Agent] Initializing Kokoro Neural TTS...")
            _pipeline_instance = KPipeline(lang_code=lang_code)
        except ImportError as e:
            raise ImportError(
                f"Kokoro TTS or PyTorch is not installed in the current Python environment: {e}\n"
                "To enable local voice synthesis, ensure dependencies are installed via: pip install kokoro soundfile torch"
            )
    return _pipeline_instance

def clean_speech_text(text: str) -> str:
    """
    Pre-processes narrative text for natural TTS output:
    - Strips markdown asterisks, hashes, backticks
    - Removes emojis and unpronounceable symbols
    - Normalizes multiple spaces and punctuation
    """
    # Remove markdown formatting
    cleaned = re.sub(r"[*_~`#]", "", text)
    # Remove URL or brackets
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", cleaned)
    # Remove emoji characters
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", cleaned)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def generate_voice(
    text: str,
    output_path: Optional[str] = None,
    voice: Optional[str] = None
) -> str:
    """
    Synthesizes natural voice audio using Kokoro TTS and saves to 24kHz WAV file.
    """
    if output_path is None:
        output_path = os.path.join(AUDIO_DIR, "output.wav")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    active_voice = voice or VOICE
    
    cleaned_text = clean_speech_text(text)
    print(f"[TTS Agent] Synthesizing {len(cleaned_text.split())} words using voice '{active_voice}'...")

    try:
        import soundfile as sf
        pipeline = get_pipeline(lang_code="a" if active_voice.startswith("a") else "b")
        generator = pipeline(cleaned_text, voice=active_voice)

        audio_chunks = []
        for _, _, audio in generator:
            if hasattr(audio, "detach"):
                audio = audio.detach().cpu().numpy()
            audio_chunks.append(audio)

        if not audio_chunks:
            raise RuntimeError("TTS generation produced empty audio.")

        import numpy as np
        sf.write(output_path, np.concatenate(audio_chunks), AUDIO_SAMPLE_RATE)
        print(f"[TTS Agent] Audio successfully saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"[TTS Agent] Synthesis error: {e}")
        raise e
