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
# Ordered strictly with verified production models first (gemini-2.5-flash, gemini-3-flash-preview, gemini-flash-latest)
MASTER_MODELS_WATERFALL: List[str] = [
    # --- Tier 1: Verified High-Speed Production Gemini Models ---
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-3.5-flash",
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.1-pro-preview",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-flash-lite",
    "gemini-2.5-pro",
    "gemini-pro-latest",
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
]

# Master prioritized list of fast Groq models (120B reasoning, Qwen 27B, 20B, 7B)
GROQ_MODELS_WATERFALL: List[str] = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "allam-2-7b",
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


DIAGNOSTIC_LOGS: List[Dict[str, Any]] = []

def record_diagnostic(
    provider: str,
    model: str,
    status: Optional[int],
    latency_ms: float,
    response_length: int = 0,
    json_parse_error: Optional[str] = None,
    pydantic_failure: Optional[str] = None,
    actual_cause: str = "success"
) -> Dict[str, Any]:
    entry = {
        "provider": provider,
        "model": model,
        "http_status": status,
        "latency_ms": round(latency_ms, 1),
        "response_length": response_length,
        "json_parse_error": json_parse_error,
        "pydantic_failure": pydantic_failure,
        "actual_cause": actual_cause,
        "timestamp": time.time(),
    }
    DIAGNOSTIC_LOGS.append(entry)
    # Keep last 100 entries
    if len(DIAGNOSTIC_LOGS) > 100:
        DIAGNOSTIC_LOGS.pop(0)
    logger.info(
        f"[LLM-DIAGNOSTIC] Provider: {provider} | Model: {model} | HTTP: {status} | "
        f"Latency: {latency_ms:.0f}ms | Length: {response_length} | Cause: {actual_cause}"
    )
    return entry


def get_recent_diagnostic_logs() -> List[Dict[str, Any]]:
    return list(DIAGNOSTIC_LOGS)


def clear_diagnostic_logs() -> None:
    DIAGNOSTIC_LOGS.clear()


async def sleep_between_calls(delay: Optional[float] = None) -> None:
    """Configurable delay between sequential LLM calls to prevent rate-limit bursts."""
    sec = delay if delay is not None else float(os.getenv("NEXUS_LLM_DELAY_SEC", "1.5"))
    if sec > 0:
        await asyncio.sleep(sec)


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
    timeout_per_model: float = 15.0,
    tag: str = "GROQ-AGENT"
) -> Optional[Tuple[str, str]]:
    """
    Executes a prompt against the Groq API (Llama 3.3 70B, Qwen 27B, GPT-OSS 120B/20B).
    Fast failover across all Groq models with exponential backoff on 429.
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

    timeout_config = httpx.Timeout(timeout_per_model, connect=3.0)

    for idx, model in enumerate(GROQ_MODELS_WATERFALL):
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        if response_mime_type == "application/json":
            payload["response_format"] = {"type": "json_object"}

        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                resp = await client.post(GROQ_API_BASE_URL, headers=headers, json=payload)
                lat_ms = (time.monotonic() - t0) * 1000.0
                status = resp.status_code

                if status == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content.strip():
                            record_diagnostic("groq", model, status, lat_ms, len(content), actual_cause="success")
                            logger.info(f"[{tag}] GROQ LLM SUCCESS | Model: '{model}' (candidate {idx+1}/{len(GROQ_MODELS_WATERFALL)})")
                            return content, f"groq/{model}"
                    record_diagnostic("groq", model, status, lat_ms, 0, actual_cause="empty_choices")

                elif status in (400, 422):
                    logger.info(f"[{tag}] Groq Model '{model}' returned {status}. Retrying in standard text mode...")
                    alt_payload = {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature
                    }
                    t_alt = time.monotonic()
                    async with httpx.AsyncClient(timeout=timeout_config) as client2:
                        alt_resp = await client2.post(GROQ_API_BASE_URL, headers=headers, json=alt_payload)
                        lat_alt = (time.monotonic() - t_alt) * 1000.0
                        if alt_resp.status_code == 200:
                            alt_choices = alt_resp.json().get("choices", [])
                            if alt_choices:
                                alt_content = alt_choices[0].get("message", {}).get("content", "")
                                if alt_content.strip():
                                    record_diagnostic("groq", model, 200, lat_alt, len(alt_content), actual_cause="success (text-mode)")
                                    logger.info(f"[{tag}] GROQ LLM SUCCESS | Model: '{model}' (standard text mode)")
                                    return alt_content, f"groq/{model}"
                    record_diagnostic("groq", model, status, lat_ms, len(resp.text), actual_cause=f"client_error ({status})")
                    continue

                elif status == 429:
                    record_diagnostic("groq", model, 429, lat_ms, len(resp.text), actual_cause="rate_limit (429)")
                    # Exponential backoff retry on 429
                    retry_succeeded = False
                    for b_attempt in range(1, 3):
                        backoff = min(6.0, 1.5 ** b_attempt)
                        logger.info(f"[{tag}] Groq Model '{model}' rate-limited (429). Backing off {backoff:.1f}s (retry {b_attempt}/2)...")
                        await asyncio.sleep(backoff)
                        try:
                            t_retry = time.monotonic()
                            async with httpx.AsyncClient(timeout=timeout_config) as r_client:
                                r_resp = await r_client.post(GROQ_API_BASE_URL, headers=headers, json=payload)
                                r_lat = (time.monotonic() - t_retry) * 1000.0
                                if r_resp.status_code == 200:
                                    r_choices = r_resp.json().get("choices", [])
                                    if r_choices:
                                        r_content = r_choices[0].get("message", {}).get("content", "")
                                        if r_content.strip():
                                            record_diagnostic("groq", model, 200, r_lat, len(r_content), actual_cause="success_after_backoff")
                                            return r_content, f"groq/{model}"
                        except Exception:
                            pass
                    continue

                else:
                    record_diagnostic("groq", model, status, lat_ms, len(resp.text), actual_cause=f"http_{status}")
                    logger.warning(f"[{tag}] Groq Model '{model}' returned status {status}: {resp.text[:120]}. Trying next...")
                    continue

        except httpx.ReadTimeout:
            lat_ms = (time.monotonic() - t0) * 1000.0
            record_diagnostic("groq", model, None, lat_ms, 0, actual_cause=f"timeout after {timeout_per_model}s")
            logger.info(f"[{tag}] Groq Model '{model}' timed out after {timeout_per_model}s. Trying next...")
            continue
        except Exception as exc:
            lat_ms = (time.monotonic() - t0) * 1000.0
            record_diagnostic("groq", model, None, lat_ms, 0, actual_cause=f"exception: {type(exc).__name__}")
            logger.warning(f"[{tag}] Groq Model '{model}' exception: {type(exc).__name__}: {exc}. Trying next...")
            continue

    return None


async def call_gemini_generate_content(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    system_instruction: Optional[str] = None,
    temperature: float = 0.2,
    response_mime_type: str = "application/json",
    timeout_per_model: float = 15.0,
    max_tokens: Optional[int] = None,
    tag: str = "AGENT"
) -> Optional[Tuple[str, str]]:
    """
    Executes a prompt against the Google Gemini API with aggressive model waterfall.
    Includes exponential backoff on 429 and fast failover to Groq.
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

        timeout_config = httpx.Timeout(timeout_per_model, connect=3.0)
        consecutive_network_errors = 0
        consecutive_429s = 0

        for idx, model in enumerate(candidate_models):
            url = f"{GEMINI_API_BASE_URL}/{model}:generateContent?key={key}"
            t0 = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=timeout_config) as client:
                    resp = await client.post(url, json=payload)
                    lat_ms = (time.monotonic() - t0) * 1000.0
                    status = resp.status_code

                    if status == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_text = parts[0].get("text", "")
                                if raw_text.strip():
                                    record_diagnostic("gemini", model, 200, lat_ms, len(raw_text), actual_cause="success")
                                    logger.info(
                                        f"[{tag}] GEMINI LLM SUCCESS | Model: '{model}' (candidate {idx+1}/{len(candidate_models)})"
                                    )
                                    return raw_text, model

                        record_diagnostic("gemini", model, 200, lat_ms, 0, actual_cause="empty_parts")
                        logger.warning(f"[{tag}] Model '{model}' returned empty candidate parts. Trying next...")
                        continue

                    elif status == 429:
                        consecutive_429s += 1
                        record_diagnostic("gemini", model, 429, lat_ms, len(resp.text), actual_cause="rate_limit (429)")
                        logger.info(f"[{tag}] Model '{model}' quota/rate-limited (429).")

                        # Try 1 backoff attempt on 429 before waterfalling
                        backoff = 2.0
                        await asyncio.sleep(backoff)
                        try:
                            t_retry = time.monotonic()
                            retry_resp = await client.post(url, json=payload)
                            r_lat = (time.monotonic() - t_retry) * 1000.0
                            if retry_resp.status_code == 200:
                                r_cand = retry_resp.json().get("candidates", [])
                                if r_cand:
                                    r_parts = r_cand[0].get("content", {}).get("parts", [])
                                    if r_parts and r_parts[0].get("text", "").strip():
                                        record_diagnostic("gemini", model, 200, r_lat, len(r_parts[0]["text"]), actual_cause="success_after_backoff")
                                        return r_parts[0]["text"], model
                        except Exception:
                            pass

                        if consecutive_429s >= 2 and get_groq_api_key():
                            logger.info(f"[{tag}] Gemini free-tier quota exhausted. Fast-failing immediately to Groq...")
                            break
                        continue

                    elif status == 404:
                        record_diagnostic("gemini", model, 404, lat_ms, 0, actual_cause="not_found (404)")
                        logger.debug(f"[{tag}] Model '{model}' not found (404). Trying next...")
                        continue

                    elif status in (500, 502, 503, 504):
                        record_diagnostic("gemini", model, status, lat_ms, len(resp.text), actual_cause=f"server_error ({status})")
                        logger.info(f"[{tag}] Model '{model}' unavailable/server error ({status}). Trying next...")
                        continue

                    elif status in (400, 401, 403):
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
                                            record_diagnostic("gemini", model, 200, (time.monotonic() - t0)*1000.0, len(alt_text), actual_cause="success (text-mode)")
                                            logger.info(f"[{tag}] GEMINI LLM SUCCESS | Model: '{model}' (standard text mode)")
                                            return alt_text, model
                        record_diagnostic("gemini", model, status, lat_ms, len(resp.text), actual_cause=f"client_error ({status})")
                        logger.warning(f"[{tag}] Model '{model}' returned HTTP {status}. Trying next...")
                        continue

                    else:
                        record_diagnostic("gemini", model, status, lat_ms, len(resp.text), actual_cause=f"http_{status}")
                        logger.warning(f"[{tag}] Model '{model}' returned status {status}. Trying next...")
                        continue

            except httpx.ReadTimeout:
                lat_ms = (time.monotonic() - t0) * 1000.0
                record_diagnostic("gemini", model, None, lat_ms, 0, actual_cause=f"timeout after {timeout_per_model}s")
                logger.info(f"[{tag}] Model '{model}' timed out after {timeout_per_model}s. Trying next...")
                consecutive_network_errors += 1
                if consecutive_network_errors >= 2:
                    logger.info(f"[{tag}] Multiple Gemini timeouts. Fast-failing waterfall...")
                    break
                continue
            except Exception as exc:
                lat_ms = (time.monotonic() - t0) * 1000.0
                record_diagnostic("gemini", model, None, lat_ms, 0, actual_cause=f"exception: {type(exc).__name__}")
                logger.warning(f"[{tag}] Model '{model}' exception: {exc}. Trying next...")
                consecutive_network_errors += 1
                if consecutive_network_errors >= 2:
                    logger.info(f"[{tag}] Multiple Gemini connection drops. Fast-failing waterfall...")
                    break
                continue

    # --- Secondary Provider: Groq (Llama 3.3 70B, Qwen 27B, GPT-OSS 120B) Failover ---
    groq_key = get_groq_api_key()
    if groq_key:
        logger.info(f"[{tag}] Gemini exhausted or rate-limited. Activating Groq failover ({len(GROQ_MODELS_WATERFALL)} models)...")
        groq_result = await call_groq_generate_content(
            prompt=prompt,
            api_key=groq_key,
            system_instruction=system_instruction,
            temperature=temperature,
            response_mime_type=response_mime_type,
            timeout_per_model=timeout_per_model,
            tag=tag
        )
        if groq_result:
            return groq_result

    logger.warning(f"[{tag}] ALL Gemini ({len(candidate_models)}) and Groq models failed or rate-limited. Activating grounded safety fallback.")
    return None


