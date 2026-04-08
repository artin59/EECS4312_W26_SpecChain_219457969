"""runs the full pipeline end-to-end"""
"""
EECS 4312 - SpecChain Project
run_all.py

This script executes the FULL automated pipeline from start to finish.

Pipeline Overview:
------------------
1. Clean raw dataset
   Input:  data/reviews_raw.jsonl
   Output: data/reviews_clean.jsonl

2. Generate review groups + personas (LLM-based)
   Input:  data/reviews_clean.jsonl
   Outputs:
     - data/review_groups_auto.json
     - personas/personas_auto.json

3. Generate system requirements (specification)
   Input:  personas/personas_auto.json
   Output: spec/spec_auto.md

4. Generate validation tests
   Input:  spec/spec_auto.md
   Output: tests/tests_auto.json

5. Compute metrics
   Inputs:
     - data/review_groups_auto.json
     - personas/personas_auto.json
     - spec/spec_auto.md
     - tests/tests_auto.json
   Outputs:
     - metrics/metrics_auto.json
     - metrics/metrics_hybrid.json
     - metrics/metrics_summary.json

Usage:
------
Run from project root:

    python src/run_all.py

IMPORTANT:
----------
- Requires GROQ_API_KEY to be set in environment
- Hybrid/manual steps are NOT executed here (as per assignment)
"""

import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# HELPER: RUN SCRIPT
# ---------------------------------------------------------------------------

def run_script(script_path):
    """
    Runs a Python script and stops execution if it fails.
    """
    print(f"\n[RUNNING] {script_path}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False
    )

    if result.returncode != 0:
        print(f"[ERROR] {script_path} failed. Stopping pipeline.")
        sys.exit(1)

    print(f"[DONE] {script_path}")

# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main():
    print("\n==============================")
    print(" SPECCHAIN AUTOMATED PIPELINE ")
    print("==============================")

    src = Path("src")

    # -------------------------------------------------------
    # STEP 1: CLEAN DATA
    # -------------------------------------------------------
    # Cleans raw reviews:
    #   data/reviews_raw.jsonl → data/reviews_clean.jsonl
    run_script(src / "02_clean.py")

    # -------------------------------------------------------
    # STEP 2: GROUP REVIEWS + GENERATE PERSONAS
    # -------------------------------------------------------
    # Outputs:
    #   data/review_groups_auto.json
    #   personas/personas_auto.json
    run_script(src / "05_personas_auto.py")

    # -------------------------------------------------------
    # STEP 3: GENERATE SPECIFICATIONS
    # -------------------------------------------------------
    # Output:
    #   spec/spec_auto.md
    run_script(src / "06_spec_generate.py")

    # -------------------------------------------------------
    # STEP 4: GENERATE TESTS
    # -------------------------------------------------------
    # Output:
    #   tests/tests_auto.json
    run_script(src / "07_test_generate.py")

    # -------------------------------------------------------
    # STEP 5: COMPUTE METRICS
    # -------------------------------------------------------
    # Outputs:
    #   metrics/metrics_auto.json
    #   metrics/metrics_hybrid.json
    #   metrics/metrics_summary.json
    run_script(src / "08_metrics.py")

    print("\n==============================")
    print(" PIPELINE COMPLETED SUCCESSFULLY ")
    print("==============================")

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()