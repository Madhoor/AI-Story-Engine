import os
import json
from typing import List, Dict
from app.llm import generate_story
from app.critic import review_story
from app.config import MODEL, FINETUNED_MODEL, DATA_DIR

VIRAL_STORY_EXEMPLARS = [
    {
        "title": "The Key Under the Floorboard",
        "hook": "I found a copper key hidden under my floorboards that fit my neighbor's door.",
        "pacing_style": "Fast setup, rising mystery, immediate stakes, high believability",
        "twist_type": "The neighbor left it intentionally for emergency protection"
    },
    {
        "title": "The 3 AM Package",
        "hook": "A courier delivered an unmarked parcel at 3 AM addressed to the previous tenant.",
        "pacing_style": "Unfolding intrigue, sensory details, natural dialogue, emotional turning point",
        "twist_type": "The tenant had staged their disappearance to escape loan sharks"
    },
    {
        "title": "The Silent Commute",
        "hook": "Every morning on the subway, the same stranger handed me an uncreased train ticket.",
        "pacing_style": "Everyday relatability, escalating curiosity, poignant revelation",
        "twist_type": "He was paying forward an old debt owed to my late father"
    }
]

def generate_rag_story(topic_seed: str = None, model: str = None, fast: bool = False) -> dict:
    """
    RAG Approach: Injects high-retention structural exemplars into the prompt context.
    """
    exemplar_context = "### High-Retention Viral Story Exemplars (Reference Style & Structure):\n"
    for ex in VIRAL_STORY_EXEMPLARS:
        exemplar_context += (
            f"- Title: {ex['title']}\n"
            f"  Hook: \"{ex['hook']}\"\n"
            f"  Pacing: {ex['pacing_style']}\n"
            f"  Twist: {ex['twist_type']}\n"
        )
    
    enriched_prompt = (
        f"{topic_seed or 'An unforgettable personal experience.'}\n\n"
        f"{exemplar_context}\n"
        "Emulate the subtle pacing, psychological tension, and authentic voice of these exemplars."
    )
    
    return generate_story(topic_seed=enriched_prompt, model=model, fast=fast)

def run_extension_study(
    num_trials: int = 2,
    fine_tuned_model: str = None,
    fast: bool = False
) -> Dict:
    """
    Runs comparative evaluation between baseline, RAG, and an optional fine-tuned
    Ollama model configured with FINETUNED_MODEL or fine_tuned_model.
    Evaluates each across the key benchmark metrics:
    - Overall Quality (1-10)
    - Retention Potential
    - Originality
    - Emotional Impact
    - Hook Strength
    - AI Naturalness
    """
    num_trials = max(1, min(num_trials, 5))
    print("\n" + "=" * 70)
    print("STARTING EXTENSION STUDY: BASELINE vs. RAG vs. FINE-TUNED MODEL")
    print(f"Model: {MODEL} | Trials per method: {num_trials}")
    print("=" * 70)

    results = {
        "baseline": [],
        "rag": [],
        "fine_tuned": []
    }
    errors = {}
    active_fine_tuned_model = fine_tuned_model or FINETUNED_MODEL
    if active_fine_tuned_model and active_fine_tuned_model == MODEL:
        raise ValueError(
            f"'{active_fine_tuned_model}' is the baseline model, not a fine-tuned model. "
            "Enter the name of a separately fine-tuned Ollama model."
        )

    metrics = ["overall", "retention", "hook", "originality", "emotion", "ai_naturalness"]

    for trial in range(num_trials):
        print(f"\n--- Trial {trial + 1} of {num_trials} ---")
        
        # 1. Baseline Run
        print("Generating Baseline Story...")
        try:
            base_story = generate_story(model=MODEL, fast=fast)
            base_review = review_story(base_story, model=MODEL, fast=fast)
            if base_review:
                results["baseline"].append({"story": base_story, "review": base_review})
        except Exception as e:
            print(f"Baseline generation failed: {e}")
            errors["baseline"] = str(e)

        # 2. RAG Run
        print("Generating RAG-Augmented Story...")
        try:
            rag_story = generate_rag_story(model=MODEL, fast=fast)
            rag_review = review_story(rag_story, model=MODEL, fast=fast)
            if rag_review:
                results["rag"].append({"story": rag_story, "review": rag_review})
        except Exception as e:
            print(f"RAG generation failed: {e}")
            errors["rag"] = str(e)

        if active_fine_tuned_model:
            print(f"Generating Fine-Tuned Story with {active_fine_tuned_model}...")
            try:
                tuned_story = generate_story(model=active_fine_tuned_model, fast=fast)
                tuned_review = review_story(tuned_story, model=active_fine_tuned_model, fast=fast)
                if tuned_review:
                    results["fine_tuned"].append({"story": tuned_story, "review": tuned_review})
            except Exception as e:
                print(f"Fine-tuned generation failed: {e}")
                errors["fine_tuned"] = str(e)

    # Compute Averages
    def get_avg(category_list, metric_key):
        vals = [c["review"]["scores"].get(metric_key, 0.0) for c in category_list]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    summary = {}
    for m in metrics:
        summary[m] = {
            "baseline_avg": get_avg(results["baseline"], m),
            "rag_avg": get_avg(results["rag"], m),
            "fine_tuned_avg": get_avg(results["fine_tuned"], m)
        }

    if not active_fine_tuned_model:
        summary["_notice"] = {
            "baseline_avg": "Fine-tuned model not configured",
            "rag_avg": "Enter an Ollama fine-tuned model name",
            "fine_tuned_avg": "Not evaluated"
        }
    if errors:
        summary["_errors"] = errors
    if not any(results.values()):
        raise RuntimeError(
            "No benchmark arm produced a valid story. Check Ollama output and model availability."
        )

    # Print Report Table
    print("\n" + "=" * 60)
    print("BENCHMARK COMPARISON SUMMARY (1-10 Scale)")
    print("-" * 60)
    print(f"{'Metric':<18} | {'Baseline':<12} | {'RAG':<12} | {'Fine-Tuned':<12}")
    print("-" * 60)
    for m in metrics:
        b = summary[m]["baseline_avg"]
        r = summary[m]["rag_avg"]
        tuned = summary[m]["fine_tuned_avg"]
        print(f"{m.capitalize():<18} | {b:<12.2f} | {r:<12.2f} | {tuned:<12.2f}")
    print("=" * 60)

    # Save Study Artifacts
    report_path = os.path.join(DATA_DIR, "study_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=4)
    print(f"\n[Extension Study] Benchmark results saved to: {report_path}")

    return summary
