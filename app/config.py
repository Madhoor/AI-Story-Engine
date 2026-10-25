import os
import requests

# Ollama API Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_HOST}/api/tags"
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "600"))

# Default Model Selection (User has Ollama with Qwen models)
DEFAULT_MODEL = os.environ.get("STORY_MODEL", "qwen3:8b")
FINETUNED_MODEL = os.environ.get("FINETUNED_MODEL", "")

def detect_qwen_model(preferred_model=DEFAULT_MODEL):
    """
    Attempts to auto-detect installed Qwen models from local Ollama instance.
    Falls back gracefully to preferred_model if Ollama is unreachable.
    """
    try:
        res = requests.get(OLLAMA_TAGS_URL, timeout=1.5)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            model_names = [m.get("name", "") for m in models_data]
            
            # Check if preferred model is directly available
            for name in model_names:
                if preferred_model in name:
                    return name
            
            # Find any installed Qwen model
            for name in model_names:
                if "qwen" in name.lower():
                    return name
                    
            if model_names:
                return model_names[0]
    except Exception:
        pass
    return preferred_model

MODEL = detect_qwen_model(DEFAULT_MODEL)

# Voice & Audio Configuration
# Popular Kokoro voices: 'af_heart' (Grade A), 'af_bella' (Grade A-), 'am_adam', 'bm_fable'
VOICE = os.environ.get("STORY_VOICE", "af_heart")
AUDIO_SAMPLE_RATE = 24000

# Video Specifications (Vertical YouTube Shorts / Reels 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# Orchestrator & Critic Thresholds
ACCEPT_THRESHOLD = 8.0
NUM_CANDIDATES = 3
MAX_REWRITES = 3

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORIES_DIR = os.path.join(DATA_DIR, "stories")
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
VIDEOS_DIR = os.path.join(DATA_DIR, "videos")

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
STORY_PROMPT_PATH = os.path.join(PROMPTS_DIR, "story_prompt.txt")
CRITIC_PROMPT_PATH = os.path.join(PROMPTS_DIR, "critic_prompt.txt")
EDITOR_PROMPT_PATH = os.path.join(PROMPTS_DIR, "editor_prompt.txt")

# Ensure required directories exist
for directory in [STORIES_DIR, AUDIO_DIR, VIDEOS_DIR, BACKGROUNDS_DIR, MUSIC_DIR, FONTS_DIR]:
    os.makedirs(directory, exist_ok=True)
