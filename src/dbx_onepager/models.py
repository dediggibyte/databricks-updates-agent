"""Data models for the pipeline.

Two core types:

* ``ReleaseNote`` — a normalized, deduplicated release note scraped from the
  Databricks docs. This is the raw input and the durable record that makes
  historical (past) release notes always available to (re)generate.

* ``OnePager`` — the *content contract* for a rendered one-pager. Every field
  maps to a slot in the design (see ``templates/onepager.html.j2``). Claude
  fills this from a ``ReleaseNote``; the renderer turns it into HTML.

Keeping the contract in one place means the LLM prompt, the JSON schema used
for structured output, and the template all stay in sync.
"""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------------------------------
# Raw release note
# --------------------------------------------------------------------------
def slugify(text: str) -> str:
    """Filesystem/URL-safe slug used for stable IDs and output filenames."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "note"


class RefLink(BaseModel):
    """A reference link found in a release note (its "See ..." / doc links)."""

    text: str
    url: str


class ReleaseNote(BaseModel):
    """A single normalized Databricks release note."""

    id: str = Field(..., description="Stable dedup id: <date>-<slug(title)>")
    title: str
    date: date
    url: str
    cloud: str = "aws"
    category: str = "platform"
    # Raw content as markdown/plain text — what the LLM reads.
    body: str = ""
    # Reference links in the note (e.g. "See Select rows to ingest"). The
    # primary one is the technical doc the one-pager should link to and expand.
    ref_links: list[RefLink] = Field(default_factory=list)
    # Provenance for auditing / re-fetch.
    source: Literal["rss", "archive", "fixture"] = "rss"
    fetched_at: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def _strip_invisible(cls, v: str) -> str:
        # Scraped Databricks headings carry trailing zero-width spaces; this
        # also cleans notes stored before the fetcher stripped them.
        return re.sub("[\\u200b\\u200c\\u200d\\u2060\\ufeff]", "", v).strip()

    @staticmethod
    def make_id(note_date: date, title: str) -> str:
        base = f"{note_date.isoformat()}-{slugify(title)}"
        # Guard against pathological collisions with a short content hash.
        if len(base) > 90:
            digest = hashlib.sha1(title.encode()).hexdigest()[:8]
            base = f"{note_date.isoformat()}-{digest}"
        return base


# --------------------------------------------------------------------------
# One-pager content contract (maps 1:1 to the design slots)
# --------------------------------------------------------------------------
Maturity = Literal["ga", "public-preview", "beta", "gated-preview", "eol", "changed"]


class Capability(BaseModel):
    title: str = Field(..., description="Short capability name (2-4 words)")
    desc: str = Field(..., description="One concise sentence")


class Step(BaseModel):
    title: str = Field(..., description="Imperative step name (1-3 words)")
    desc: str = Field(..., description="One short sentence")


class OnePager(BaseModel):
    """Everything needed to render a one-pager for one release note."""

    # -- header
    product: str = Field(..., description="Feature/product name — the H1")
    tagline: str = Field(..., description="1-2 sentence subtitle under the title")
    updated: str = Field(..., description="Human date, e.g. 'Jun 16, 2026'")
    status_label: str = Field(..., description="Badge text, e.g. 'GA', 'Public Preview'")
    status: Maturity = "changed"
    docs_url: str = Field("", description="Canonical Databricks docs link")
    source_url: str = Field("", description="Release-note URL this was built from")

    # -- body
    what_it_does: str = Field(..., description="Technical explanation paragraph")
    why_it_matters: str = Field(..., description="Business impact paragraph")
    # Plain-language one-liner for readers who just want the gist — shown as an
    # "In short" block, especially for notes with no concrete adoption steps.
    plain_summary: str = Field("", description="One plain-English sentence a non-expert understands")
    capabilities: list[Capability] = Field(default_factory=list, max_length=4)
    prerequisites: list[str] = Field(default_factory=list, max_length=5)
    use_cases: list[str] = Field(default_factory=list, max_length=6)
    limitations: list[str] = Field(default_factory=list, max_length=5)
    # Architecture strip: ordered stages/components, rendered as chips.
    architecture: list[str] = Field(default_factory=list, max_length=6)
    steps: list[Step] = Field(default_factory=list, max_length=5)
    key_takeaway: str = Field(..., description="One-sentence executive summary")

    # -- linkage back to the source record (not LLM-filled)
    note_id: str = ""
    category: str = "platform"

    @classmethod
    def json_schema_for_llm(cls) -> dict:
        """Schema used as the Claude tool input — omits linkage fields the
        model must not invent (note_id/category are set from the record)."""
        schema = cls.model_json_schema()
        for drop in ("note_id", "category"):
            schema.get("properties", {}).pop(drop, None)
        schema["required"] = [
            "product", "tagline", "updated", "status_label", "status",
            "what_it_does", "why_it_matters", "key_takeaway",
        ]
        schema["additionalProperties"] = False
        return schema
