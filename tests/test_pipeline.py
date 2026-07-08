"""Smoke tests that exercise the offline path end-to-end (no network/API)."""

from datetime import date

from dbx_onepager.enrich import enrich_note
from dbx_onepager.fetch import detect_status
from dbx_onepager.models import OnePager, ReleaseNote


def _note(**kw) -> ReleaseNote:
    base = dict(
        id="2026-06-16-x",
        title="Feature X is now generally available",
        date=date(2026, 6, 16),
        url="https://example.com",
        body="Feature X is now generally available. It does a useful thing.",
    )
    base.update(kw)
    return ReleaseNote(**base)


def test_status_detection_handles_wrapped_phrases():
    assert detect_status("now in Public\nPreview")[0] == "public-preview"
    assert detect_status("is generally available")[0] == "ga"
    assert detect_status("nothing notable here")[0] == "changed"


def test_make_id_is_stable_and_dated():
    a = ReleaseNote.make_id(date(2026, 6, 16), "Feature X!")
    b = ReleaseNote.make_id(date(2026, 6, 16), "Feature X!")
    assert a == b
    assert a.startswith("2026-06-16-")


def test_heuristic_enrichment_produces_valid_onepager():
    cfg = {"llm": {}, "source": {}}
    op = enrich_note(_note(), cfg, mock=True)
    assert isinstance(op, OnePager)
    assert op.product
    assert op.what_it_does
    assert op.key_takeaway
    assert op.status == "ga"
    assert op.note_id == "2026-06-16-x"          # linkage set from the record
    assert op.source_url == "https://example.com"


def test_llm_schema_drops_linkage_fields():
    schema = OnePager.json_schema_for_llm()
    assert "note_id" not in schema["properties"]
    assert "category" not in schema["properties"]
    assert "product" in schema["required"]


_SAMPLE_HTML = """
<html><body><article>
  <h1>Platform release notes</h1>
  <h2 id="feat-a">Feature A is generally available</h2>
  <p>Feature A does something on June 3, 2026.</p>
  <ul><li>bullet one</li><li>bullet two</li></ul>
  <h2 id="feat-b">Feature B is in Public Preview</h2>
  <p>Feature B is a preview thing.</p>
  <h3>Some sub-note</h3>
  <p>Details for the sub note.</p>
</article></body></html>
"""


def test_parse_notes_from_html_splits_and_dedupes():
    from datetime import date

    from dbx_onepager.fetch import parse_notes_from_html

    cfg = {"source": {"cloud": "aws", "category": "platform"}}
    notes = parse_notes_from_html(
        _SAMPLE_HTML, cfg, date(2026, 6, 1), "https://x/product/", "archive"
    )
    titles = [n.title for n in notes]
    assert "Feature A is generally available" in titles
    assert "Feature B is in Public Preview" in titles
    a = next(n for n in notes if n.title.startswith("Feature A"))
    # Nested <li> text captured once (via the <ul>), not duplicated.
    assert a.body.count("bullet one") == 1
    # Explicit in-text date parsed; anchor id used for the URL.
    assert a.date == date(2026, 6, 3)
    assert a.url.endswith("#feat-a")
