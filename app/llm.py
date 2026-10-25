import json
import os
import re
import requests

from app.config import OLLAMA_URL, MODEL, STORY_PROMPT_PATH, STORIES_DIR

def clean_json_response(raw_text: str) -> dict:
    """
    Cleans markdown formatting, code fences, or extraneous tokens
    from Ollama LLM responses and parses into a dictionary.
    """
    text = raw_text.strip()
    
    # Strip markdown backticks
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
        
    # Extract outermost JSON object if preamble text exists
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        text = text[start_idx:end_idx + 1]

    return json.loads(text)

def call_ollama(payload: dict, timeout: int = 360) -> str:
    """
    Executes streaming request to Ollama to prevent socket read timeouts
    during model loading and generation. Supports automatic fallback.
    """
    payload["stream"] = True
    payload.setdefault("keep_alive", "10m")
    if str(payload.get("model", "")).lower().startswith("qwen3"):
        payload["think"] = False
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=timeout)
        response.raise_for_status()

        full_text = []
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                full_text.append(chunk.get("response", ""))
                if chunk.get("done", False):
                    break
        result = "".join(full_text).strip()
        if not result:
            raise ConnectionError(
                f"Ollama returned an empty response for model '{payload.get('model', '')}'. "
                "Verify the model is installed and retry."
            )
        return result
    except requests.exceptions.Timeout:
        active_model = payload.get("model", "")
        if "3b" not in active_model.lower():
            print(f"[Ollama] Model '{active_model}' timed out. Attempting fast fallback to 'qwen2.5:3b'...")
            fallback_payload = dict(payload)
            fallback_payload["model"] = "qwen2.5:3b"
            return call_ollama(fallback_payload, timeout=180)
        raise ConnectionError(
            f"Ollama generation timed out after {timeout} seconds on model '{active_model}'. "
            "Ensure Ollama has sufficient CPU/GPU resources."
        )
    except requests.exceptions.RequestException as e:
        raise ConnectionError(
            f"Failed to communicate with Ollama at {OLLAMA_URL}. Ensure Ollama is running ('ollama serve'). Details: {e}"
        )

def load_prompt(moral: str = None, topic_seed: str = None) -> str:
    """
    Loads story generation prompt and appends the target moral and optional topic seed.
    """
    with open(STORY_PROMPT_PATH, "r", encoding="utf-8") as file:
        prompt = file.read()
    
    if moral:
        prompt += f"\n\n## Target Moral / Life Lesson\nThe story must be built specifically around this moral lesson: \"{moral}\".\nThe narrative events must clearly demonstrate why this lesson is true, and the moral must be stated powerfully at the end of the story as its climax and conclusion.\n"

    if topic_seed:
        prompt += f"\n## Setting or Character Context\nIncorporate this setting or context: {topic_seed}\n"
        
    return prompt

def generate_story(moral: str = None, topic_seed: str = None, model: str = None, fast: bool = False) -> dict:
    """
    Calls local Ollama instance running Qwen model to generate an educational story with a moral.
    """
    active_model = model or MODEL
    prompt_text = load_prompt(moral=moral, topic_seed=topic_seed)
    
    payload = {
        "model": active_model,
        "prompt": prompt_text,
        "format": "json",
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "num_ctx": 2048 if fast else 4096,
            "num_predict": 420 if fast else 700
        }
    }

    raw_response = call_ollama(payload, timeout=360)
    try:
        story = clean_json_response(raw_response)
    except json.JSONDecodeError as err:
        raise ValueError(f"Failed to parse LLM story output as JSON: {err}\nRaw output: {raw_response[:300]}")

    # Validate schema
    required_keys = ["title", "hook", "story"]
    for key in required_keys:
        if key not in story or not story[key]:
            raise ValueError(f"Generated story missing required key: '{key}'")
            
    if "moral" not in story or not story["moral"]:
        story["moral"] = moral or "Actions have consequences, and true character is revealed through adversity."

    if "scene_prompts" not in story or not isinstance(story["scene_prompts"], list):
        story["scene_prompts"] = [
            f"Cinematic scene representing the hook: {story['hook']}",
            "Cinematic scene depicting the character facing a moral dilemma",
            "Cinematic scene showing the critical turning point and realization",
            f"Cinematic scene illustrating the moral resolution: {story['moral']}"
        ]

    return story

def save_story(story: dict) -> int:
    """
    Saves story package to data/stories/story_{index:04d}.json and returns index.
    """
    os.makedirs(STORIES_DIR, exist_ok=True)

    existing = [
        f for f in os.listdir(STORIES_DIR)
        if f.startswith("story_") and f.endswith(".json")
    ]

    if existing:
        numbers = []
        for f in existing:
            try:
                num = int(f.replace("story_", "").replace(".json", ""))
                numbers.append(num)
            except ValueError:
                continue
        next_number = max(numbers) + 1 if numbers else 1
    else:
        next_number = 1

    filename = f"story_{next_number:04d}.json"
    filepath = os.path.join(STORIES_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(story, file, indent=4, ensure_ascii=False)

    print(f"[Story Generator] Story #{next_number} saved to: {filepath}")
    return next_number

def load_saved_story(story_id: int) -> dict:
    """Loads a previously saved story by ID."""
    filename = f"story_{story_id:04d}.json"
    filepath = os.path.join(STORIES_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Story #{story_id} not found at {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
