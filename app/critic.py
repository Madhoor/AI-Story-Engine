import json
import requests

from app.config import OLLAMA_URL, MODEL

OLLAMA_URL = OLLAMA_URL
MODEL = MODEL

def load_prompt():
    with open("prompts/critic_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


def review_story(story):
    prompt = load_prompt() + "\n\nStory Package:\n" + json.dumps(story, indent=4)
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(OLLAMA_URL, json=payload)

    # # review = json.loads(response.json()["response"]) #temp change

    # print("\n========== RAW REVIEW ==========\n")
    # print(raw_review)
    # print("\n===============================\n")

    # review = json.loads(raw_review)
    # return reviewraw_review = response.json()["response"]

    raw_review = response.json()["response"]
    try:
        review = json.loads(raw_review)
    except json.JSONDecodeError:
        print("\nFailed to parse review JSON:\n")
        print(raw_review)
        return None
    if "scores" not in review or "overall" not in review["scores"]:
        print("\nInvalid critic structure:\n")
        print(json.dumps(review, indent=4))
        return None
    
    return review


if __name__ == "__main__":
    # print("Critic initialized.")
    # print ("res")
    pass