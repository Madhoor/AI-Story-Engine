# Technical Requirements Document (TRD)
## Project: AI-Story-Engine
**An Agentic AI Pipeline for Automated Story Generation, Evaluation, and Short-Form Video Creation**

---

## 1. System Overview & Technology Stack

| Component | Technology / Library | Version / Requirement | Purpose |
| :--- | :--- | :--- | :--- |
| **Runtime** | Python | 3.10 – 3.12 (Windows 64-bit) | Core application execution |
| **Local LLM Engine** | Ollama REST API | v0.3.0+ (`localhost:11434`) | Hosting open-source LLM inference |
| **Primary LLM** | Qwen family (`qwen2.5:7b`, `qwen3:8b`, etc.) | Quantized (4-bit/8-bit GGUF) | Story generation, critique, rewriting |
| **TTS Engine** | Kokoro TTS (`kokoro>=0.9.4`) | Torch CUDA/CPU, `espeakng` | 24kHz photorealistic voice synthesis |
| **Audio Processing** | `soundfile`, `numpy` | `soundfile==0.14.0`, `numpy>=1.26` | WAV writing and normalization |
| **Video Compositing** | MoviePy / FFmpeg | `moviepy>=1.0.3` / `ffmpeg` | Video assembly, cropping, audio ducking |
| **Subtitles / Fonts** | Pillow (`PIL`), SRT / Subtitles | `pillow>=10.0.0` | Styled dynamic kinetic subtitles |
| **Storage & Data** | Local JSON & Media Directories | Structured file system | Storage for stories, audio, videos |

---

## 2. Architecture & Data Contracts

### 2.1 Story Schema (`data/stories/story_XXXX.json`)
The generator must produce valid JSON matching this schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "StoryPackage",
  "type": "object",
  "required": ["title", "hook", "story", "thumbnail_prompt", "scene_prompts"],
  "properties": {
    "title": {
      "type": "string",
      "maxLength": 60,
      "description": "Short, curiosity-inducing title under 60 chars"
    },
    "hook": {
      "type": "string",
      "maxLength": 100,
      "description": "Opening hook sentence under 15 words"
    },
    "story": {
      "type": "string",
      "description": "First-person narrative, 300 to 350 words"
    },
    "thumbnail_prompt": {
      "type": "string",
      "description": "Cinematic visual description for thumbnail generation"
    },
    "scene_prompts": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 4,
      "maxItems": 4,
      "description": "Exactly 4 progression prompts: Hook, Conflict, Climax, Ending"
    }
  }
}
```

### 2.2 Critic Review Schema
The Critic Agent evaluates the story package and returns:
```json
{
  "scores": {
    "hook": 8,
    "pacing": 8,
    "emotion": 7,
    "believability": 9,
    "twist": 8,
    "retention": 8,
    "originality": 8,
    "ai_naturalness": 9,
    "comment_potential": 8,
    "overall": 8.1
  },
  "confidence": 88,
  "decision": "ACCEPT",
  "weaknesses": [
    "The middle transition could introduce the twist clues earlier."
  ],
  "improvements": [
    "Tighten the 3rd sentence in paragraph 2 to maintain pacing."
  ],
  "ai_flags": [],
  "high_score_justifications": [
    "Strong realistic narrator voice without melodramatic tropes."
  ],
  "retention_drops": [
    {
      "approx_time": "0:35",
      "reason": "Slight slowdown in dialogue explanation"
    }
  ],
  "feedback": "Compelling story with high authenticity."
}
```

---

## 3. Component Specifications

### 3.1 LLM Client (`app/llm.py`)
- **Protocol:** HTTP POST to `OLLAMA_URL` (`http://localhost:11434/api/generate`).
- **Configurable Parameters:**
  - `model`: Configured via `app/config.py` (e.g., `qwen2.5:7b`, `qwen3:8b`).
  - `format`: `"json"` to ensure native JSON grammar constrained output.
  - `stream`: `true`; the client assembles response chunks before parsing JSON.
  - `options`: `{ "temperature": 0.75, "top_p": 0.9, "num_ctx": 4096 }`.
- **Resilience:**
  - Sanitization of markdown code fences (````json ... ````).
  - Schema fallback and automatic retry on missing keys.

### 3.2 AI Critic (`app/critic.py`)
- **Logic:**
  - Evaluates consistency between `title`, `hook`, `story`, and `twist`.
  - Implements the **Logical Consistency Rule**: If plot contradictions or unearned twists exist, scores for Believability, Twist, and Overall are clamped to $\le 6$, and decision cannot be `ACCEPT`.
  - Parses and validates numeric ranges ($1 \le score \le 10$).

### 3.3 Decision & Orchestrator Logic
- **Iterative Mode:** Up to `MAX_REWRITES` (default: 3). If `score >= ACCEPT_THRESHOLD` (default: 8.0), story is accepted.
- **Tournament / Ranking Mode:** (Identified as superior in `app/notes.md`) Generates $N$ stories (e.g., $N=5$), critiques each, and selects the optimal story based on:
  $$\text{Score} = \text{overall} \times 0.4 + \text{retention} \times 0.2 + \text{hook} \times 0.2 + \text{originality} \times 0.2$$
  Ties broken by `ai_naturalness` and `believability`.

### 3.4 Text-To-Speech (`app/tts.py`)
- **Engine:** Kokoro-82M model (`lang_code="a"` for American, `"b"` for British).
- **Audio Output:** 24,000 Hz, 16-bit mono WAV.
- **Voice Selection:** Dynamic mapping based on narrator profile:
  - Female: `af_heart` (primary), `af_bella`, `af_nicole`.
  - Male: `am_adam` (primary), `am_fenrir`, `am_michael`, `bm_fable`.
- **Chunking:** Automatic sentence-level audio splitting and concatenation to avoid VRAM exhaustion and clipping.

### 3.5 Video Synthesizer (`app/video.py`)
- **Input Specifications:**
  - Visual: 1080x1920 (9:16 vertical video) background clips (`assets/backgrounds/*.mp4`).
  - Audio: Primary voice narration (`data/audio/*.wav`) + ambient background music (`assets/music/*.mp3`).
- **Processing Steps:**
  1. Measure exact duration of voice audio $T$.
  2. Subclip or loop video to match duration $T$.
  3. Overlay kinetic subtitles synchronized with voice timings.
  4. Duck background music audio to -18dB when narration is playing.
  5. Export MP4 (H.264 video, AAC audio) to `data/videos/`.

---

## 4. Hardware & Resource Requirements

| Resource | Minimum | Recommended |
| :--- | :--- | :--- |
| **GPU** | NVIDIA RTX 3060 6GB (VRAM) | NVIDIA RTX 3080/4070 12GB+ |
| **RAM** | 16 GB DDR4 | 32 GB DDR4/DDR5 |
| **Disk** | 15 GB free SSD space | 50 GB free NVMe SSD |
| **OS** | Windows 10/11 64-bit | Windows 11 / Ubuntu 22.04 |

---

## 5. Security & Verification Strategy
- **Sandboxed Execution:** 100% offline generation prevents API key leaks or confidential data transmission.
- **Unit & Integration Tests:**
  - Prompt loader integrity check.
  - JSON schema conformance verification.
  - Ollama health check & model discovery.
  - Kokoro audio generation test.
  - Video rendering test pattern.
