import argparse
import sys
import os

from app.config import (
    MODEL, VOICE, ACCEPT_THRESHOLD, NUM_CANDIDATES, MAX_REWRITES,
    AUDIO_DIR, VIDEOS_DIR
)
from app.llm import generate_story, save_story
from app.critic import review_story
from app.editor import rewrite_story
from app.ranker import run_tournament
from app.tts import generate_voice
from app.video import render_short_video
from app.study import run_extension_study

def run_tournament_mode(num_candidates: int, moral: str = None, topic: str = None, skip_audio: bool = False, skip_video: bool = False, model: str = None):
    """Generates multiple story candidates centered on a moral, ranks them using AI Critic, and renders the winner."""
    print(f"\n🚀 Launching AI-Story-Engine (Mode: Tournament Ranking | Model: {model or MODEL})")
    if moral:
        print(f"🎯 Target Moral: \"{moral}\"")

    best_story, best_review, _ = run_tournament(num_candidates=num_candidates, moral=moral, topic_seed=topic, model=model)
    
    story_number = save_story(best_story)
    audio_path = os.path.join(AUDIO_DIR, f"story_{story_number:04d}.wav")
    video_path = os.path.join(VIDEOS_DIR, f"story_{story_number:04d}.mp4")

    if not skip_audio:
        try:
            generate_voice(best_story["story"], output_path=audio_path, voice=VOICE)
        except Exception as e:
            print(f"[Main] Voice generation skipped or failed: {e}")

    if not skip_video and os.path.exists(audio_path):
        try:
            render_short_video(best_story, audio_path=audio_path, output_path=video_path)
        except Exception as e:
            print(f"[Main] Video rendering skipped or failed: {e}")

    print(f"\n🎉 Pipeline Finished! Story #{story_number:04d} ready.")

def run_rewrite_mode(moral: str = None, topic: str = None, skip_audio: bool = False, skip_video: bool = False, model: str = None):
    """Generates an educational story and iteratively refines it with the Editor Agent until threshold is met."""
    print(f"\n🚀 Launching AI-Story-Engine (Mode: Iterative Rewrite | Model: {model or MODEL})")
    if moral:
        print(f"🎯 Target Moral: \"{moral}\"")
        
    story = generate_story(moral=moral, topic_seed=topic, model=model)
    best_story = story
    best_score = -1.0
    best_review = None

    for attempt in range(MAX_REWRITES):
        print(f"\n[Iteration {attempt + 1}/{MAX_REWRITES}] Evaluating story: '{story.get('title')}'")
        review = review_story(story, model=model)
        if review is None:
            print("[Main] Critic evaluation failed. Continuing.")
            break

        score = review["scores"]["overall"]
        print(f"-> Overall Score: {score:.1f}/10 (Decision: {review.get('decision', 'N/A')})")

        if score > best_score:
            best_score = score
            best_story = story
            best_review = review

        if score >= ACCEPT_THRESHOLD or review.get("decision") == "ACCEPT":
            print(f"✨ Score threshold met ({score:.1f} >= {ACCEPT_THRESHOLD})! Accepting story.")
            break

        if attempt < MAX_REWRITES - 1:
            print(f"🔧 Applying surgical rewrites based on Critic weaknesses...")
            story = rewrite_story(story, review, model=model)

    story_number = save_story(best_story)
    audio_path = os.path.join(AUDIO_DIR, f"story_{story_number:04d}.wav")
    video_path = os.path.join(VIDEOS_DIR, f"story_{story_number:04d}.mp4")

    if not skip_audio:
        try:
            generate_voice(best_story["story"], output_path=audio_path, voice=VOICE)
        except Exception as e:
            print(f"[Main] Voice generation skipped or failed: {e}")

    if not skip_video and os.path.exists(audio_path):
        try:
            render_short_video(best_story, audio_path=audio_path, output_path=video_path)
        except Exception as e:
            print(f"[Main] Video rendering skipped or failed: {e}")

    print(f"\n🎉 Pipeline Finished! Story #{story_number:04d} ready.")

def main():
    parser = argparse.ArgumentParser(
        description="AI-Story-Engine: Agentic Pipeline for Moral-Driven Educational Story Generation and Short-Form Video Creation."
    )
    parser.add_argument(
        "--moral",
        type=str,
        default=None,
        help="The core moral or life lesson the story must illustrate and conclude with."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Optional character or setting context to guide story generation."
    )
    parser.add_argument(
        "--mode",
        choices=["tournament", "rewrite", "study"],
        default="tournament",
        help="Pipeline execution mode: 'tournament' (Best-of-N), 'rewrite' (Iterative refinement), or 'study' (RAG benchmark)."
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=NUM_CANDIDATES,
        help=f"Number of story candidates in tournament mode (default: {NUM_CANDIDATES})."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Ollama model to use (e.g. qwen2.5:3b or qwen3:8b)."
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip TTS voice synthesis."
    )
    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Skip video composition."
    )

    args = parser.parse_args()

    if args.mode == "study":
        run_extension_study(num_trials=args.candidates)
    elif args.mode == "rewrite":
        run_rewrite_mode(moral=args.moral, topic=args.topic, skip_audio=args.skip_audio, skip_video=args.skip_video, model=args.model)
    else:
        run_tournament_mode(num_candidates=args.candidates, moral=args.moral, topic=args.topic, skip_audio=args.skip_audio, skip_video=args.skip_video, model=args.model)

if __name__ == "__main__":
    main()
