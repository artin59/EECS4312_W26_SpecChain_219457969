"""
Step 4.1: Automatically Group Reviews Using Groq API (LLM-based grouping)

Model: meta-llama/llama-4-scout-17b-16e-instruct via Groq
Input:  data/reviews_clean.jsonl
Output: data/review_groups_auto.json
"""

import json
import os
import random
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
GROQ_MODEL    = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_URL      = "https://api.groq.com/openai/v1/chat/completions"

PERSONA_OUTPUT_PATH = Path("personas/personas_auto.json")
PERSONAS_PER_GROUP = 1
REVIEWS_PATH  = Path("data/reviews_clean.jsonl")
OUTPUT_PATH   = Path("data/review_groups_auto.json")

NUM_GROUPS                = 5
MIN_REVIEWS_PER_GROUP     = 10
EXAMPLE_REVIEWS_PER_GROUP = 4

# How many reviews to send in the theme-discovery pass (Pass 1).
DISCOVERY_SAMPLE_SIZE = 300

# Batch size for the classification pass (Pass 2).
CLASSIFICATION_BATCH = 20

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# PROMPT TEMPLATES
# ---------------------------------------------------------------------------
PERSONA_SYSTEM = (
    "You are a requirements engineering expert specializing in user persona creation. "
    "You will generate structured personas based on grouped user reviews. "
    "Be realistic, specific, and grounded in the provided evidence."
)

PERSONA_USER_TEMPLATE = """\
You are given a thematic group of user reviews for the Calm meditation and sleep app.

GROUP:
ID: {group_id}
Theme: {theme}
Description: {description}

EXAMPLE REVIEWS:
{reviews_block}

Generate exactly ONE persona that represents this group.

Follow this JSON format EXACTLY (no extra text, no markdown):
{{
  "id": "{persona_id}",
  "name": "<persona name>",
  "description": "<short description>",
  "derived_from_group": "{group_id}",
  "goals": ["...", "..."],
  "pain_points": ["...", "..."],
  "context": ["...", "..."],
  "constraints": ["...", "..."],
  "evidence_reviews": ["<review_id>", "..."]
}}
"""
DISCOVERY_SYSTEM = (
    "You are a requirements engineering expert specialising in mobile application feedback analysis. "
    "Your task is to identify the most common and distinct thematic groups in user reviews of a "
    "meditation and sleep wellness app called Calm. Focus on user needs, pain points, and experiences."
)

DISCOVERY_USER_TEMPLATE = """\
Below is a sample of {n} user reviews (pre-processed: lowercased, stop-words removed, lemmatised) \
from the Calm meditation and sleep app on the Google Play Store.

REVIEWS:
{reviews_block}

Analyse these reviews and identify exactly {num_groups} distinct thematic groups. \
Each group must represent a clearly different user need, complaint, or experience category. \
Do NOT overlap groups.

Respond ONLY with a valid JSON object in this exact format (no extra text, no markdown):
{{
  "themes": [
    {{
      "group_id": "A1",
      "theme": "<short descriptive theme name>",
      "description": "<one sentence describing what this group covers>"
    }}
  ]
}}
"""

CLASSIFICATION_SYSTEM = (
    "You are a requirements engineering expert. "
    "You will classify user reviews into pre-defined thematic groups. "
    "Respond ONLY with valid JSON — no extra text, no markdown code fences."
)

CLASSIFICATION_USER_TEMPLATE = """\
You are classifying user reviews into thematic groups.

GROUPS:
{groups_block}

REVIEWS TO CLASSIFY:
{reviews_block}

RULES:
- Only assign a review to a group if the review is PRIMARILY and CENTRALLY about that theme
- A passing mention is NOT enough — the theme must be the main point of the review
- If a review touches multiple themes, assign NONE
- If unsure, assign NONE
- Expect to assign NONE to at least 30-40% of reviews

Respond ONLY with JSON:
[
  {{"review_id": "<id>", "group_id": "<group_id OR NONE>", "confidence": <0.0-1.0>}}
]
"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_reviews(path: Path) -> list[dict]:
    """Load all reviews from a .jsonl file."""
    reviews = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                reviews.append(json.loads(line))
    print(f"[INFO] Loaded {len(reviews)} reviews from {path}")
    return reviews


def call_groq(messages: list[dict], temperature: float = 0.2, max_tokens: int = 4096, retries: int = 5) -> str:
    """Send a chat completion request to Groq with exponential backoff on 429."""
    import urllib.request
    import urllib.error

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(retries):
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
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (2 ** attempt) + random.uniform(0, 1)  # exponential backoff + jitter
                print(f"[WARN] Rate limited (429). Waiting {wait:.1f}s before retry {attempt + 1}/{retries}...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq API call failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Groq API call failed: {e}")

    raise RuntimeError("Max retries exceeded due to rate limiting.")


def safe_json_parse(text: str):
    """Strip markdown fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[WARN] JSON parse failed: {e}\nRaw text (first 300 chars):\n{text[:300]}")
        return None


# ---------------------------------------------------------------------------
# STEP 1 – DISCOVER THEMES
# ---------------------------------------------------------------------------

def discover_themes(reviews: list[dict]) -> list[dict]:
    """Ask the LLM to identify NUM_GROUPS themes from a sample of reviews."""
    sample = random.sample(reviews, min(DISCOVERY_SAMPLE_SIZE, len(reviews)))

    reviews_block = "\n".join(
        f"[{r['reviewId'][:8]}] (score {r['score']}) {r['content']}"
        for r in sample
        if r.get("content", "").strip()
    )

    user_msg = DISCOVERY_USER_TEMPLATE.format(
        n=len(sample),
        reviews_block=reviews_block,
        num_groups=NUM_GROUPS,
    )

    print(f"[INFO] Pass 1 – Sending {len(sample)} reviews to LLM for theme discovery ...")
    raw = call_groq(
        messages=[
            {"role": "system", "content": DISCOVERY_SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    parsed = safe_json_parse(raw)
    if parsed is None or "themes" not in parsed:
        raise ValueError(f"Theme discovery returned unexpected output:\n{raw}")

    themes = parsed["themes"]
    if len(themes) != NUM_GROUPS:
        print(f"[WARN] Expected {NUM_GROUPS} themes, got {len(themes)}. Proceeding.")

    print(f"[INFO] Discovered {len(themes)} themes:")
    for t in themes:
        print(f"       {t['group_id']}: {t['theme']}")

    return themes


# ---------------------------------------------------------------------------
# STEP 2 – CLASSIFY ALL REVIEWS INTO THEMES
# ---------------------------------------------------------------------------

def classify_reviews(reviews: list[dict], themes: list[dict]) -> dict[str, list[str]]:
    groups_block = "\n".join(
        f"{t['group_id']}: {t['theme']} — {t['description']}" for t in themes
    )

    assignments: dict[str, list[str]] = {t["group_id"]: [] for t in themes}

    valid_reviews = [r for r in reviews if r.get("content", "").strip()]
    total = len(valid_reviews)

    print(f"[INFO] Classifying {total} reviews with strict filtering...")

    for batch_start in range(0, total, CLASSIFICATION_BATCH):
        batch = valid_reviews[batch_start : batch_start + CLASSIFICATION_BATCH]

        reviews_block = json.dumps(
            [{"review_id": r["reviewId"], "content": r["content"]} for r in batch],
            ensure_ascii=False,
            indent=2,
        )

        user_msg = CLASSIFICATION_USER_TEMPLATE.format(
            num_groups=len(themes),
            groups_block=groups_block,
            reviews_block=reviews_block,
        )

        raw = call_groq(
            messages=[
                {"role": "system", "content": CLASSIFICATION_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.0,
        )

        parsed = safe_json_parse(raw)
        if parsed is None:
            print("[WARN] Skipping batch due to parse failure")
            continue

        for item in parsed:
            rid = item.get("review_id")
            gid = item.get("group_id")
            confidence = item.get("confidence", 1.0)

            if gid == "NONE" or confidence < 0.75:  # tune this threshold
                continue

            if gid in assignments:
                assignments[gid].append(rid)
            else:
                # skip unknown instead of forcing
                print(f"[WARN] Invalid group {gid}, skipping {rid[:8]}")

        time.sleep(5)

    return assignments

# ---------------------------------------------------------------------------
# STEP 3 – BUILD FINAL JSON STRUCTURE
# ---------------------------------------------------------------------------

def build_groups_json(themes, assignments, all_reviews):
    review_lookup = {r["reviewId"]: r for r in all_reviews}

    groups = []

    for theme in themes:
        gid  = theme["group_id"]
        rids = assignments.get(gid, [])

        # 🔥 NEW: enforce minimum size
        if len(rids) < MIN_REVIEWS_PER_GROUP:
            print(f"[INFO] Dropping group {gid} (only {len(rids)} reviews)")
            continue

        candidates = [review_lookup[rid] for rid in rids if rid in review_lookup]

        candidates_sorted = sorted(
            candidates,
            key=lambda r: len(r.get("content", "")),
            reverse=True
        )

        examples = [r["content"] for r in candidates_sorted[:EXAMPLE_REVIEWS_PER_GROUP]]

        groups.append({
            "group_id": gid,
            "theme": theme["theme"],
            "description": theme["description"],
            "review_ids": rids,
            "review_count": len(rids),
            "example_reviews": examples,
        })

    print(f"[INFO] Final groups after filtering: {len(groups)}")

    return {"groups": groups}

# ---------------------------------------------------------------------------
# STEP 4 – SAVE OUTPUT
# ---------------------------------------------------------------------------

def save_output(groups_data: dict) -> None:
    """Write review_groups_auto.json."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(groups_data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved {OUTPUT_PATH}")


def generate_personas(groups_data: dict) -> dict:
    """Generate personas from grouped reviews using LLM."""
    personas = []

    for idx, group in enumerate(groups_data["groups"], start=1):
        gid = group["group_id"]
        theme = group["theme"]
        desc = group["description"]

        # Use top example reviews
        example_reviews = group.get("example_reviews", [])
        review_ids = group.get("review_ids", [])[:5]

        reviews_block = "\n".join(
            f"- {r}" for r in example_reviews
        )

        persona_id = f"P{idx}"

        user_msg = PERSONA_USER_TEMPLATE.format(
            group_id=gid,
            theme=theme,
            description=desc,
            reviews_block=reviews_block,
            persona_id=persona_id
        )

        print(f"[INFO] Generating persona for {gid} ({theme}) ...")

        raw = call_groq(
            messages=[
                {"role": "system", "content": PERSONA_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        parsed = safe_json_parse(raw)

        if parsed is None:
            print(f"[WARN] Failed to parse persona for {gid}, skipping.")
            continue

        # Ensure evidence reviews exist
        parsed["evidence_reviews"] = review_ids

        personas.append(parsed)

        time.sleep(5)  # avoid rate limit

    return {"personas": personas}

def save_personas(personas_data: dict):
    PERSONA_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PERSONA_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(personas_data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved {PERSONA_OUTPUT_PATH}")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        raise EnvironmentError(
            "Groq API key not set. "
            "Export it before running:\n  export GROQ_API_KEY='your_key_here'"
        )

    # 1. Load reviews
    reviews = load_reviews(REVIEWS_PATH)

    # 2. Discover themes (Pass 1)
    themes = discover_themes(reviews)

    # 3. Classify all reviews (Pass 2)
    assignments = classify_reviews(reviews, themes)

    # 4. Build output structure
    groups_data = build_groups_json(themes, assignments, reviews)

    # 5. Print summary
    print("\n[SUMMARY] Review group sizes:")
    for g in groups_data["groups"]:
        print(f"  {g['group_id']}: {g['theme']:<45} → {g['review_count']} reviews")

    # 6. Save
    save_output(groups_data)
    print("\n[DONE] Step 4.1 complete.")

    # 7. Generate personas (Step 4.2)
    personas_data = generate_personas(groups_data)

    # 8. Save personas
    save_personas(personas_data)

    print("\n[DONE] complete.")

if __name__ == "__main__":
    main()