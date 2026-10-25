import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests

from app.config import (
    MODEL, VOICE, STORIES_DIR, AUDIO_DIR, VIDEOS_DIR,
    OLLAMA_TAGS_URL, DATA_DIR, ACCEPT_THRESHOLD, NUM_CANDIDATES
)
from app.llm import generate_story, save_story, load_saved_story
from app.critic import review_story
from app.editor import rewrite_story
from app.ranker import run_tournament, select_best_candidate
from app.tts import generate_voice
from app.video import render_short_video
from app.study import run_extension_study

app = FastAPI(
    title="AI-Story-Engine API",
    description="Agentic Backend for Educational Moral Stories and Short-Form Video Creation",
    version="2.0.0"
)

# Enable CORS for React frontend (Vite default is 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static media directories
app.mount("/media/audio", StaticFiles(directory=AUDIO_DIR), name="audio")
app.mount("/media/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

class GenerateRequest(BaseModel):
    moral: Optional[str] = None
    topic: Optional[str] = None
    mode: str = "tournament"  # "tournament", "rewrite", "single"
    candidates: int = 3
    model: Optional[str] = None
    voice: Optional[str] = "af_heart"
    generate_audio: bool = True
    generate_video: bool = True

class StudyRequest(BaseModel):
    trials: int = 2
    fine_tuned_model: Optional[str] = None
    fast: bool = True

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "AI-Story-Engine"}

@app.get("/api/models")
def get_models():
    models = []
    try:
        res = requests.get(OLLAMA_TAGS_URL, timeout=1.5)
        if res.status_code == 200:
            models = [m.get("name") for m in res.json().get("models", [])]
    except Exception:
        pass
    
    if not models:
        models = ["qwen2.5:3b", "qwen3:8b"]
        
    return {
        "models": models,
        "default": "qwen2.5:3b" if any("3b" in m for m in models) else MODEL,
        "baseline": MODEL
    }

@app.get("/api/voices")
def get_voices():
    return {
        "voices": [
            {"id": "af_heart", "name": "Heart (Female - Warm & Grade A)", "gender": "Female"},
            {"id": "af_bella", "name": "Bella (Female - Friendly & Engaging)", "gender": "Female"},
            {"id": "af_nicole", "name": "Nicole (Female - Professional)", "gender": "Female"},
            {"id": "am_adam", "name": "Adam (Male - Confident & Clear)", "gender": "Male"},
            {"id": "am_fenrir", "name": "Fenrir (Male - Deep & Dramatic)", "gender": "Male"},
            {"id": "bm_fable", "name": "Fable (British Male - Storyteller)", "gender": "Male"}
        ],
        "default": VOICE
    }

@app.post("/api/generate")
def generate_story_endpoint(req: GenerateRequest):
    active_model = req.model or MODEL
    target_moral = req.moral.strip() if req.moral else "True character is revealed through how we treat others."
    
    try:
        best_story = None
        best_review = None

        if req.mode == "tournament":
            best_story, best_review, _ = run_tournament(
                num_candidates=max(1, req.candidates),
                moral=target_moral,
                topic_seed=req.topic,
                model=active_model
            )
        elif req.mode == "rewrite":
            story = generate_story(moral=target_moral, topic_seed=req.topic, model=active_model)
            best_story = story
            best_score = -1.0
            for attempt in range(3):
                review = review_story(story, model=active_model)
                if not review:
                    break
                score = review["scores"]["overall"]
                if score > best_score:
                    best_score = score
                    best_story = story
                    best_review = review
                if score >= ACCEPT_THRESHOLD or review.get("decision") == "ACCEPT":
                    break
                if attempt < 2:
                    story = rewrite_story(story, review, model=active_model)
        else:
            best_story = generate_story(moral=target_moral, topic_seed=req.topic, model=active_model)
            best_review = review_story(best_story, model=active_model)

        story_id = save_story(best_story)
        audio_filename = f"story_{story_id:04d}.wav"
        video_filename = f"story_{story_id:04d}.mp4"
        
        audio_path = os.path.join(AUDIO_DIR, audio_filename)
        video_path = os.path.join(VIDEOS_DIR, video_filename)

        audio_url = None
        video_url = None

        if req.generate_audio:
            try:
                generate_voice(best_story["story"], output_path=audio_path, voice=req.voice or VOICE)
                audio_url = f"/media/audio/{audio_filename}"
            except Exception as e:
                print(f"[API] Audio error: {e}")

        if req.generate_video and os.path.exists(audio_path):
            try:
                render_short_video(best_story, audio_path=audio_path, output_path=video_path)
                video_url = f"/media/videos/{video_filename}"
            except Exception as e:
                print(f"[API] Video error: {e}")

        return {
            "success": True,
            "story_id": story_id,
            "story": best_story,
            "review": best_review,
            "audio_url": audio_url,
            "video_url": video_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stories")
def list_stories():
    os.makedirs(STORIES_DIR, exist_ok=True)
    files = [f for f in os.listdir(STORIES_DIR) if f.startswith("story_") and f.endswith(".json")]
    files.sort(reverse=True)
    
    stories_list = []
    for f in files:
        story_id = int(f.replace("story_", "").replace(".json", ""))
        filepath = os.path.join(STORIES_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            
            audio_file = f"story_{story_id:04d}.wav"
            video_file = f"story_{story_id:04d}.mp4"
            
            stories_list.append({
                "id": story_id,
                "title": data.get("title", f"Story #{story_id}"),
                "hook": data.get("hook", ""),
                "moral": data.get("moral", ""),
                "story": data.get("story", ""),
                "audio_url": f"/media/audio/{audio_file}" if os.path.exists(os.path.join(AUDIO_DIR, audio_file)) else None,
                "video_url": f"/media/videos/{video_file}" if os.path.exists(os.path.join(VIDEOS_DIR, video_file)) else None
            })
        except Exception:
            continue

    return {"stories": stories_list}

@app.post("/api/study")
def run_study(req: StudyRequest):
    try:
        if req.fine_tuned_model:
            available_models = get_models()["models"]
            if req.fine_tuned_model not in available_models:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"'{req.fine_tuned_model}' is not an installed Ollama model. "
                        f"Choose one from: {', '.join(available_models)}"
                    )
                )
            if req.fine_tuned_model == MODEL:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"'{req.fine_tuned_model}' is the baseline model, not a fine-tuned model. "
                        "Enter a separately fine-tuned Ollama model."
                    )
                )
        summary = run_extension_study(
            num_trials=max(1, min(req.trials, 5)),
            fine_tuned_model=req.fine_tuned_model,
            fast=req.fast
        )
        return {"success": True, "summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
