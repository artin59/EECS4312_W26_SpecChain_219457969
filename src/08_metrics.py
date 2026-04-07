"""
EECS 4312 - SpecChain Project
Step 4.5: Compute Metrics for Automated Pipeline

Output: metrics/metrics_auto.json
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
GROUPS_PATH   = Path("data/review_groups_auto.json")
PERSONAS_PATH = Path("personas/personas_auto.json")
SPEC_PATH     = Path("spec/spec_auto.md")
TESTS_PATH    = Path("tests/tests_auto.json")

OUTPUT_PATH   = Path("metrics/metrics_auto.json")

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_spec_requirements(md_text):
    """Extract FR_auto_X IDs from spec"""
    pattern = r"# Requirement ID: (FR_auto_\d+)"
    return re.findall(pattern, md_text)

# ---------------------------------------------------------------------------
# METRICS
# ---------------------------------------------------------------------------

def compute_metrics():
    groups_data   = load_json(GROUPS_PATH)
    personas_data = load_json(PERSONAS_PATH)
    tests_data    = load_json(TESTS_PATH)

    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        spec_text = f.read()

    groups   = groups_data["groups"]
    personas = personas_data["personas"]
    tests    = tests_data["tests"]

    req_ids = load_spec_requirements(spec_text)

    # -----------------------------
    # BASIC COUNTS
    # -----------------------------
    dataset_size = sum(g["review_count"] for g in groups)
    persona_count = len(personas)
    requirements_count = len(req_ids)
    tests_count = len(tests)

    # -----------------------------
    # TRACEABILITY LINKS
    # -----------------------------
    # persona → group
    persona_links = sum(1 for p in personas if p.get("derived_from_group"))

    # requirement → persona (approx: persona name appears in spec)
    req_links = 0
    for p in personas:
        if p.get("name") and p["name"] in spec_text:
            req_links += 1

    # test → requirement
    test_links = len(tests)

    traceability_links = persona_links + req_links + test_links

    # -----------------------------
    # REVIEW COVERAGE
    # -----------------------------
    total_reviews_in_groups = dataset_size  # all grouped
    review_coverage = (
        total_reviews_in_groups / dataset_size if dataset_size else 0
    )

    # -----------------------------
    # TRACEABILITY RATIO
    # -----------------------------
    linked_requirements = len(set(t["requirement_id"] for t in tests))
    traceability_ratio = (
        linked_requirements / requirements_count
        if requirements_count else 0
    )

    # -----------------------------
    # TESTABILITY RATE
    # -----------------------------
    testability_rate = traceability_ratio  # same definition

    # -----------------------------
    # AMBIGUITY RATIO
    # -----------------------------
    ambiguous_words = ["may", "might", "could", "etc", "various", "some"]

    requirement_blocks = re.findall(
        r"(# Requirement ID: FR_auto_\d+[\s\S]*?)(?=\n# Requirement ID:|\Z)",
        spec_text
    )

    ambiguous_count = 0
    for block in requirement_blocks:
        block_lower = block.lower()
        if any(word in block_lower for word in ambiguous_words):
            ambiguous_count += 1

    ambiguity_ratio = (
        ambiguous_count / requirements_count
        if requirements_count else 0
    )

    # -----------------------------
    # FINAL OUTPUT FORMAT
    # -----------------------------
    return {
        "pipeline": "automated",
        "dataset_size": dataset_size,
        "persona_count": persona_count,
        "requirements_count": requirements_count,
        "tests_count": tests_count,
        "traceability_links": traceability_links,
        "review_coverage": round(review_coverage, 2),
        "traceability_ratio": round(traceability_ratio, 2),
        "testability_rate": round(testability_rate, 2),
        "ambiguity_ratio": round(ambiguity_ratio, 2)
    }

# ---------------------------------------------------------------------------
# SAVE
# ---------------------------------------------------------------------------

def save_metrics(metrics):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Saved {OUTPUT_PATH}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    metrics = compute_metrics()

    print("\n[METRICS SUMMARY]")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    save_metrics(metrics)

    print("\n[DONE] Step 4.5 complete.")

if __name__ == "__main__":
    main()