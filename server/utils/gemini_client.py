"""
Universal Resilient Gemini Multi-Model Client for NEXUS-ISB7.

Prioritizes ALL valid Google AI Studio Gemini & Gemma models from best to last.
Provides fast failover when models encounter 429 (rate-limit / quota exhausted),
404 (deprecated), 503 (high demand), or timeouts.
Heuristic/deterministic fallbacks in agents are only used as the absolute last resort
after every single candidate model has been tried.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

# Base endpoints
GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GROQ_API_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# Master prioritized list of all text generation models on Google AI Studio
# Ordered strictly from BEST (premier reasoning, modern capabilities) to LAST (lite, older, specialized).
MASTER_MODELS_WATERFALL: List[str] = [
    # --- Tier 1: Premier Gemini 3 Flagships (Top reasoning, quality & comprehension) ---
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",

    # --- Tier 2: Current Production Aliases & Core Workhorses ---
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-2.5-computer-use-preview-10-2025",

    # --- Tier 3: High-Capability Specialized Engines ---
    "gemini-robotics-er-2-preview",
    "gemma-4-26b-a4b-it",
    "gemini-omni-flash-preview",
    "gemini-omni-1.1-flash",
    "gemma-4-31b-it",

    # --- Tier 4: Gemini 2.0 Series ---
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",

    # --- Tier 5: Gemini 1.5 Series ---
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
]

# Master prioritized list of fast, free Groq models (120B reasoning, Qwen 27B, 20B, 7B, Llama 3)
GROQ_MODELS_WATERFALL: List[str] = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "allam-2-7b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
]

# Cache for dynamically discovered models from ListModels
_DISCOVERED_MODELS_CACHE: List[str] = []
_LAST_DISCOVERY_TIME: float = 0.0
_DISCOVERY_CACHE_TTL: float = 600.0  # 10 minutes


def get_gemini_api_key() -> str:
    """
    Retrieves the GEMINI_API_KEY from environment or directly from server/.env.
    """
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key

    # If running inside a pytest test that deliberately unset GEMINI_API_KEY, respect it
    if "PYTEST_CURRENT_TEST" in os.environ:
        return ""

    # Attempt locating server/.env
    search_paths = [
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / "server" / ".env",
        Path.cwd() / ".env"
    ]

    for p in search_paths:
        if p.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=p, override=False)
                key = os.getenv("GEMINI_API_KEY", "").strip()
                if key:
                    return key
            except Exception:
                pass
            # Manual fallback reading
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == "GEMINI_API_KEY":
                                key = v.strip().strip("'\"")
                                if key:
                                    os.environ["GEMINI_API_KEY"] = key
                                    return key
            except Exception:
                pass

    return ""


def get_groq_api_key() -> str:
    """
    Retrieves the GROQ_API_KEY from environment or directly from server/.env.
    """
    key = os.getenv("GROQ_API_KEY", "").strip()
    if key:
        return key

    if "PYTEST_CURRENT_TEST" in os.environ:
        return ""

    search_paths = [
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / "server" / ".env",
        Path.cwd() / ".env"
    ]

    for p in search_paths:
        if p.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(dotenv_path=p, override=False)
                key = os.getenv("GROQ_API_KEY", "").strip()
                if key:
                    return key
            except Exception:
                pass
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == "GROQ_API_KEY":
                                key = v.strip().strip("'\"")
                                if key:
                                    os.environ["GROQ_API_KEY"] = key
                                    return key
            except Exception:
                pass

    return ""


async def get_all_viable_models(api_key: Optional[str] = None) -> List[str]:
    """
    Returns the comprehensive list of all candidate models ordered from best to last.
    Dynamically blends models discovered via ListModels with the master waterfall.
    """
    global _DISCOVERED_MODELS_CACHE, _LAST_DISCOVERY_TIME

    now = time.monotonic()
    if _DISCOVERED_MODELS_CACHE and (now - _LAST_DISCOVERY_TIME) < _DISCOVERY_CACHE_TTL:
        return list(_DISCOVERED_MODELS_CACHE)

    key = (api_key or get_gemini_api_key()).strip()
    discovered: List[str] = []

    if key:
        try:
            url = f"{GEMINI_API_BASE_URL}?key={key}"
            async with httpx.AsyncClient(timeout=httpx.Timeout(6.0, connect=3.0)) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    models_raw = data.get("models", [])
                    for m in models_raw:
                        m_name = m.get("name", "").replace("models/", "").strip()
                        methods = m.get("supportedGenerationMethods", [])
                        if "generateContent" in methods and m_name:
                            # Filter out non-text models and internal preview engines that reject standard chat generation
                            non_viable = (
                                "tts", "transcribe", "lyria", "image", "clip", "banana",
                                "antigravity-preview", "deep-research", "customtools"
                            )
                            if not any(k in m_name.lower() for k in non_viable):
                                discovered.append(m_name)
        except Exception as exc:
            logger.debug(f"Dynamic ListModels query skipped: {exc}")

    # Build ordered list:
    ordered_list: List[str] = []
    seen = set()

    for m in MASTER_MODELS_WATERFALL:
        if m not in seen:
            ordered_list.append(m)
            seen.add(m)

    for m in discovered:
        if m not in seen:
            ordered_list.append(m)
            seen.add(m)

    _DISCOVERED_MODELS_CACHE = ordered_list
    _LAST_DISCOVERY_TIME = now
    return list(ordered_list)


def clean_llm_json_text(text: str) -> str:
    """Extracts clean JSON from LLM output, handling markdown fences and prose."""
    raw = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    first_brace = raw.find("{")
    last_brace = raw.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return raw[first_brace:last_brace+1].strip()
    return raw


async def call_groq_generate_content(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    response_mime_type: str = "application/json",
    timeout_per_model: float = 7.0,
    tag: str = "GROQ-AGENT"
) -> Optional[Tuple[str, str]]:
    """
    Executes a prompt against the Groq API (Llama 3.3 70B, Llama 3.1 8B, Mixtral).
    Fast failover across all Groq models when Gemini is rate-limited or unavailable.
    """
    key = (api_key or get_groq_api_key()).strip()
    if not key:
        return None

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    timeout_config = httpx.Timeout(timeout_per_model, connect=2.5)

    for idx, model in enumerate(GROQ_MODELS_WATERFALL):
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if response_mime_type == "application/json":
            payload["response_format"] = {"type": "json_object"}

        try:
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                resp = await client.post(GROQ_API_BASE_URL, headers=headers, json=payload)
                status = resp.status_code

                if status == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content.strip():
                            logger.info(f"[{tag}] GROQ LLM SUCCESS | Model: '{model}' (candidate {idx+1}/{len(GROQ_MODELS_WATERFALL)})")
                            return content, f"groq/{model}"

                elif status == 429:
                    logger.info(f"[{tag}] Groq Model '{model}' rate-limited (429). Trying next Groq model...")
                    continue
                else:
                    logger.warning(f"[{tag}] Groq Model '{model}' returned status {status}. Trying next...")
                    continue

        except Exception as exc:
            logger.warning(f"[{tag}] Groq Model '{model}' exception: {exc}. Trying next...")
            continue

    return None


async def call_gemini_generate_content(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    response_mime_type: str = "application/json",
    timeout_per_model: float = 6.5,
    max_tokens: Optional[int] = None,
    tag: str = "AGENT"
) -> Optional[Tuple[str, str]]:
    """
    Executes a prompt against the Google Gemini API with aggressive model waterfall.
    If all Gemini models are exhausted / rate-limited (429), automatically fails over
    to Groq (Llama-3.3-70B, Llama-3.1-8B) before falling back to heuristics.

    Returns:
        (raw_response_text, successful_model_name) or None if all LLMs failed.
    """
    key = (api_key or get_gemini_api_key()).strip()
    candidate_models = await get_all_viable_models(key) if key else []

    if key and candidate_models:
        logger.info(f"[{tag}] Attempting LLM generation across {len(candidate_models)} Gemini models (best-to-last)...")

        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature
            }
        }

        if response_mime_type:
            payload["generationConfig"]["responseMimeType"] = response_mime_type
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        timeout_config = httpx.Timeout(timeout_per_model, connect=2.5)
        consecutive_network_errors = 0
        consecutive_429s = 0

        for idx, model in enumerate(candidate_models):
            url = f"{GEMINI_API_BASE_URL}/{model}:generateContent?key={key}"
            try:
                async with httpx.AsyncClient(timeout=timeout_config) as client:
                    resp = await client.post(url, json=payload)
                    status = resp.status_code

                    if status == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_text = parts[0].get("text", "")
                                if raw_text.strip():
                                    logger.info(
                                        f"[{tag}] GEMINI LLM SUCCESS | Model: '{model}' (candidate {idx+1}/{len(candidate_models)})"
                                    )
                                    return raw_text, model

                        logger.warning(f"[{tag}] Model '{model}' returned empty candidate parts. Trying next...")
                        continue

                    elif status == 429:
                        consecutive_429s += 1
                        logger.info(f"[{tag}] Model '{model}' quota/rate-limited (429).")
                        if consecutive_429s >= 3 and get_groq_api_key():
                            logger.info(f"[{tag}] Gemini free-tier quota exhausted. Fast-failing immediately to Groq...")
                            break
                        continue

                    elif status == 404:
                        logger.debug(f"[{tag}] Model '{model}' not found (404). Trying next...")
                        continue

                    elif status in (500, 502, 503, 504):
                        logger.info(f"[{tag}] Model '{model}' unavailable/server error ({status}). Trying next...")
                        continue

                    elif status in (400, 401, 403):
                        # Check if error is due to responseMimeType: application/json on models like gemma
                        err_text = resp.text.lower()
                        if "responsemimetype" in err_text or "mime" in err_text or "json" in err_text:
                            logger.info(f"[{tag}] Model '{model}' does not support responseMimeType JSON. Retrying without it...")
                            alt_payload = {
                                "contents": [{"parts": [{"text": prompt + "\n\nCRITICAL: Return ONLY valid JSON."}]}],
                                "generationConfig": {"temperature": temperature}
                            }
                            alt_resp = await client.post(url, json=alt_payload)
                            if alt_resp.status_code == 200:
                                alt_cand = alt_resp.json().get("candidates", [])
                                if alt_cand:
                                    alt_parts = alt_cand[0].get("content", {}).get("parts", [])
                                    if alt_parts:
                                        alt_text = alt_parts[0].get("text", "")
                                        if alt_text.strip():
                                            logger.info(f"[{tag}] GEMINI LLM SUCCESS | Model: '{model}' (standard text mode)")
                                            return alt_text, model
                        logger.warning(f"[{tag}] Model '{model}' returned HTTP {status}. Trying next...")
                        continue

                    else:
                        logger.warning(f"[{tag}] Model '{model}' returned status {status}. Trying next...")
                        continue

            except httpx.ReadTimeout:
                logger.info(f"[{tag}] Model '{model}' timed out after {timeout_per_model}s. Trying next...")
                consecutive_network_errors += 1
                if consecutive_network_errors >= 2 and get_groq_api_key():
                    logger.info(f"[{tag}] Multiple Gemini timeouts. Fast-failing directly to Groq...")
                    break
                continue
            except Exception as exc:
                logger.warning(f"[{tag}] Model '{model}' exception: {exc}. Trying next...")
                consecutive_network_errors += 1
                if consecutive_network_errors >= 2 and get_groq_api_key():
                    logger.info(f"[{tag}] Multiple Gemini connection drops. Fast-failing directly to Groq...")
                    break
                continue

    # --- Secondary Provider: Groq (Llama 3.3 70B, Llama 3.1 8B, Mixtral) Failover ---
    groq_key = get_groq_api_key()
    if groq_key:
        logger.info(f"[{tag}] Gemini exhausted or rate-limited. Activating Groq failover ({len(GROQ_MODELS_WATERFALL)} models)...")
        groq_result = await call_groq_generate_content(
            prompt=prompt,
            api_key=groq_key,
            system_instruction=system_instruction,
            temperature=temperature,
            response_mime_type=response_mime_type,
            tag=tag
        )
        if groq_result:
            return groq_result

    logger.warning(f"[{tag}] ALL Gemini ({len(candidate_models)}) and Groq models failed or rate-limited. Activating grounded safety fallback.")
    return None

