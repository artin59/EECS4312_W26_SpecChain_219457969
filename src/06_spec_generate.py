"""generates structured specs from personas"""
"""
Step 4.3: Automatically Generate System Requirements from Personas
Input:  personas/personas_auto.json
Output: spec/spec_auto.md
"""

import json
import os
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
GROQ_MODEL    = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_URL      = "https://api.groq.com/openai/v1/chat/completions"

PERSONAS_PATH = Path("personas/personas_auto.json")
OUTPUT_PATH   = Path("spec/spec_auto.md")

REQUIREMENTS_PER_PERSONA = 3

# ---------------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------------

SPEC_SYSTEM = (
    "You are a requirements engineering expert. "
    "Generate high-quality functional system requirements from user personas. "
    "Requirements must be clear, testable, and structured."
)

SPEC_USER_TEMPLATE = """\
You are given a user persona for the Calm meditation and sleep app.

PERSONA:
Name: {name}
Description: {description}
Goals: {goals}
Pain Points: {pain_points}
Context: {context}
Constraints: {constraints}
Derived From Group: {group_id}

Generate EXACTLY {num_reqs} functional requirements.

Each requirement MUST follow this EXACT format:

# Requirement ID: FR_auto_<number>
- Description: [The system shall ...]
- Source Persona: [{name}]
- Traceability: [Derived from review group {group_id}]
- Acceptance Criteria: [Given ..., When ..., Then ...]

IMPORTANT:
- Use ONLY this format
- Do NOT include explanations
- Do NOT use markdown code blocks
- Make requirements specific and testable
"""

# ---------------------------------------------------------------------------
# GROQ CALL
# ---------------------------------------------------------------------------

def call_groq(messages, temperature=0.2, max_tokens=2048):
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
# LOAD PERSONAS
# ---------------------------------------------------------------------------

def load_personas():
    with open(PERSONAS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["personas"]


# ---------------------------------------------------------------------------
# GENERATE REQUIREMENTS
# ---------------------------------------------------------------------------

def generate_requirements(personas):
    all_requirements = []
    req_counter = 1

    for persona in personas:
        print(f"[INFO] Generating requirements for {persona['name']}...")

        user_msg = SPEC_USER_TEMPLATE.format(
            name=persona["name"],
            description=persona["description"],
            goals=", ".join(persona["goals"]),
            pain_points=", ".join(persona["pain_points"]),
            context=", ".join(persona["context"]),
            constraints=", ".join(persona["constraints"]),
            group_id=persona["derived_from_group"],
            num_reqs=REQUIREMENTS_PER_PERSONA
        )

        raw = call_groq(
            messages=[
                {"role": "system", "content": SPEC_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )

        # Fix requirement numbering globally
        lines = raw.split("\n")
        updated_lines = []

        for line in lines:
            if line.startswith("# Requirement ID:"):
                line = f"# Requirement ID: FR_auto_{req_counter}"
                req_counter += 1
            updated_lines.append(line)

        all_requirements.append("\n".join(updated_lines))

        time.sleep(2)  # rate limit safety

    return "\n\n".join(all_requirements)


# ---------------------------------------------------------------------------
# SAVE OUTPUT
# ---------------------------------------------------------------------------

def save_spec(markdown_text):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    print(f"[INFO] Saved {OUTPUT_PATH}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        raise EnvironmentError("Set your GROQ_API_KEY first.")

    personas = load_personas()
    spec_text = generate_requirements(personas)

    print("\n[SUMMARY] Generated specification preview:\n")
    print(spec_text[:500])  # preview

    save_spec(spec_text)
    print("\n[DONE] Step 4.3 complete.")


if __name__ == "__main__":
    main()