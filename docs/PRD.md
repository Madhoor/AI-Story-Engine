# Product Requirements Document (PRD)
## Project: AI-Story-Engine
**Sub-title:** An Agentic AI Pipeline for Automated Story Generation, Evaluation, and Short-Form Video Creation  
**Authors:** Siddhant Lawand (Roll No: 9), Madhoor Deo (Roll No: 13) | Panel C1  
**Status:** In Active Development  
**Target Platform:** YouTube Shorts, Instagram Reels, TikTok  

---

## 1. Executive Summary
The **AI-Story-Engine** is a fully autonomous, 100% local agentic content creation pipeline designed to generate moral-driven educational stories and modern fables, critically evaluate and refine them through a multi-agent feedback loop, synthesize natural voice narration, and produce high-engagement vertical short-form videos (9:16).

By taking a user-specified **Moral or Life Lesson** as input, the engine crafts a story that organically illustrates the principle and delivers the moral powerfully at the end of the narrative. By leveraging open-source local LLMs (Ollama with Qwen models), high-fidelity local text-to-speech (Kokoro TTS), and automated video rendering (MoviePy / FFmpeg), the platform operates with zero API costs, zero cloud dependency, and total data privacy.

---

## 2. Problem Statement
Short-form content creators face significant bottlenecks:
1. **Ideation & Writing Fatigue:** Creating compelling, high-retention hooks and authentic first-person stories consistently requires hours of manual drafting.
2. **Quality Variance:** Unassisted LLMs tend to generate cliché-ridden, overly dramatic, or clearly artificial stories that viewers quickly scroll past.
3. **Expensive Cloud Toolchains:** Combining proprietary LLM APIs (OpenAI/Anthropic), cloud TTS (ElevenLabs), and commercial video editing suites is costly and difficult to automate at scale.
4. **Complex Editing Workflow:** Synchronizing voiceover, background footage, dynamic captions, and background music manually in NLE software is time-consuming.

---

## 3. Product Vision & Goals
### 3.1 Vision
A one-click autonomous engine that converts a concept or prompt into a production-ready, high-retention vertical short video with human-level storytelling and voice narration.

### 3.2 Key Objectives
- **100% Local Execution:** No paid API keys required; runs locally on consumer GPU hardware via Ollama and local models.
- **Agentic Quality Assurance:** Incorporate a specialized AI Critic agent that evaluates stories across 9 viral retention metrics before approval.
- **Dual Optimization Strategies:** Support both iterative self-improvement (critic-guided rewriting) and Best-of-N candidate ranking.
- **End-to-End Automation:** Seamless transition from Story Prompt -> LLM Generation -> Critic Assessment -> Audio Synthesis -> Video Assembly with Subtitles.
- **Comparative Research Extension:** Benchmark RAG (Retrieval-Augmented Generation) against LoRA Fine-Tuning for viral story generation.

---

## 4. User Personas & Target Audience
1. **Faceless Channel Creators:** Operators running automated YouTube Shorts, Instagram Reels, and TikTok channels seeking scalable, high-volume production.
2. **Storytellers & Writers:** Creators who want rapid prototyping of twists, narrative arcs, and audio narrations.
3. **AI Researchers & Students:** Evaluators analyzing multi-agent workflows, local LLM capabilities (Qwen), and domain adaptation techniques (RAG vs Fine-Tuning).

---

## 5. Key Features & Functional Requirements

### 5.1 Story Generation Agent
- **FR-1.1:** Generate original first-person ("I", "me", "my") stories in authentic Reddit-style confession format.
- **FR-1.2:** Enforce word count constraints tailored for 50–70 second narrations (target: 300–350 words).
- **FR-1.3:** Output structured JSON containing `title`, `hook`, `story`, `thumbnail_prompt`, and `scene_prompts` (exactly 4 progression scenes).
- **FR-1.4:** Enforce strict anti-cliché constraints (banning phrases like "little did I know", "my blood ran cold", etc.).

### 5.2 AI Critic (Quality Analyzer)
- **FR-2.1:** Evaluate stories across 9 key retention dimensions on a 1–10 scale:
  1. *Hook Strength*
  2. *Pacing*
  3. *Emotional Impact*
  4. *Believability*
  5. *Twist Quality*
  6. *Audience Retention*
  7. *Originality*
  8. *AI Naturalness*
  9. *Comment Potential*
- **FR-2.2:** Calculate weighted `overall` score and `confidence` metric (0–100).
- **FR-2.3:** Detect retention drop-off timestamps and identify specific sections exhibiting AI artifacts.
- **FR-2.4:** Provide explicit verdicts: `ACCEPT`, `REWRITE`, or `REJECT`.

### 5.3 Story Rewriter / Ranking Engine
- **FR-3.1 (Rewrite Mode):** Targeted micro-edits addressing specific critic weaknesses while preserving plot, characters, and unaffected paragraphs.
- **FR-3.2 (Ranking Mode):** Generate $N$ diverse candidate stories, evaluate each with the Critic, and select the highest-scoring candidate (with tie-breaking on Hook, Originality, and Believability).

### 5.4 Text-to-Speech (TTS) Engine
- **FR-4.1:** Utilize Kokoro TTS for ultra-realistic local neural voice synthesis.
- **FR-4.2:** Support multiple voice personas (e.g., `af_heart`, `af_bella`, `am_adam`, `bm_fable`, `am_fenrir`).
- **FR-4.3:** Export 24kHz master WAV files structured in `data/audio/`.

### 5.5 Video Generation & Compositor Engine
- **FR-5.1:** Produce vertical 9:16 videos (1080x1920) at 30 FPS.
- **FR-5.2:** Select and loop atmospheric background video assets (`assets/backgrounds/`).
- **FR-5.3:** Overlay dynamic word-by-word or phrase-level subtitles with high-visibility styling (custom fonts, outline, shadow).
- **FR-5.4:** Mix narration audio with ambient background music (`assets/music/`) with automatic audio ducking.

### 5.6 Extension Study: RAG vs. Fine-Tuning
- **FR-6.1:** Provide evaluation framework comparing baseline Qwen vs RAG-augmented generation vs Fine-Tuned Qwen checkpoint.
- **FR-6.2:** Measure performance against standardized benchmark metrics: Overall Quality, Retention Potential, Originality, Emotional Impact, Hook Strength, and Human Preference.

---

## 6. Non-Functional Requirements
- **Performance:** End-to-end generation under 3 minutes per short on modern consumer GPUs (RTX 3060/4060 or better).
- **Reliability:** Strict JSON schema validation with automatic recovery and repair for malformed LLM responses.
- **Privacy & Security:** Zero telemetry, no cloud API calls, 100% offline functionality.
- **Portability:** Clean modular Python architecture running on Windows, Linux, and macOS.

---

## 7. Success Metrics
- **Audience Retention Rate:** Short completion rate > 75% on YouTube Shorts.
- **Critic Pass Rate:** Stories achieve overall score $\ge 8.0/10$ within candidate selection.
- **Generation Time:** Full pipeline from prompt to MP4 video in under 180 seconds.
- **Zero API Incurred Cost:** \$0.00 infrastructure cost per video generated.

