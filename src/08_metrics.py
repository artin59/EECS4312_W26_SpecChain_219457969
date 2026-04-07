"""
EECS 4312 - SpecChain Project
Compute Metrics for Automated + Hybrid Pipelines

Outputs:
- metrics/metrics_auto.json
- metrics/metrics_hybrid.json
- metrics/metrics_summary.json
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
DATASET_PATH = Path("data/reviews_clean.jsonl")

AUTO_PATHS = {
    "groups": Path("data/review_groups_auto.json"),
    "personas": Path("personas/personas_auto.json"),
    "spec": Path("spec/spec_auto.md"),
    "tests": Path("tests/tests_auto.json"),
    "output": Path("metrics/metrics_auto.json")
}

HYBRID_PATHS = {
    "groups": Path("data/review_groups_hybrid.json"),
    "personas": Path("personas/personas_hybrid.json"),
    "spec": Path("spec/spec_hybrid.md"),
    "tests": Path("tests/tests_hybrid.json"),
    "output": Path("metrics/metrics_hybrid.json")
}

SUMMARY_PATH = Path("metrics/metrics_summary.json")

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_spec_requirements(md_text):
    pattern = r"# Requirement ID: (FR_auto_\d+)"
    return re.findall(pattern, md_text)

def load_dataset_size():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

def normalize_req_id(rid):
    return rid.replace("FR_hybrid_", "FR_auto_")

# ---------------------------------------------------------------------------
# CORE METRICS FUNCTION (REUSABLE)
# ---------------------------------------------------------------------------

def compute_metrics(paths, pipeline_name):
    groups_data   = load_json(paths["groups"])
    personas_data = load_json(paths["personas"])
    tests_data    = load_json(paths["tests"])

    with open(paths["spec"], "r", encoding="utf-8") as f:
        spec_text = f.read()

    groups   = groups_data["groups"]
    personas = personas_data["personas"]
    tests    = tests_data["tests"]

    req_ids = load_spec_requirements(spec_text)
    req_id_set = set(req_ids)

    dataset_size = load_dataset_size()
    persona_count = len(personas)
    requirements_count = len(req_ids)
    tests_count = len(tests)

    # TRACEABILITY
    persona_links = sum(1 for p in personas if p.get("derived_from_group"))

    req_links = sum(
        1 for p in personas
        if p.get("name") and p["name"] in spec_text
    )

    test_links = len(tests)
    traceability_links = persona_links + req_links + test_links

    # REVIEW COVERAGE (handle both formats safely)
    total_reviews_in_groups = sum(
        len(g.get("review_ids", g.get("reviews", [])))
        for g in groups
    )

    review_coverage = (
        total_reviews_in_groups / dataset_size
        if dataset_size else 0
    )

    # TRACEABILITY RATIO
    linked_requirements = len(set(
        normalize_req_id(t["requirement_id"])
        for t in tests
        if "requirement_id" in t and
           normalize_req_id(t["requirement_id"]) in req_id_set
    ))

    traceability_ratio = (
        linked_requirements / requirements_count
        if requirements_count else 0
    )

    testability_rate = traceability_ratio

    # AMBIGUITY
    ambiguous_words = ["may", "might", "could", "etc", "various", "some"]

    requirement_blocks = re.findall(
        r"(# Requirement ID: FR_auto_\d+[\s\S]*?)(?=\n# Requirement ID:|\Z)",
        spec_text
    )

    ambiguous_count = sum(
        1 for block in requirement_blocks
        if any(word in block.lower() for word in ambiguous_words)
    )

    ambiguity_ratio = (
        ambiguous_count / requirements_count
        if requirements_count else 0
    )

    return {
        "pipeline": pipeline_name,
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
# SAVE FUNCTIONS
# ---------------------------------------------------------------------------

def save_metrics(metrics, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[INFO] Saved {path}")

def update_summary(auto_metrics, hybrid_metrics):
    summary = {}

    if SUMMARY_PATH.exists():
        with open(SUMMARY_PATH, "r", encoding="utf-8") as f:
            summary = json.load(f)

    manual = summary.get("manual", {})

    auto_clean = dict(auto_metrics)
    auto_clean.pop("pipeline", None)

    hybrid_clean = dict(hybrid_metrics)
    hybrid_clean.pop("pipeline", None)

    final = {
        "manual": manual,
        "automated": auto_clean,
        "hybrid": hybrid_clean
    }

    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print(f"[INFO] Updated {SUMMARY_PATH}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n--- COMPUTING AUTOMATED METRICS ---")
    auto_metrics = compute_metrics(AUTO_PATHS, "automated")
    save_metrics(auto_metrics, AUTO_PATHS["output"])

    print("\n--- COMPUTING HYBRID METRICS ---")
    hybrid_metrics = compute_metrics(HYBRID_PATHS, "hybrid")
    save_metrics(hybrid_metrics, HYBRID_PATHS["output"])

    print("\n--- UPDATING SUMMARY ---")
    update_summary(auto_metrics, hybrid_metrics)

    print("\n[DONE] All metrics computed.")

if __name__ == "__main__":
    main()