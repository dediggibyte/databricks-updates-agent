"""Turn a raw release note into a filled one-pager.

Three interchangeable providers (chosen in ``config.yaml`` → ``llm.provider``):

* ``github-models`` — GitHub's free built-in models, authenticated by the
  ``GITHUB_TOKEN`` that GitHub Actions provides automatically. No API key for
  the user to obtain or pay for. Rate-limited but free.
* ``anthropic``     — Claude via ``ANTHROPIC_API_KEY`` (best quality, paid).
* ``heuristic``     — no network, no key. Deterministic extraction from the
  note text. Always works, and is the automatic fallback if a provider fails.

Whatever the provider, the output is validated against the ``OnePager``
contract, so the template always receives well-formed data.
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Optional

from .fetch import detect_status
from .models import Capability, OnePager, ReleaseNote, Step

_TOOL_NAME = "emit_one_pager"

_SYSTEM = """You are a Databricks platform analyst who writes crisp executive \
one-pagers about product release notes. For each release note you receive, \
produce a single one-pager that explains the update BOTH technically (what \
changed, how it works, prerequisites, limitations) AND from a business \
perspective (why it matters, who benefits, use cases).

Rules:
- Be specific and factual to the release note. Never invent version numbers, \
dates, or features that are not implied by the text.
- "what_it_does" is technical and concrete. "why_it_matters" is business \
impact for a data/platform leader.
- Keep capabilities to at most 4, each a short title + one sentence.
- Prerequisites, limitations, use_cases, steps: only include what the note \
supports; leave a list empty rather than padding it.
- "architecture" is an ordered list of 3-6 short stage/component labels showing \
where this fits in the data stack (e.g. "Unity Catalog", "Serverless SQL").
- "updated" must be a human date like "Jun 16, 2026".
- "status"/"status_label" reflect the maturity (GA, Public Preview, Beta, \
etc.). Use "changed"/"Update" if unclear."""


def _prompt_for(note: ReleaseNote) -> str:
    return (
        f"Release note title: {note.title}\n"
        f"Date: {note.date.isoformat()}\n"
        f"Cloud: {note.cloud}\n"
        f"Source URL: {note.url}\n\n"
        f"Release note content:\n{note.body[:8000]}\n"
    )


def _resolve_provider(cfg: dict, mock: bool) -> str:
    if mock:
        return "heuristic"
    return (cfg.get("llm") or {}).get("provider", "github-models")


def enrich_note(
    note: ReleaseNote,
    cfg: dict,
    model: Optional[str] = None,
    mock: bool = False,
) -> OnePager:
    provider = _resolve_provider(cfg, mock)
    try:
        if provider == "anthropic":
            op = _llm_anthropic(note, cfg, model)
        elif provider == "github-models":
            op = _llm_github_models(note, cfg, model)
        else:
            op = _heuristic_onepager(note)
    except Exception as err:  # noqa: BLE001 - degrade, never fail the run
        if provider != "heuristic":
            print(f"    · {provider} failed ({err}); using heuristic")
        op = _heuristic_onepager(note)
    # Fields the model must not set — always sourced from the record.
    op.note_id = note.id
    op.category = note.category
    op.source_url = note.url
    if not op.docs_url:
        op.docs_url = note.url
    return op


# --------------------------------------------------------------------------
# Provider: Anthropic (paid, best quality)
# --------------------------------------------------------------------------
def _llm_anthropic(note: ReleaseNote, cfg: dict, model: Optional[str]) -> OnePager:
    import anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic()
    llm = cfg["llm"]
    chosen = model or llm.get("anthropic_model", "claude-sonnet-5")
    tool = {
        "name": _TOOL_NAME,
        "description": "Emit the structured one-pager for this release note.",
        "input_schema": OnePager.json_schema_for_llm(),
    }
    resp = client.messages.create(
        model=chosen,
        max_tokens=llm.get("max_tokens", 2000),
        temperature=llm.get("temperature", 0.2),
        system=_SYSTEM,
        tools=[tool],
        tool_choice={"type": "tool", "name": _TOOL_NAME},
        messages=[{"role": "user", "content": _prompt_for(note)}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == _TOOL_NAME:
            return OnePager.model_validate(block.input)
    raise RuntimeError("no tool_use block returned")


# --------------------------------------------------------------------------
# Provider: GitHub Models (free, uses the built-in GITHUB_TOKEN)
# --------------------------------------------------------------------------
def _llm_github_models(note: ReleaseNote, cfg: dict, model: Optional[str]) -> OnePager:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
    llm = cfg["llm"]
    endpoint = llm.get("github_endpoint", "https://models.github.ai/inference/chat/completions")
    chosen = model or llm.get("github_model", "openai/gpt-4o-mini")
    schema = json.dumps(OnePager.json_schema_for_llm())
    system = (
        _SYSTEM
        + "\n\nReturn ONLY a single JSON object (no markdown, no prose) that "
        "conforms to this JSON schema:\n" + schema
    )
    payload = {
        "model": chosen,
        "temperature": llm.get("temperature", 0.2),
        "max_tokens": llm.get("max_tokens", 2000),
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": _prompt_for(note)},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310
        body = json.loads(resp.read().decode("utf-8"))
    content = body["choices"][0]["message"]["content"]
    return OnePager.model_validate(_extract_json(content))


def _extract_json(text: str) -> dict:
    """Parse a JSON object out of a model response, tolerating code fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise


# --------------------------------------------------------------------------
# Provider: heuristic (no key, no network — always available)
# --------------------------------------------------------------------------
def _sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", re.sub(r"[#>*`_\-]{1,}", " ", text)).strip()
    parts = re.split(r"(?<=[.!?])\s+", clean)
    return [p.strip() for p in parts if len(p.strip()) > 20]


def _all_bullets(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        m = re.match(r"\s*[-*+]\s+(.*)", line)
        if m and len(m.group(1).strip()) > 4:
            out.append(re.sub(r"[`*_]", "", m.group(1)).strip())
    return out


def _bullets_under(text: str, *keywords: str) -> list[str]:
    """Bullets that appear in a block introduced by any of ``keywords``."""
    lines = text.splitlines()
    collecting = False
    out: list[str] = []
    for line in lines:
        low = line.lower()
        is_bullet = re.match(r"\s*[-*+]\s+", line)
        if any(k in low for k in keywords) and not is_bullet:
            collecting = True
            continue
        if collecting:
            m = re.match(r"\s*[-*+]\s+(.*)", line)
            if m:
                out.append(re.sub(r"[`*_]", "", m.group(1)).strip())
            elif line.strip() == "":
                continue
            else:
                collecting = False
    return out


def _heuristic_onepager(note: ReleaseNote) -> OnePager:
    """Deterministic one-pager from the note text — no LLM, no key.

    Databricks release notes follow a predictable shape (highlights, then
    Prerequisites / Limitations / use-case sections), so section-aware
    extraction gives a genuinely useful result.
    """
    status, label = detect_status(note.title + " " + note.body)
    sents = _sentences(note.body)
    prereqs = _bullets_under(note.body, "prerequisite")
    limits = _bullets_under(note.body, "limitation", "known issue")
    use_cases = _bullets_under(note.body, "use case", "recommended for")
    # Capability bullets = the first list that isn't prereq/limit/use-case.
    excluded = set(prereqs) | set(limits) | set(use_cases)
    highlights = [b for b in _all_bullets(note.body) if b not in excluded]

    tagline = sents[0] if sents else note.title
    what = " ".join(sents[:2]) if sents else (note.body[:280] or note.title)
    why = next(
        (s for s in sents if re.search(r"\b(reduc|cost|faster|scale|govern|saving|productiv|latency)\w*", s, re.I)),
        "Reduces operational overhead and unlocks new capabilities for data teams on Databricks.",
    )
    caps = [
        Capability(title=" ".join(b.split()[:4]) or "Capability", desc=b[:130])
        for b in (highlights[:4] or [tagline])
    ][:4]
    # Light use-case fallback: short noun phrases from the use-case sentence.
    if not use_cases:
        uc_sent = next((s for s in sents if "use case" in s.lower()), "")
        use_cases = [p.strip() for p in re.split(r",|;| and ", uc_sent.split(":")[-1]) if 3 < len(p.strip()) < 40][:4]

    return OnePager(
        product=note.title[:80],
        tagline=tagline[:200],
        updated=note.date.strftime("%b %-d, %Y"),
        status_label=label,
        status=status,  # type: ignore[arg-type]
        docs_url=note.url,
        source_url=note.url,
        what_it_does=what,
        why_it_matters=why,
        capabilities=caps,
        prerequisites=prereqs[:5],
        use_cases=use_cases[:6],
        limitations=limits[:5],
        architecture=["Databricks Platform", note.category.title()],
        steps=[Step(title="Read the docs", desc="Review the linked release note.")],
        key_takeaway=tagline[:200],
    )
