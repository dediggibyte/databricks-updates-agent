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
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from .fetch import detect_status, fetch_doc, pick_primary_doc
from .models import Capability, OnePager, ReleaseNote, Step

_TOOL_NAME = "emit_one_pager"

_SYSTEM = """You are a Databricks platform analyst who writes crisp executive \
one-pagers about product release notes. For each release note you receive, \
produce a single one-pager that explains the update BOTH technically (what \
changed, how it works, prerequisites, limitations) AND from a business \
perspective (why it matters, who benefits, use cases).

You are given the release note AND, when available, the full text of the \
underlying technical documentation it links to. USE THE TECHNICAL DOC as your \
primary source — it contains the real detail (how it works, exact \
prerequisites, limitations, configuration, steps). The one-pager must convey \
what actually changed and its impact, not just restate the one-line blurb.

Rules:
- Be specific and factual to the provided material. Never invent version \
numbers, dates, or features not present in the note or doc.
- "what_it_does" is 3-5 sentences: technical and concrete, drawn from the doc \
(mechanism, scope, what it supports). "why_it_matters" is real business impact \
for a data/platform leader (performance, cost, governance, risk, productivity).
- capabilities: up to 4 concrete features from the doc, each a short title + \
one specific sentence.
- prerequisites, limitations, use_cases: extract the REAL ones from the doc; \
leave a list empty only if the material truly has none.
- steps: up to 5 concrete adoption steps from the doc's guidance.
- "architecture" is an ordered list of 3-6 short stage/component labels showing \
where this fits in the data stack (e.g. "Lakeflow Connect", "Unity Catalog").
- "updated" must be a human date like "Jul 2, 2026".
- "status"/"status_label" reflect the maturity (GA, Public Preview, Beta, \
etc.). Use "changed"/"Update" if unclear.
- "docs_url": set to the technical documentation URL provided (not the release \
note URL) when one is given."""


def _prompt_for(note: ReleaseNote, doc_url: Optional[str], doc_text: str) -> str:
    parts = [
        f"Release note title: {note.title}",
        f"Date: {note.date.isoformat()}",
        f"Cloud: {note.cloud}",
        f"Release note URL: {note.url}",
    ]
    if doc_url:
        parts.append(f"Technical documentation URL: {doc_url}")
    parts.append(f"\nRelease note content:\n{note.body[:4000]}")
    if doc_text:
        parts.append(
            "\n----- UNDERLYING TECHNICAL DOCUMENTATION (primary source) -----\n"
            f"{doc_text}"
        )
    return "\n".join(parts)


def _resolve_provider(cfg: dict, mock: bool) -> str:
    if mock:
        return "heuristic"
    return (cfg.get("llm") or {}).get("provider", "github-models")


def enrich_note(
    note: ReleaseNote,
    cfg: dict,
    model: Optional[str] = None,
    mock: bool = False,
    docs_cache: Optional[Path] = None,
) -> OnePager:
    provider = _resolve_provider(cfg, mock)
    # Resolve the technical reference doc and (optionally) fetch its full text.
    doc_url = pick_primary_doc(note)
    doc_text = ""
    if doc_url and (cfg.get("doc") or {}).get("fetch_underlying", True):
        doc_text = fetch_doc(
            doc_url, docs_cache, (cfg.get("doc") or {}).get("max_chars", 14000)
        )
    try:
        if provider == "anthropic":
            op = _llm_anthropic(note, cfg, model, doc_url, doc_text)
        elif provider == "github-models":
            op = _llm_github_models(note, cfg, model, doc_url, doc_text)
        else:
            op = _heuristic_onepager(note, doc_text)
    except Exception as err:  # noqa: BLE001 - degrade, never fail the run
        if provider != "heuristic":
            print(f"    · {provider} failed ({err}); using heuristic")
        op = _heuristic_onepager(note, doc_text)
    # Fields the model must not freely set — sourced from the record/links.
    op.note_id = note.id
    op.category = note.category
    op.source_url = note.url
    # The docs link points at the technical reference, not the release note.
    op.docs_url = doc_url or op.docs_url or note.url
    return op


# --------------------------------------------------------------------------
# Provider: Anthropic (paid, best quality)
# --------------------------------------------------------------------------
def _llm_anthropic(
    note: ReleaseNote, cfg: dict, model: Optional[str], doc_url: Optional[str], doc_text: str
) -> OnePager:
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
        max_tokens=llm.get("max_tokens", 2600),
        temperature=llm.get("temperature", 0.2),
        system=_SYSTEM,
        tools=[tool],
        tool_choice={"type": "tool", "name": _TOOL_NAME},
        messages=[{"role": "user", "content": _prompt_for(note, doc_url, doc_text)}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == _TOOL_NAME:
            return OnePager.model_validate(block.input)
    raise RuntimeError("no tool_use block returned")


# --------------------------------------------------------------------------
# Provider: GitHub Models (free, uses the built-in GITHUB_TOKEN)
# --------------------------------------------------------------------------
def _llm_github_models(
    note: ReleaseNote, cfg: dict, model: Optional[str], doc_url: Optional[str], doc_text: str
) -> OnePager:
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
        "max_tokens": llm.get("max_tokens", 2600),
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": _prompt_for(note, doc_url, doc_text)},
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
    # The free tier rate-limits aggressively (429); wait and retry a few times
    # before degrading to the heuristic.
    attempts = int(llm.get("retries", 3)) + 1
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310
                body = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 502, 503) or attempt == attempts - 1:
                raise
            wait = int(err.headers.get("Retry-After") or 0) or 15 * (attempt + 1)
            print(f"    · github-models HTTP {err.code}; retrying in {wait}s")
            time.sleep(min(wait, 120))
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
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_LEAD_DATE = re.compile(
    r"^\s*(January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\s+\d{1,2},\s+\d{4}[\s—:-]*"
)


def _clean_text(text: str) -> str:
    """Strip markdown link syntax + emphasis markers and drop a leading date
    stamp (Databricks notes often begin with '**June 8, 2026**')."""
    text = _MD_LINK.sub(r"\1", text)
    text = re.sub(r"[*`]", "", text)          # bold/italic/code markers
    return _LEAD_DATE.sub("", text).strip()


def _cap_title(bullet: str) -> str:
    """A short capability title from a bullet: cleaned, first ~5 words."""
    words = _clean_text(bullet).split()
    title = " ".join(words[:5]).rstrip(".,;:")
    return title or "Capability"


def _unwrap(text: str) -> str:
    """Join soft-wrapped continuation lines so a list item / paragraph is one
    line. Prevents mid-sentence truncation when extracting bullets."""
    out: list[str] = []
    for line in text.splitlines():
        is_new_block = (
            re.match(r"\s*[-*+]\s+", line)
            or re.match(r"\s*\d+\.\s+", line)
            or line.startswith("#")
            or line.strip() == ""
            or line.rstrip().endswith(":")
        )
        if is_new_block or not out or not out[-1].strip():
            out.append(line)
        else:
            out[-1] = out[-1].rstrip() + " " + line.strip()
    return "\n".join(out)


def _truncate_words(text: str, limit: int) -> str:
    """Truncate on a word boundary with an ellipsis — never mid-word."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:—-")
    return cut + "…"


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


def _heuristic_onepager(note: ReleaseNote, doc_text: str = "") -> OnePager:
    """Deterministic one-pager from the note + underlying doc — no LLM, no key.

    Databricks docs follow a predictable shape (overview, then Prerequisites /
    Limitations / use-case sections), so section-aware extraction over the note
    plus the linked technical doc gives a genuinely detailed result.
    """
    # Clean markdown links / leading dates, note first then the deep doc.
    note_body = _clean_text(note.body)
    combined = _unwrap(note_body + ("\n\n" + _clean_text(doc_text) if doc_text else ""))
    status, label = detect_status(note.title + " " + note.body)
    sents = _sentences(combined)
    prereqs = _bullets_under(combined, "prerequisite")
    limits = _bullets_under(combined, "limitation", "known issue", "not supported")
    use_cases = _bullets_under(combined, "use case", "recommended for")
    # Capability bullets = the first list that isn't prereq/limit/use-case.
    excluded = set(prereqs) | set(limits) | set(use_cases)
    highlights = [b for b in _all_bullets(combined) if b not in excluded]

    # Ignore pure "See ..." cross-reference sentences for prose fields.
    def _is_ref(s: str) -> bool:
        return bool(re.match(r"\s*See\b", s)) or s.lower().startswith("for more")

    note_sents = [s for s in _sentences(note_body) if not _is_ref(s)]
    prose = [s for s in sents if not _is_ref(s)]
    tagline = note_sents[0] if note_sents else note.title
    # "What it does" prefers the fuller doc-backed description (3 sentences).
    what = " ".join(prose[:3]) if prose else (note_body[:320] or note.title)
    why = next(
        (s for s in prose if re.search(r"\b(reduc|cost|faster|improv|scale|govern|saving|productiv|latency|performance|minimiz)\w*", s, re.I)),
        "Reduces operational overhead and unlocks new capabilities for data teams on Databricks.",
    )
    # Capabilities come from real bullets; if the note has none, leave the
    # section empty rather than echoing the tagline.
    caps = [Capability(title=_cap_title(b), desc=_truncate_words(b, 130)) for b in highlights[:4]]
    # Light use-case fallback: short noun phrases from the use-case sentence.
    if not use_cases:
        uc_sent = next((s for s in prose if "use case" in s.lower()), "")
        use_cases = [p.strip() for p in re.split(r",|;| and ", uc_sent.split(":")[-1]) if 3 < len(p.strip()) < 40][:4]

    return OnePager(
        product=_truncate_words(note.title, 80),
        tagline=_truncate_words(tagline, 200),
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
        key_takeaway=_truncate_words(tagline, 200),
    )
