import os
import re
from typing import List, Dict, Tuple

def create_timed_chunks(text: str, total_duration: float, words_per_chunk: int = 3) -> List[Dict]:
    """
    Splits text into short, high-impact subtitle cards (2-4 words) with proportional timestamps.
    """
    words = re.findall(r"\S+", text)
    if not words:
        return []

    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= words_per_chunk or word.endswith((".", "!", "?", ",", ";", ":")):
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Calculate proportional duration per chunk based on character length
    total_chars = sum(len(c) for c in chunks)
    timed_subtitles = []
    current_time = 0.0

    for chunk in chunks:
        # Proportion based on text length with slight minimum display time
        duration = (len(chunk) / total_chars) * total_duration if total_chars > 0 else 1.0
        duration = max(0.4, duration)  # Minimum 400ms for readability
        end_time = min(total_duration, current_time + duration)

        timed_subtitles.append({
            "text": chunk.upper(),
            "start": round(current_time, 2),
            "end": round(end_time, 2)
        })
        current_time = end_time

    return timed_subtitles

def format_timestamp_srt(seconds: float) -> str:
    """Formats seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def export_srt(timed_subtitles: List[Dict], srt_path: str) -> str:
    """Exports timed subtitle chunks to an SRT file."""
    os.makedirs(os.path.dirname(os.path.abspath(srt_path)), exist_ok=True)
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, sub in enumerate(timed_subtitles, 1):
            start = format_timestamp_srt(sub["start"])
            end = format_timestamp_srt(sub["end"])
            f.write(f"{idx}\n{start} --> {end}\n{sub['text']}\n\n")
    return srt_path

