import os
import random
import math
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from app.config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    BACKGROUNDS_DIR, MUSIC_DIR, FONTS_DIR, VIDEOS_DIR
)
from app.subtitles import create_timed_chunks

def get_audio_duration(audio_path: str) -> float:
    """Returns duration of a WAV file in seconds."""
    try:
        with wave.open(audio_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception as e:
        print(f"[Video Compositor] Error reading WAV duration: {e}")
        return 60.0

def find_font(size: int = 64) -> ImageFont.FreeTypeFont:
    """Finds an appropriate bold font for short-form subtitles."""
    # Check custom font folder first
    for f in os.listdir(FONTS_DIR):
        if f.lower().endswith((".ttf", ".otf")):
            try:
                return ImageFont.truetype(os.path.join(FONTS_DIR, f), size)
            except Exception:
                pass

    # Windows system fonts
    font_candidates = [
        "C:\\Windows\\Fonts\\impact.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for candidate in font_candidates:
        if os.path.exists(candidate):
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue

    return ImageFont.load_default()

def draw_subtitle_on_frame(
    frame_pil: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color=(255, 230, 0),  # High-retention Shorts yellow
    stroke_color=(0, 0, 0),
    stroke_width=6
) -> Image.Image:
    """Draws centered kinetic subtitle with strong outline onto an image frame."""
    draw = ImageDraw.Draw(frame_pil)
    
    # Calculate bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center horizontally, place slightly below center (62% height) for Shorts UI clearance
    x = (VIDEO_WIDTH - text_w) // 2
    y = int(VIDEO_HEIGHT * 0.62)

    # Draw dark shadow / stroke for maximum readability on any background
    for ox in range(-stroke_width, stroke_width + 1):
        for oy in range(-stroke_width, stroke_width + 1):
            if ox != 0 or oy != 0:
                draw.text((x + ox, y + oy), text, font=font, fill=stroke_color)

    # Draw primary text
    draw.text((x, y), text, font=font, fill=text_color)
    return frame_pil

def create_procedural_background_frame(width: int, height: int, t: float) -> Image.Image:
    """
    Creates an atmospheric deep gradient frame with subtle ambient motion
    when no video footage is provided.
    """
    # Dynamic dark indigo-violet atmospheric gradient
    r1, g1, b1 = int(15 + 10 * math.sin(t * 0.4)), int(18 + 8 * math.cos(t * 0.5)), int(45 + 15 * math.sin(t * 0.3))
    r2, g2, b2 = int(35 + 12 * math.cos(t * 0.3)), int(20 + 10 * math.sin(t * 0.4)), int(75 + 20 * math.cos(t * 0.5))

    # Create vertical gradient array
    y_coords = np.linspace(0, 1, height)[:, None]
    r = (r1 * (1 - y_coords) + r2 * y_coords).astype(np.uint8)
    g = (g1 * (1 - y_coords) + g2 * y_coords).astype(np.uint8)
    b = (b1 * (1 - y_coords) + b2 * y_coords).astype(np.uint8)

    grad = np.dstack((np.tile(r, (1, width)), np.tile(g, (1, width)), np.tile(b, (1, width))))
    return Image.fromarray(grad)

def render_short_video(
    story: dict,
    audio_path: str,
    output_path: str,
    background_path: str = None
) -> str:
    """
    Assembles audio narration, background visuals, and dynamic subtitles into a 9:16 vertical short.
    Uses MoviePy if available; falls back to OpenCV video rendering.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    duration = get_audio_duration(audio_path)
    print(f"[Video Compositor] Rendering 9:16 Short ({VIDEO_WIDTH}x{VIDEO_HEIGHT}) | Duration: {duration:.1f}s")

    # Generate timed subtitle chunks
    subtitles = create_timed_chunks(story.get("story", ""), duration)
    font = find_font(size=64)

    # Attempt MoviePy compilation if available
    try:
        from moviepy.editor import (
            AudioFileClip, VideoClip, CompositeVideoClip, ImageClip
        )
        print("[Video Compositor] Utilizing MoviePy pipeline...")
        
        audio_clip = AudioFileClip(audio_path)
        
        def make_frame(t):
            img = create_procedural_background_frame(VIDEO_WIDTH, VIDEO_HEIGHT, t)
            # Find active subtitle
            active_text = ""
            for sub in subtitles:
                if sub["start"] <= t <= sub["end"]:
                    active_text = sub["text"]
                    break
            if active_text:
                img = draw_subtitle_on_frame(img, active_text, font)
            return np.array(img)

        video = VideoClip(make_frame, duration=duration)
        video = video.set_audio(audio_clip)
        video.write_videofile(
            output_path,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4
        )
        print(f"[Video Compositor] Final Short rendered successfully: {output_path}")
        return output_path

    except ImportError:
        print("[Video Compositor] MoviePy is unavailable; using OpenCV video-only fallback.")

    # OpenCV Fallback video rendering
    try:
        import cv2
        print("[Video Compositor] Utilizing OpenCV high-performance compositor...")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, FPS, (VIDEO_WIDTH, VIDEO_HEIGHT))

        total_frames = int(duration * FPS)
        for f in range(total_frames):
            t = f / float(FPS)
            img = create_procedural_background_frame(VIDEO_WIDTH, VIDEO_HEIGHT, t)

            active_text = ""
            for sub in subtitles:
                if sub["start"] <= t <= sub["end"]:
                    active_text = sub["text"]
                    break

            if active_text:
                img = draw_subtitle_on_frame(img, active_text, font)

            # Convert RGB PIL to BGR OpenCV
            cv_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(cv_frame)

        out.release()
        raise RuntimeError(
            "OpenCV created the video frames, but cannot mux the narration audio. "
            "Install the video dependencies with `pip install -r requirements.txt` "
            "so MoviePy and FFmpeg can produce a video with voice."
        )

    except Exception as e:
        print(f"[Video Compositor] Compositing error: {e}")
        raise e
