# System Architecture Document
## Project: AI-Story-Engine
**An Agentic AI Pipeline for Automated Story Generation, Evaluation, and Short-Form Video Creation**  
**Authors:** Siddhant Lawand (Roll No: 9), Madhoor Deo (Roll No: 13) | Panel C1  

---

## 1. High-Level System Architecture

The AI-Story-Engine is organized as a modular, agentic pipeline where independent autonomous agents collaborate sequentially and iteratively to produce polished viral short-form videos.

```mermaid
flowchart TD
    subgraph S1["1. Generation Phase"]
        A["1. Story Prompt<br/>(Hooks, Tension, Constraints)"] --> B["2. LLM - Story Generator<br/>(Ollama / Qwen)"]
        B --> C["3. Structured Story<br/>(JSON Output)"]
    end

    subgraph S2["2. Quality Analysis & Feedback Loop"]
        C --> D["4. AI Critic Agent<br/>(9 Retention Dimensions)"]
        D --> E["5. Score & Feedback<br/>(Strengths, Weaknesses, AI Flags)"]
        E --> F{"6. Is Score Good Enough?<br/>(Threshold Check)"}
        
        F -- "NO (Rewrite)" --> G["6a. Story Rewriter Agent<br/>(Micro-Edits from Feedback)"]
        G --> C
        
        F -- "NO (Ranking/Tournament)" --> H["Rank Candidate Stories<br/>(Best-of-N Selection)"]
        H --> I
        
        F -- "YES (Score >= 8.0)" --> I["7. Accepted Story<br/>(Saved in /data/stories/)"]
    end

    subgraph S3["3. Media Synthesis & Video Composition"]
        I --> J["8. Text-to-Speech (TTS) Agent<br/>(Kokoro TTS 24kHz)"]
        J --> K["Audio Voiceover<br/>(/data/audio/)"]
        K --> L["9. Video Generation Pipeline<br/>(MoviePy / FFmpeg)"]
        
        M["Background Assets<br/>(/assets/backgrounds/)"] --> L
        N["Background Music<br/>(/assets/music/)"] --> L
        O["Dynamic Subtitle Engine<br/>(Timed Words / Sentences)"] --> L
        
        L --> P["Final Short Video<br/>(/data/videos/*.mp4)"]
    end
```

---

## 2. Agentic Workflow & Component Interactions

### 2.1 The Core Agents

```mermaid
classDiagram
    class StoryGeneratorAgent {
        +prompt_template: str
        +model: str
        +generate(prompt) StoryPackage
    }
    class AICriticAgent {
        +rubric: list
        +evaluate(story: StoryPackage) CriticReview
    }
    class DecisionAgent {
        +threshold: float
        +decide(review: CriticReview) str
        +rank(candidates: list) StoryPackage
    }
    class StoryRewriterAgent {
        +editor_prompt: str
        +rewrite(story, review) StoryPackage
    }
    class TTSAgent {
        +pipeline: KPipeline
        +voice: str
        +synthesize(text, output_path) str
    }
    class VideoAgent {
        +width: int
        +height: int
        +fps: int
        +assemble(audio_path, video_asset, subtitles, music) str
    }

    StoryGeneratorAgent --> AICriticAgent : Emits StoryPackage
    AICriticAgent --> DecisionAgent : Emits CriticReview
    DecisionAgent --> StoryRewriterAgent : Triggers Rewrite if below threshold
    StoryRewriterAgent --> AICriticAgent : Loops revised story
    DecisionAgent --> TTSAgent : Passes Accepted Story
    TTSAgent --> VideoAgent : Passes Synthesized Audio
```

---

## 3. Storage & Directory Architecture

The repository enforces a clean separation of code, prompts, media assets, generated outputs, and documentation:

```
AI-Story-Engine/
├── app/                      # Application Logic & Agent implementations
│   ├── __init__.py
│   ├── config.py             # System constants, models, voice & video specs
│   ├── llm.py                # Story Generator Agent (Ollama client)
│   ├── critic.py             # AI Critic Quality Analyzer
│   ├── editor.py             # Story Rewriter / Editor Agent
│   ├── ranker.py             # Best-of-N Candidate Tournament Selector
│   ├── tts.py                # Kokoro Neural Text-to-Speech synthesis
│   ├── subtitles.py          # Dynamic subtitle and timestamp generator
│   └── video.py              # FFmpeg / MoviePy Video Compositor
├── prompts/                  # Carefully tuned system & prompt templates
│   ├── story_prompt.txt      # Viral Reddit/Shorts story generation prompt
│   ├── critic_prompt.txt     # 9-dimension brutally honest critic prompt
│   └── editor_prompt.txt     # Micro-edit preservation prompt
├── data/                     # Output directory for pipeline artifacts
│   ├── stories/              # Saved JSON story packages (story_0001.json)
│   ├── audio/                # Master 24kHz voiceover WAV files
│   └── videos/               # Rendered 1080x1920 MP4 Shorts
├── assets/                   # Static media libraries
│   ├── backgrounds/          # Looping ambient video clips (nature, city, abstract)
│   ├── music/                # Royalty-free background music tracks
│   └── fonts/                # Bold typography fonts for short-form subtitles
├── docs/                     # System architecture, PRD, TRD, UI/UX, Design specs
│   ├── PRD.md
│   ├── TRD.md
│   ├── Architecture.md
│   ├── UI_UX.md
│   ├── Design.md
│   └── Agents.md
├── models/                   # Local models or weights configs
├── main.py                   # CLI Orchestrator entry point
├── requirements.txt          # Python dependencies
└── README.md                 # Project guide & quickstart
```

---

## 4. Extension Study Architecture: RAG vs. Fine-Tuning

As illustrated in the project roadmap, the study investigates:
**"Which approach is better for our domain: Retrieval-Augmented Generation (RAG) or Fine-Tuning?"**

```mermaid
flowchart TD
    subgraph S_RAG["Approach 1: Retrieval-Augmented Generation (RAG)"]
        R1["Story Prompt Query"] --> R2["Vector Retriever<br/>(ChromaDB / FAISS)"]
        R3["Viral Stories & Hook Dataset<br/>(Curated Exemplars)"] --> R2
        R2 --> R4["Enriched Context<br/>(Few-shot Viral Patterns)"]
        R4 --> R5["Base Qwen LLM"]
        R5 --> R6["RAG Story Output"]
    end

    subgraph S_FT["Approach 2: Supervised Fine-Tuning (SFT / LoRA)"]
        F1["Base Qwen 8B LLM"] --> F2["Curated Viral Dataset<br/>(High-Retention Confessions)"]
        F2 --> F3["LoRA Adapter Training<br/>(Rank 16, Alpha 32)"]
        F3 --> F4["Fine-Tuned Qwen Model"]
        F5["Story Prompt"] --> F4
        F4 --> F6["Fine-Tuned Story Output"]
    end

    subgraph S_Eval["Standardized Evaluation Suite"]
        R6 --> EVAL["Evaluation Metrics Engine<br/>- Overall Quality Score (1-10)<br/>- Retention Potential<br/>- Originality<br/>- Emotional Impact<br/>- Hook Strength<br/>- AI Naturalness<br/>- Consistency"]
        F6 --> EVAL
    end
```

### Comparative Trade-off Matrix

| Metric / Dimension | Approach 1: RAG | Approach 2: Fine-Tuning |
| :--- | :--- | :--- |
| **Training Required** | None (Zero training overhead) | Requires GPU compute & training run |
| **Knowledge Agility** | Instant updates by updating database | Harder to update (requires retraining) |
| **Context Window Cost** | Consumes prompt tokens (few-shot) | Zero prompt tokens overhead |
| **Style Consistency** | Moderate (guided by exemplar prompts) | High (innate neural style adaptation) |
| **Tone Adherence** | Dependent on retrieval precision | Baked directly into model weights |
| **Computational Footprint** | Low setup, slightly higher inference latency | Higher training cost, fast inference |

---

## 5. Fault Tolerance & Resilience Architecture
1. **Ollama Service Detection:** Auto-checks Ollama connection and fallbacks gracefully to available models (`qwen3:8b`, `qwen2.5:7b`, `qwen2.5:14b`).
2. **JSON Parser & Repair:** Uses robust regex and AST recovery when small JSON syntax deviations occur in model outputs.
3. **Audio Chunking:** Kokoro processes text using phoneme chunks, preventing VRAM overflow and maintaining crisp voice flow.
4. **Video Fallback:** If background video rendering is missing assets, procedural atmospheric color-wash clips or test cards are automatically generated.

