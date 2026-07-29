import json
from urllib import response
import os 
from os import path
import requests


from app.critic import review_story
from app.config import OLLAMA_URL, MODEL

OLLAMA_URL = OLLAMA_URL
MODEL = MODEL

def load_prompt():
    with open("prompts/story_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()

def generate_story():
    payload = {
        "model": MODEL,
        "prompt": load_prompt(),
        "stream": False,
        "format": "json"
    }

    response = requests.post(OLLAMA_URL, json=payload)
    story_txt = response.json()["response"]
    story = json.loads(story_txt)
    return story

def save_story(story):
    folder = "data/stories"
    os.makedirs(folder, exist_ok=True)

    existing = [
        f for f in os.listdir(folder)
        if f.startswith("story_") and f.endswith(".json")
    ]

    if existing:
        numbers = [
            int(f.replace("story_", "").replace(".json", ""))
            for f in existing
        ]
        next_number = max(numbers) + 1
    else:
        next_number = 1

    filename = f"story_{next_number:04d}.json"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(story, file, indent=4, ensure_ascii=False)

    print(f"Story saved to: {filepath}")

    return next_number

if __name__ == "__main__":
   
    story = generate_story()
    review = review_story(story)

    print(json.dumps(review, indent=4))
    save_story(story)






















