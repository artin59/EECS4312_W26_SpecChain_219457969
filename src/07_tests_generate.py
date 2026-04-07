"""
EECS 4312 - SpecChain Project
Step 4.4: Automatically Generate Validation Tests

Input:  spec/spec_auto.md
Output: tests/tests_auto.json
"""

import json
import os
import re
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
GROQ_MODEL    = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_URL      = "https://api.groq.com/openai/v1/chat/completions"

SPEC_PATH   = Path("spec/spec_auto.md")
OUTPUT_PATH = Path("tests/tests_auto.json")

# ---------------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------------

TEST_SYSTEM = (
    "You are a software testing expert. "
    "Generate clear and structured validation test scenarios from system requirements."
)

TEST_USER_TEMPLATE = """\
You are given a system requirement.

REQUIREMENT:
{requirement_text}

Generate EXACTLY ONE validation test scenario.

Follow this JSON format EXACTLY (no extra text):
{{
  "test_id": "{test_id}",
  "requirement_id": "{req_id}",
  "scenario": "<short scenario description>",
  "steps": [
    "...",
    "...",
    "..."
  ],
  "expected_result": "<expected outcome>"
}}

IMPORTANT:
- Steps must be clear and sequential
- Expected result must directly validate the requirement
- Do NOT include markdown or explanations
"""

# ---------------------------------------------------------------------------
# GROQ CALL
# ---------------------------------------------------------------------------

def call_groq(messages, temperature=0.2, max_tokens=1024):
    import urllib.request

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        GROQ_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "User-Agent": "Mozilla/5.0"
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"].strip()

# ---------------------------------------------------------------------------
# PARSE REQUIREMENTS
# ---------------------------------------------------------------------------

def parse_requirements(md_text):
    """
    Extract requirements from markdown.
    Returns list of (requirement_id, full_text)
    """
    pattern = r"(# Requirement ID: (FR_auto_\d+)([\s\S]*?))(?=\n# Requirement ID:|\Z)"
    matches = re.findall(pattern, md_text)

    requirements = []
    for full_block, req_id, _ in matches:
        requirements.append((req_id, full_block.strip()))

    return requirements

# ---------------------------------------------------------------------------
# GENERATE TESTS
# ---------------------------------------------------------------------------

def generate_tests(requirements):
    tests = []
    test_counter = 1

    for req_id, req_text in requirements:
        print(f"[INFO] Generating test for {req_id}...")

        test_id = f"T_auto_{test_counter}"

        user_msg = TEST_USER_TEMPLATE.format(
            requirement_text=req_text,
            test_id=test_id,
            req_id=req_id
        )

        raw = call_groq(
            messages=[
                {"role": "system", "content": TEST_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )

        try:
            parsed = json.loads(raw)
            tests.append(parsed)
            test_counter += 1
        except json.JSONDecodeError:
            print(f"[WARN] Failed to parse test for {req_id}, skipping.")

        time.sleep(2)  # avoid rate limits

    return {"tests": tests}

# ---------------------------------------------------------------------------
# SAVE OUTPUT
# ---------------------------------------------------------------------------

def save_tests(data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Saved {OUTPUT_PATH}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        raise EnvironmentError("Set your GROQ_API_KEY first.")

    # Load spec
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Parse requirements
    requirements = parse_requirements(md_text)
    print(f"[INFO] Found {len(requirements)} requirements")

    # Generate tests
    tests_data = generate_tests(requirements)

    # Save
    save_tests(tests_data)

    print("\n[DONE] Step 4.4 complete.")

if __name__ == "__main__":
    main()