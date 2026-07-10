"""Offline repair of already-generated one-pagers.

Fixes two defects in stored ``data/onepagers`` JSON without re-fetching or
calling an LLM:

1. Prose fields (notably ``why_it_matters``) that captured a markdown table —
   Databricks' "what's coming" page is a big ``| Feature | Status | ... |``
   matrix that leaked in as a giant fake sentence.
2. The hollow ``steps = [{"Read the docs", ...}]`` placeholder — replaced with
   an empty steps list plus a plain-language ``plain_summary`` ("In short").

Deterministic and idempotent: run it as many times as you like.
"""

from __future__ import annotations

import re

from .enrich import _clean_text, _looks_like_table, _sentences, _truncate_words
from .models import OnePager

_GENERIC_WHY = (
    "Reduces operational overhead and unlocks new capabilities for data teams "
    "on Databricks."
)
_PLACEHOLDER_STEP_TITLES = {"read the docs", "review the docs", "see the docs"}
_BIZ_RE = re.compile(
    r"\b(reduc|cost|faster|improv|scale|govern|saving|productiv|latency|"
    r"performance|minimiz|simplif|secur|complian|default|remov|requir)\w*",
    re.I,
)
_PROSE_FIELDS = ("product", "tagline", "what_it_does", "key_takeaway", "plain_summary")


def _clean_sentences(*texts: str) -> list[str]:
    out: list[str] = []
    for t in texts:
        out.extend(s for s in _sentences(_clean_text(t or "")) if not _looks_like_table(s))
    return out


def _first_clean(*texts: str) -> str:
    s = _clean_sentences(*texts)
    return s[0] if s else ""


def _business_sentence(*texts: str) -> str:
    for s in _clean_sentences(*texts):
        if _BIZ_RE.search(s):
            return s
    return ""


def repair_onepager(op: OnePager) -> bool:
    """Repair one one-pager in place. Returns True if anything changed."""
    changed = False

    # 1. De-table prose fields.
    for field in _PROSE_FIELDS:
        val = getattr(op, field, "") or ""
        if _looks_like_table(val):
            repl = _first_clean(val, op.what_it_does, op.tagline)
            if not repl:  # last resort: drop the pipes
                repl = _clean_text(val.replace("|", " "))
            setattr(op, field, _truncate_words(repl, 320))
            changed = True

    # 2. why_it_matters: never a table, never empty.
    if _looks_like_table(op.why_it_matters) or not op.why_it_matters.strip():
        op.why_it_matters = _truncate_words(
            _business_sentence(op.what_it_does, op.tagline) or _GENERIC_WHY, 320
        )
        changed = True

    # 3. Capabilities: drop table junk in title/desc.
    for cap in op.capabilities:
        if _looks_like_table(cap.desc) or _looks_like_table(cap.title):
            cap.desc = _truncate_words(_clean_text(cap.desc.replace("|", " ")), 130)
            cap.title = _truncate_words(_clean_text(cap.title.replace("|", " ")), 48)
            changed = True

    # 4. Hollow "read the docs" step -> no steps.
    if op.steps and all(
        s.title.strip().lower() in _PLACEHOLDER_STEP_TITLES for s in op.steps
    ):
        op.steps = []
        changed = True

    # 5. Ensure a plain-language summary exists (the "In short" block): a concise
    #    TL;DR of up to two sentences, shown with the docs link in place of a
    #    hollow "read the docs" step.
    if not op.plain_summary.strip():
        gist = " ".join(_clean_sentences(op.what_it_does, op.tagline)[:2])
        if gist:
            op.plain_summary = _truncate_words(gist, 260)
            changed = True

    return changed
