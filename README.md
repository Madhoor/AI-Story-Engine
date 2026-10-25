# AI-Story-Engine

An agentic, local-first pipeline for generating moral-driven stories, evaluating
them with an Ollama LLM, synthesizing narration, and producing vertical short
videos.

**Authors:** Siddhant Lawand (Roll No: 9) | Madhoor Deo (Roll No: 13) | Panel C1

## What the project does

AI-Story-Engine combines:

1. A local Ollama/Qwen story generator.
2. Structured JSON story output.
3. An AI critic that scores story quality.
4. Tournament ranking or iterative rewriting.
5. Kokoro neural text-to-speech.
6. 24 kHz WAV voiceover export.
7. 1080x1920 vertical video composition with timed subtitles.
8. A research benchmark comparing baseline prompting, RAG, and an optional
   separately fine-tuned Ollama model.

All story generation and evaluation requests run locally through Ollama. Kokoro
may download its model from Hugging Face the first time voice synthesis runs;
the model is cached locally afterward.

## Requirements

- Windows, macOS, or Linux.
- Python **3.11 or 3.12** for the complete pipeline. Kokoro 0.9.4 does not
  support Python 3.13+.
- Node.js and npm for the React frontend.
- Ollama.
- At least 8 GB RAM is recommended. More RAM or a supported GPU improves
  generation speed.
- Internet access for the first Python package installation and the first
  Kokoro model download.

## Windows setup

Open PowerShell in the repository root:

```powershell
cd "C:\Users\Admin\Documents\Projects\AI-Story-Engine"
```

### 1. Create and activate the Python environment

If Python 3.11 is installed:

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\activate
```

Verify the interpreter:

```powershell
python --version
```

It must report Python 3.11.x or Python 3.12.x. Always use the activated
environment when installing packages or starting the backend.

### 2. Install Python dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements include FastAPI, Uvicorn, Ollama HTTP support, Kokoro,
PyTorch, SoundFile, MoviePy, and the FFmpeg helper.

### 3. Install and prepare Ollama

Install Ollama from [ollama.com/download](https://ollama.com/download), then
start its local service:

```powershell
ollama serve
```

Keep that terminal open. In a second terminal, download the recommended
development model:

```powershell
ollama pull qwen2.5:3b
```

You can also install the larger model:

```powershell
ollama pull qwen3:8b
```

Verify the models:

```powershell
ollama list
```

The application automatically discovers installed Ollama models.

### 4. Install frontend dependencies

Open a third PowerShell terminal:

```powershell
cd "C:\Users\Admin\Documents\Projects\AI-Story-Engine\frontend"
npm install
```

## Start the application

Three processes are used during development.

### Terminal 1: Ollama

```powershell
ollama serve
```

### Terminal 2: FastAPI backend

```powershell
cd "C:\Users\Admin\Documents\Projects\AI-Story-Engine"
.venv311\Scripts\activate
python server.py
```

The backend runs at `http://localhost:8000`.

Health check:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Expected response:

```json
{"status":"ok","service":"AI-Story-Engine"}
```

### Terminal 3: React frontend

```powershell
cd "C:\Users\Admin\Documents\Projects\AI-Story-Engine\frontend"
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The frontend communicates with the FastAPI backend through the Vite proxy.

## Using Creator Studio

1. Open the **Creator Studio** tab.
2. Choose an installed Ollama model.
3. Select a moral or enter a custom topic.
4. Choose an execution mode:
   - **Tournament:** generates and scores multiple candidates.
   - **Iterative Rewrite:** improves one story using critic feedback.
   - **Rapid Single Draft:** fastest option for testing.
5. Select a Kokoro voice.
6. Enable audio and video when you want final media.
7. Click **Generate Story & Short**.

Generated files are saved to:

```text
data/stories/story_XXXX.json
data/audio/story_XXXX.wav
data/videos/story_XXXX.mp4
```

Use `qwen2.5:3b` and **Rapid Single Draft** while testing. Tournament mode makes
several generation and critic requests and therefore takes longer.

## RAG vs. fine-tuning benchmark

Open the **RAG vs. Fine-Tuning Benchmark** tab to compare:

- **Baseline:** normal prompting with the selected baseline Ollama model.
- **RAG:** baseline model with local viral-story exemplars added to the prompt.
- **Fine-Tuned:** a separate fine-tuned Ollama model.

### Selecting the fine-tuned model

The fine-tuned model field is a dropdown populated from `ollama list`. Select
the exact model name shown by Ollama. Do not enter a story title.

The baseline model is excluded from the dropdown and cannot be compared against
itself. A base model such as `qwen3:8b` is not a fine-tuned model simply because
it appears in the Ollama list.

For a genuine third benchmark arm, create or import a separately fine-tuned
Ollama model, for example:

```powershell
ollama create story-lora -f Modelfile
ollama list
```

Then select `story-lora` in the benchmark dropdown.

Recommended fast settings:

```text
Trials per Method: 1
Fast mode: enabled
```

Fast mode reduces the context and output limits for quicker comparison. Use
multiple trials and disable fast mode for a more reliable research result.

The CLI study mode supports baseline and RAG. To run the fine-tuned arm from
the CLI, set the model before starting the backend or command:

```powershell
$env:FINETUNED_MODEL="story-lora"
python main.py --mode study --candidates 1
```

## CLI usage

Run commands from the repository root with `.venv311` activated.

### Tournament mode

```powershell
python main.py --mode tournament --candidates 3
```

With a moral:

```powershell
python main.py --mode tournament `
  --moral "Honesty builds trust that deceit permanently destroys." `
  --candidates 3
```

With a topic:

```powershell
python main.py --mode tournament `
  --topic "finding an unmarked copper key under the floorboards" `
  --model qwen2.5:3b
```

### Iterative rewrite mode

```powershell
python main.py --mode rewrite --model qwen2.5:3b
```

### RAG benchmark

```powershell
python main.py --mode study --candidates 1
```

### Skip media generation

```powershell
python main.py --mode tournament --candidates 1 --skip-audio --skip-video
```

## Configuration

Configuration is read from environment variables in `app/config.py`.

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `OLLAMA_TIMEOUT` | `600` | Maximum Ollama generation time in seconds |
| `STORY_MODEL` | `qwen3:8b` | Default baseline model |
| `FINETUNED_MODEL` | empty | Optional fine-tuned model for CLI study mode |
| `STORY_VOICE` | `af_heart` | Default Kokoro voice |

PowerShell example:

```powershell
$env:STORY_MODEL="qwen2.5:3b"
$env:OLLAMA_TIMEOUT="900"
$env:STORY_VOICE="af_heart"
```

The environment variables must be set before starting the backend or CLI.

## Project structure

```text
AI-Story-Engine/
├── app/
│   ├── config.py       # Models, paths, timeouts, audio/video settings
│   ├── llm.py          # Ollama generation and response parsing
│   ├── critic.py       # Story quality scoring
│   ├── editor.py       # Critic-guided story rewriting
│   ├── ranker.py       # Candidate ranking and tournament mode
│   ├── study.py        # Baseline, RAG, and optional fine-tuned benchmark
│   ├── tts.py          # Kokoro neural voice synthesis
│   ├── subtitles.py    # Timed subtitle generation
│   └── video.py        # Vertical video composition
├── frontend/
│   ├── src/App.jsx     # React Creator Studio and benchmark UI
│   └── package.json    # Frontend dependencies and scripts
├── prompts/
│   ├── story_prompt.txt
│   ├── critic_prompt.txt
│   └── editor_prompt.txt
├── data/
│   ├── stories/
│   ├── audio/
│   └── videos/
├── docs/               # PRD, TRD, architecture, design, and agent docs
├── server.py           # FastAPI backend
├── main.py             # CLI entry point
├── requirements.txt
└── README.md
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`

The wrong Python interpreter is being used. Activate `.venv311` and install
the requirements:

```powershell
.venv311\Scripts\activate
python -m pip install -r requirements.txt
python -c "import fastapi, uvicorn; print('Backend dependencies OK')"
```

### Ollama connection error

Start Ollama and confirm its API:

```powershell
ollama serve
Invoke-RestMethod http://localhost:11434/api/tags
```

### Empty Ollama response or JSON parsing error

Confirm that the selected model is installed and try `qwen2.5:3b` first:

```powershell
ollama list
ollama run qwen2.5:3b
```

The application reports empty responses as errors instead of displaying
misleading zero scores.

### Voice generation is slow the first time

Kokoro downloads and loads its neural model on the first TTS request. This can
download hundreds of megabytes. Later requests reuse the local Hugging Face
cache.

### Video has no voice

Install the video dependencies from `requirements.txt`. MoviePy and FFmpeg
support are required to mux the WAV narration into the MP4. If the media
dependencies are unavailable, the application reports the problem instead of
silently creating a video-only file.

### Benchmark shows no fine-tuned result

Install a separate fine-tuned Ollama model and select it from the dropdown.
`qwen2.5:3b` and `qwen3:8b` are base models, not fine-tuned models.

## Documentation

- [Product requirements](docs/PRD.md)
- [Technical requirements](docs/TRD.md)
- [Architecture](docs/Architecture.md)
- [Design](docs/Design.md)
- [UI/UX](docs/UI_UX.md)
- [Agent specifications](docs/Agents.md)

## Validation

Backend syntax:

```powershell
python -m compileall -q app server.py main.py
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Privacy and limitations

- Story generation, critique, and media processing are designed to run locally.
- Ollama model files and Kokoro model files consume substantial disk space.
- Fine-tuning is not performed automatically by this repository; the benchmark
  consumes a separately trained/imported Ollama model.
- Research benchmark quality depends on the number of trials and the critic
  model's consistency.
