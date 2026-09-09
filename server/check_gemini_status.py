"""
check_gemini_status.py  —  TEMPORARY DIAGNOSTIC SCRIPT (not part of the app)

Checks, in order:
  1. Loads GEMINI_API_KEY from server/.env (same pattern as web_search_agent.py)
  2. Calls ListModels endpoint — prints HTTP status + available model names (or error body)
  3. Calls generateContent on gemini-2.5-flash  (confirmed working model in web_search_agent.py)
  4. Calls generateContent on gemini-3.6-flash and gemini-3-flash-preview
     (models used in market_analysis_agent.py), plus the full union of all
     models from both agent files for completeness.
  5. Prints a summary table: Model | HTTP Status | Verdict

Run from the workspace root:
    py server/check_gemini_status.py
"""

import os
import sys
import json
import httpx
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — Load GEMINI_API_KEY from server/.env
#           (same dotenv pattern used in web_search_agent.py)
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("STEP 1 — Loading GEMINI_API_KEY from server/.env")
print("=" * 70)

# Resolve server/.env relative to THIS file's location
# This script lives at server/check_gemini_status.py
# parents[0] = server/
server_dir = Path(__file__).resolve().parent
env_path = server_dir / ".env"

print(f"  .env path:  {env_path}")
print(f"  .env found: {'YES' if env_path.exists() else 'NO'}")

if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=False)
        print("  dotenv:     loaded successfully")
    except ImportError:
        # Fallback: manually parse the .env file
        print("  dotenv:     python-dotenv not installed — parsing manually")
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))
else:
    print("  WARNING: server/.env not found — relying on existing environment vars")

api_key = os.getenv("GEMINI_API_KEY", "").strip()
print(f"\n  API Key loaded: {'YES' if api_key else 'NO'}")

if not api_key:
    print("\n  FATAL: GEMINI_API_KEY is empty or missing.")
    print("  Add GEMINI_API_KEY=<your_key> to server/.env and re-run.")
    sys.exit(1)

print()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — ListModels endpoint
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("STEP 2 — ListModels endpoint")
print("  GET https://generativelanguage.googleapis.com/v1beta/models?key=***")
print("=" * 70)

list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(list_url)

    print(f"\n  HTTP Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        models_list = data.get("models", [])
        names = sorted(m.get("name", "?") for m in models_list)
        print(f"\n  Available models ({len(names)} total):")
        for n in names:
            print(f"    {n}")
    else:
        print("\n  ERROR body (raw):")
        print(resp.text)

except Exception as exc:
    print(f"\n  EXCEPTION during ListModels: {exc}")

print()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3–4 — generateContent probe for each model
#
# STEP 3: gemini-2.5-flash (confirmed working in web_search_agent.py)
# STEP 4: gemini-3.6-flash and gemini-3-flash-preview (from market_analysis_agent.py
#         as mentioned in the request), plus the full set of models actually
#         coded in market_analysis_agent.py:
#           gemini-2.5-flash, gemini-flash-latest, gemini-pro-latest,
#           gemini-flash-lite-latest
#         and competitor_analysis_agent.py:
#           gemini-2.5-flash, gemini-flash-latest, gemini-2.5-pro,
#           gemini-flash-lite-latest, gemini-pro-latest
# ─────────────────────────────────────────────────────────────────────────────

# Ordered: gemini-2.5-flash first (STEP 3), then specifically requested models
# (gemini-3.6-flash and gemini-3-flash-preview), then full union from both agent files
MODELS_TO_TEST = [
    # STEP 3 — confirmed working model per web_search_agent.py comment
    "gemini-2.5-flash",
    # STEP 4 — specifically requested models from market_analysis_agent.py (as named in request)
    "gemini-3.6-flash",
    "gemini-3-flash-preview",
    # Full union of all models actually coded in market_analysis_agent.py + competitor_analysis_agent.py
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-pro",
]

GENERATE_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
PAYLOAD = {
    "contents": [{"parts": [{"text": "Reply with exactly: OK"}]}]
}


def _verdict(status: int, body: str) -> str:
    """Derive a human-readable verdict from HTTP status + body text."""
    if status == 200:
        return "WORKING"
    body_lower = body.lower()
    if status == 429:
        return "QUOTA EXCEEDED"
    if status in (401, 403):
        if "api key" in body_lower or "invalid" in body_lower:
            return "INVALID KEY"
        return "PERMISSION DENIED"
    if status == 404:
        return "MODEL NOT FOUND"
    if status == 400:
        return "BAD REQUEST"
    return "OTHER ERROR"


results = []  # [(model, status, verdict)]

for idx, model in enumerate(MODELS_TO_TEST):
    step = 3 if idx == 0 else 4
    print("=" * 70)
    print(f"STEP {step} — generateContent: {model}")
    url = f"{GENERATE_BASE}/{model}:generateContent?key={api_key}"
    print(f"  POST {GENERATE_BASE}/{model}:generateContent?key=***")
    print("=" * 70)

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, json=PAYLOAD)

        status = resp.status_code
        body = resp.text
        verdict = _verdict(status, body)

        print(f"\n  HTTP Status: {status}")
        print(f"\n  Raw response body:")
        # Pretty-print if JSON, raw otherwise
        try:
            parsed = json.loads(body)
            print(json.dumps(parsed, indent=2))
        except Exception:
            print(body)

        results.append((model, status, verdict))

    except Exception as exc:
        print(f"\n  EXCEPTION: {exc}")
        results.append((model, "ERR", "CONNECTION ERROR"))

    print()

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — Summary table
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 70)
print("STEP 5 — SUMMARY TABLE")
print("=" * 70)

col_model   = max(len(m) for m, _, _ in results) + 2
col_status  = 14
col_verdict = 20

header = (
    f"  {'Model':<{col_model}}"
    f"{'HTTP Status':<{col_status}}"
    f"{'Verdict'}"
)
divider = "  " + "-" * (col_model + col_status + col_verdict)

print(header)
print(divider)

for model, status, verdict in results:
    print(
        f"  {model:<{col_model}}"
        f"{str(status):<{col_status}}"
        f"{verdict}"
    )

print()
working = [m for m, s, v in results if v == "WORKING"]
quota   = [m for m, s, v in results if v == "QUOTA EXCEEDED"]
missing = [m for m, s, v in results if v == "MODEL NOT FOUND"]
errors  = [m for m, s, v in results if v not in ("WORKING", "QUOTA EXCEEDED", "MODEL NOT FOUND")]

if working:
    print(f"  [OK] WORKING ({len(working)}): {', '.join(working)}")
if quota:
    print(f"  [!!] QUOTA EXCEEDED ({len(quota)}): {', '.join(quota)}")
if missing:
    print(f"  [XX] MODEL NOT FOUND ({len(missing)}): {', '.join(missing)}")
if errors:
    print(f"  [XX] ERRORS ({len(errors)}): {', '.join(errors)}")

print()
print("Diagnostic complete.")
