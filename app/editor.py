import json
import requests

from app.config import MODEL, OLLAMA_URL


def load_prompt():
    with open("prompts/editor_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def rewrite_story(story, review):

    prompt = (
        load_prompt()
        + "\n\nStory Package:\n"
        + json.dumps(story, indent=4)
        + "\n\nCritic Review:\n"
        + json.dumps(review, indent=4)
    )

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload
    )

    
    response_text = response.json()["response"]

    print("\n===== RAW EDITOR RESPONSE =====\n")
    print(response_text)
    print("\n===============================\n")

    return json.loads(response_text)