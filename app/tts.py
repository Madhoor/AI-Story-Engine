import torch
import soundfile as sf
import os

from kokoro import KPipeline, KModel


device = "cuda" if torch.cuda.is_available() else "cpu"

model = KModel().to(device)
pipeline = KPipeline(
    lang_code="a",
    model=model
)

print(f"Kokoro running on: {device}")

def generate_voice(text, output_path="data/audio/story.wav", voice="af_heart"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    audio_chunks = []

    generator = pipeline(text, voice=voice)

    for _, _, audio in generator:
        audio_chunks.extend(audio)

    sf.write(output_path, audio_chunks, 24000)

    print(f"Voice saved to: {output_path}")