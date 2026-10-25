import json
from app.config import MODEL, EDITOR_PROMPT_PATH
from app.llm import clean_json_response, call_ollama

def load_prompt() -> str:
    with open(EDITOR_PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()

def rewrite_story(story: dict, review: dict, model: str = None) -> dict:
    """
    Applies surgical micro-edits to a story using the Critic's feedback.
    Preserves unaffected sections, characters, and overall plot.
    """
    active_model = model or MODEL
    prompt = (
        load_prompt()
        + "\n\nStory Package:\n"
        + json.dumps(story, indent=4)
        + "\n\nCritic Review:\n"
        + json.dumps(review, indent=4)
    )

    payload = {
        "model": active_model,
        "prompt": prompt,
        "format": "json",
        "options": {
            "temperature": 0.6,
            "top_p": 0.9,
            "num_ctx": 4096
        }
    }

    try:
        response_text = call_ollama(payload)
    except Exception as e:
        print(f"[Story Rewriter] Request error: {e}")
        return story
    
    try:
        revised_story = clean_json_response(response_text)
    except json.JSONDecodeError:
        print("[Story Rewriter] Failed to parse rewriter response. Retaining original story.")
        return story

    # Fallback merge: ensure required fields are not dropped
    for key in ["title", "hook", "story", "thumbnail_prompt", "scene_prompts"]:
        if key not in revised_story or not revised_story[key]:
            revised_story[key] = story.get(key, "")

    return revised_story
