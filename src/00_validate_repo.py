"""checks required files/folders exist"""
"""
EECS 4312 - SpecChain Project
Repository Validation Script

This script verifies that all required folders and files exist.

Usage:
------
python src/00_validate_repo.py
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# REQUIRED STRUCTURE
# ---------------------------------------------------------------------------

REQUIRED_DIRS = [
    "data",
    "personas",
    "spec",
    "tests",
    "metrics",
    "src"
]

REQUIRED_FILES = [
    # DATA
    "data/reviews_raw.jsonl",
    "data/reviews_clean.jsonl",
    "data/review_groups_auto.json",
    "data/review_groups_hybrid.json",

    # PERSONAS
    "personas/personas_auto.json",
    "personas/personas_hybrid.json",
    "personas/personas_manual.json",

    # SPECIFICATIONS
    "spec/spec_auto.md",
    "spec/spec_hybrid.md",
    "spec/spec_manual.md",

    # TESTS
    "tests/tests_auto.json",
    "tests/tests_hybrid.json",
    "tests/tests_manual.json",

    # METRICS
    "metrics/metrics_auto.json",
    "metrics/metrics_hybrid.json",
    "metrics/metrics_summary.json",

    # CORE SCRIPTS
    "src/00_validate_repo.py",
    "src/02_clean.py",
    "src/05_personas_auto.py",
    "src/06_spec_generate.py",
    "src/07_tests_generate.py",
    "src/08_metrics.py",
    "src/run_all.py"
]

# ---------------------------------------------------------------------------
# VALIDATION LOGIC
# ---------------------------------------------------------------------------

def check_directories():
    print("\n[CHECK] Directories:")
    missing = []

    for d in REQUIRED_DIRS:
        if Path(d).exists():
            print(f"  ✔ {d}/ found")
        else:
            print(f"  ✘ {d}/ MISSING")
            missing.append(d)

    return missing


def check_files():
    print("\n[CHECK] Files:")
    missing = []

    for f in REQUIRED_FILES:
        if Path(f).exists():
            print(f"  ✔ {f} found")
        else:
            print(f"  ✘ {f} MISSING")
            missing.append(f)

    return missing


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("Checking repository structure...")

    missing_dirs = check_directories()
    missing_files = check_files()

    print("\n------------------------------")

    if not missing_dirs and not missing_files:
        print("Repository validation complete ✅")
    else:
        print("Repository validation FAILED ❌")
        print(f"Missing directories: {len(missing_dirs)}")
        print(f"Missing files: {len(missing_files)}")

        if missing_dirs:
            print("\nMissing directories:")
            for d in missing_dirs:
                print(f"  - {d}")

        if missing_files:
            print("\nMissing files:")
            for f in missing_files:
                print(f"  - {f}")

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()