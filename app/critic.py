import json
import re
import requests

from app.config import OLLAMA_URL, MODEL, CRITIC_PROMPT_PATH
from app.llm import clean_json_response, call_ollama

def load_prompt() -> str:
    with open(CRITIC_PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()

def review_story(story: dict, model: str = None, fast: bool = False) -> dict:
    """
    Evaluates educational story package against 9 criteria including Moral Clarity.
    """
    active_model = model or MODEL
    prompt = load_prompt() + "\n\nStory Package:\n" + json.dumps(story, indent=4)
    
    payload = {
        "model": active_model,
        "prompt": prompt,
        "format": "json",
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_ctx": 2048 if fast else 4096,
            "num_predict": 180 if fast else 320
        }
    }

    try:
        raw_review = call_ollama(payload, timeout=360)
    except Exception as e:
        print(f"[AI Critic] Request error: {e}")
        return None
    
    try:
        review = clean_json_response(raw_review)
    except json.JSONDecodeError:
        print(f"[AI Critic] Failed to parse critic review JSON: {raw_review[:200]}")
        return None

    # Verify and normalize score structure
    if "scores" not in review or not isinstance(review["scores"], dict):
        print("[AI Critic] Invalid structure: missing 'scores' dict.")
        return None
        
    scores = review["scores"]
    required_dimensions = [
        "hook", "pacing", "emotion", "believability",
        "moral_clarity", "retention", "originality", "ai_naturalness", "comment_potential"
    ]

    # Map legacy 'twist' to 'moral_clarity' if present
    if "twist" in scores and "moral_clarity" not in scores:
        scores["moral_clarity"] = scores["twist"]
    
    for dim in required_dimensions:
        if dim not in scores:
            scores[dim] = 7.0
        else:
            try:
                scores[dim] = float(scores[dim])
            except (ValueError, TypeError):
                scores[dim] = 7.0

    if "overall" not in scores or not scores["overall"]:
        scores["overall"] = round(sum(scores[d] for d in required_dimensions) / len(required_dimensions), 1)
    else:
        scores["overall"] = float(scores["overall"])

    if "decision" not in review or not review["decision"]:
        review["decision"] = "ACCEPT" if scores["overall"] >= 8.0 else "REWRITE"

    return review
