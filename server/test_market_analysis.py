"""
test_market_analysis.py — TEMPORARY test script (not part of the app)
Runs market_analysis_agent directly against the manufacturing/IoT
predictive maintenance idea and prints the full synthesis path + output.
"""
import asyncio
import json
import os
import sys
import logging
from pathlib import Path

# ── env loading (same pattern as agents) ──────────────────────────────────────
server_dir = Path(__file__).resolve().parent
env_path = server_dir / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=False)
    except ImportError:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# ── verbose logging so we can see every step ─────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
# quieten httpx noise but keep our agent logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# ── patch sys.path so server.models.validation resolves ──────────────────────
workspace = server_dir.parent  # NEXUS-ISB7/
sys.path.insert(0, str(workspace))

IDEA = (
    "An IoT-based predictive maintenance platform for manufacturing plants "
    "that uses sensor data and machine learning to predict equipment failures "
    "before they happen, reducing unplanned downtime by up to 40%."
)

print("=" * 70)
print("TEST: market_analysis_agent — Manufacturing / IoT Predictive Maintenance")
print("=" * 70)
print(f"\nIdea: {IDEA}\n")


async def main():
    from server.agents.market_analysis_agent import run_market_analysis_agent

    print("[runner] Calling run_market_analysis_agent() ...")
    result = await run_market_analysis_agent(
        idea=IDEA,
        search_results=None,   # no pre-fetched search results — agent uses its own heuristics + Gemini
        domain=None,           # let the agent auto-detect industry
    )

    print("\n" + "=" * 70)
    print("RAW OUTPUT (JSON)")
    print("=" * 70)
    if hasattr(result, "model_dump"):
        output = result.model_dump()
    elif hasattr(result, "dict"):
        output = result.dict()
    else:
        output = result

    print(json.dumps(output, indent=2, default=str))

    # ── decomposition summary ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("DECOMPOSITION / SYNTHESIS SUMMARY")
    print("=" * 70)

    if isinstance(output, dict):
        print(f"\n  Industry classification : {output.get('industry', 'N/A')}")
        print(f"  Sub-industry           : {output.get('sub_industry', 'N/A')}")
        print(f"  Market size (est.)     : {output.get('market_size', 'N/A')}")

        segs = output.get("customer_segments", [])
        print(f"\n  Customer segments ({len(segs)}):")
        for i, seg in enumerate(segs, 1):
            name = seg.get("segment", seg.get("name", "?")) if isinstance(seg, dict) else str(seg)
            print(f"    {i}. {name}")

        trends = output.get("market_trends", output.get("trends", []))
        print(f"\n  Market trends ({len(trends)}):")
        for t in trends[:4]:
            if isinstance(t, dict):
                t = t.get("trend", t.get("description", str(t)))
            print(f"    - {str(t)[:120]}")

        drivers = output.get("growth_drivers", [])
        print(f"\n  Growth drivers ({len(drivers)}):")
        for d in drivers[:3]:
            print(f"    - {str(d)[:120]}")

    print("\nTest complete.")


asyncio.run(main())
