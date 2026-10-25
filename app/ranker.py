from typing import List, Dict, Tuple, Optional
from app.llm import generate_story
from app.critic import review_story

def calculate_composite_score(review: Dict) -> float:
    """
    Computes a weighted viral retention score incorporating Moral Clarity.
    """
    scores = review.get("scores", {})
    overall = scores.get("overall", 0.0)
    retention = scores.get("retention", 0.0)
    hook = scores.get("hook", 0.0)
    moral_clarity = scores.get("moral_clarity", scores.get("twist", 0.0))
    believability = scores.get("believability", 0.0)

    composite = (
        (overall * 0.35) +
        (moral_clarity * 0.25) +
        (retention * 0.15) +
        (hook * 0.15) +
        (believability * 0.10)
    )
    return round(composite, 2)

def select_best_candidate(candidates: List[Tuple[Dict, Dict]]) -> Tuple[Dict, Dict]:
    """
    Selects the highest quality candidate from (story, review) pairs.
    """
    if not candidates:
        raise ValueError("Candidate list cannot be empty.")

    best_story = None
    best_review = None
    best_rank_key = (-1, -1, -1, -1, -1)

    print("\n" + "=" * 70)
    print(f"{'#':<3} | {'Title':<22} | {'Overall':<7} | {'Moral':<6} | {'Hook':<5} | {'Comp':<6}")
    print("-" * 70)

    for idx, (story, review) in enumerate(candidates, 1):
        scores = review.get("scores", {})
        overall = scores.get("overall", 0.0)
        comp = calculate_composite_score(review)
        hook = scores.get("hook", 0.0)
        moral_score = scores.get("moral_clarity", scores.get("twist", 0.0))
        retention = scores.get("retention", 0.0)
        ai_nat = scores.get("ai_naturalness", 0.0)

        title = story.get("title", f"Candidate {idx}")[:21]
        print(f"{idx:<3} | {title:<22} | {overall:<7.1f} | {moral_score:<6.1f} | {hook:<5.1f} | {comp:<6.2f}")

        rank_key = (comp, overall, moral_score, hook, ai_nat)
        if rank_key > best_rank_key:
            best_rank_key = rank_key
            best_story = story
            best_review = review

    print("=" * 70 + "\n")
    return best_story, best_review

def run_tournament(
    num_candidates: int = 3,
    moral: Optional[str] = None,
    topic_seed: Optional[str] = None,
    model: Optional[str] = None
) -> Tuple[Dict, Dict, List]:
    """
    Generates N candidates around the given moral, evaluates with AI Critic, and selects the winner.
    """
    print(f"\n[Tournament] Initiating tournament with {num_candidates} candidate stories...")
    if moral:
        print(f"[Tournament] Target Moral: \"{moral}\"")

    evaluated_candidates = []

    for i in range(num_candidates):
        print(f"\n[Tournament] Generating Candidate {i+1} of {num_candidates}...")
        try:
            story = generate_story(moral=moral, topic_seed=topic_seed, model=model)
        except Exception as e:
            print(f"[Tournament] Story generation error on candidate {i+1}: {e}")
            continue

        print(f"[Tournament] Reviewing Candidate {i+1}: '{story.get('title', '')}'...")
        review = review_story(story, model=model)
        if review is None:
            print(f"[Tournament] Critic failed for Candidate {i+1}. Skipping.")
            continue

        evaluated_candidates.append((story, review))

    if not evaluated_candidates:
        raise RuntimeError("All candidate generations failed.")

    best_story, best_review = select_best_candidate(evaluated_candidates)
    print(f"[Tournament] Selected Winner: '{best_story.get('title')}' (Overall: {best_review['scores']['overall']}/10)")
    return best_story, best_review, evaluated_candidates
