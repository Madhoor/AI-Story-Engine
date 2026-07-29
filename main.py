import json

from app.llm import generate_story, save_story
from app.critic import review_story
from app.editor import rewrite_story
from app.tts import generate_voice

def main():
    NUM_STORIES = 5

    print("WORKING...\n")

    best_story = None
    best_review = None
    best_score = -1

    for i in range(NUM_STORIES):

        print(f"\n===== Story {i+1} =====")

        print(f"\nGenerating story {i+1}:\n")
        story = generate_story()
        print(f"\nReviewing story {i+1}:\n")

        review = review_story(story)

        if review is None:
            print("Critic failed. Skipping story.")
            continue
        
        score = review["scores"]["overall"]

        print(f"Score: {score}")

        if score > best_score:
            best_story = story
            best_review = review
            best_score = score

    print(f"\nBest score: {best_score}")


    story_number = save_story(best_story)
    generate_voice(best_story["story"], f"data/audio/story_{story_number:04d}.wav")

    
    
    # if we wanyt to rewrite the story based on the review, we can uncomment the following lines
    # but after testing, it seems that the rewriting is not necessary, as the generated stories are already good enough.
    
'''    
    MAX_REWRITES = 3
    story = generate_story()

    best_story = story
    best_review = None
    best_score = -1

    for attempt in range(MAX_REWRITES):

        print(f"\n=== Attempt {attempt + 1} ===")

        review = review_story(story)
        score = review["scores"]["overall"]

        print(f"Score: {score}")

        if score > best_score:
            best_score = score
            best_story = story
            best_review = review

        if score >= 9:
            print("Excellent story found!")
            break

        # story = rewrite_story(story, review)

    print(f"\nBest score: {best_score}")

    save_story(best_story)

save_story(story)
'''
if __name__ == "__main__":
    main()
