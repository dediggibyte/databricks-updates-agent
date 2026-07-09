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


_NOTE_WITH_SECTIONS = (
    "Feature Z is generally available. It streamlines ingestion.\n\n"
    "Highlights:\n\n- Serverless execution.\n- Native CDC.\n\n"
    "Prerequisites:\n\n- Unity Catalog enabled.\n- A supported region.\n\n"
    "Limitations:\n\n- No Windows support yet.\n"
)


def test_heuristic_extracts_sections():
    cfg = {"llm": {}, "source": {}}
    op = enrich_note(_note(body=_NOTE_WITH_SECTIONS), cfg, mock=True)
    assert "Unity Catalog enabled." in op.prerequisites
    assert "A supported region." in op.prerequisites
    assert "No Windows support yet." in op.limitations
    # Highlights become capabilities, not confused with prereqs/limits.
    cap_text = " ".join(c.desc for c in op.capabilities)
    assert "Serverless execution." in cap_text
    assert "Unity Catalog enabled." not in cap_text


def test_truncate_words_never_cuts_mid_word():
    from dbx_onepager.enrich import _truncate_words

    title = (
        "Delta Sharing recipient can now query shared streaming tables in "
        "Databricks SQL warehouses"
    )
    out = _truncate_words(title, 80)
    assert len(out) <= 80
    assert out.endswith("…")
    assert "Databr…" not in out                     # no mid-word cut
    assert all(w in title for w in out[:-1].split())  # only whole words survive
    assert _truncate_words("short title", 80) == "short title"


def test_title_zero_width_space_stripped():
    op = enrich_note(
        _note(title="Feature X is now generally available ​"),
        {"llm": {}, "source": {}},
        mock=True,
    )
    assert op.product == "Feature X is now generally available"


def test_doc_chrome_stripped():
    from dbx_onepager.fetch import _strip_doc_chrome

    md = (
        "On this page\n\n"
        "Last updated on **Jul 8, 2026**\n\n"
        "Real content about the feature.\n\n"
        '## Limitations[​](#limitations "Direct link to Limitations")\n\n'
        "- No Windows support yet.\n"
    )
    out = _strip_doc_chrome(md)
    assert "On this page" not in out
    assert "Last updated on" not in out
    assert "Direct link to" not in out
    assert "Real content about the feature." in out
    assert "No Windows support yet." in out


def test_email_digest_selects_recent_and_builds_html():
    from datetime import date

    from dbx_onepager.notify import build_html, build_subject, recent_onepagers

    def _op(note_id, product="Feature X"):
        return OnePager(
            product=product, tagline="Does a thing.", updated="Jul 8, 2026",
            status_label="GA", status="ga", what_it_does="x", why_it_matters="y",
            key_takeaway="z", note_id=note_id,
        )

    ops = [_op("2026-07-08-new"), _op("2026-05-01-old")]
    today = date(2026, 7, 9)
    recent = recent_onepagers(ops, days=7, today=today)
    assert [o.note_id for o in recent] == ["2026-07-08-new"]

    assert build_subject(recent, today) == "Databricks updates — 1 new release note (Jul 09, 2026)"
    html_body = build_html(recent, "https://example.github.io/repo/", days=7)
    assert "https://example.github.io/repo/onepagers/2026-07-08-new.html" in html_body
    assert "Feature X" in html_body

    empty = build_html([], "https://example.github.io/repo", days=7)
    assert "No Databricks platform updates" in empty
    assert build_subject([], today).startswith("Databricks updates — no new release notes")


def test_monthly_digest_selects_calendar_month():
    from dbx_onepager.notify import build_subject, month_onepagers

    def _op(note_id):
        return OnePager(
            product="X", tagline="t", updated="u", status_label="GA", status="ga",
            what_it_does="x", why_it_matters="y", key_takeaway="z", note_id=note_id,
        )

    ops = [_op("2026-06-30-last"), _op("2026-07-01-next"), _op("2026-06-01-first")]
    june = month_onepagers(ops, "2026-06")
    assert [o.note_id for o in june] == ["2026-06-30-last", "2026-06-01-first"]
    assert build_subject(june, month="2026-06") == (
        "Databricks updates — June 2026 monthly digest (2 release notes)"
    )
    assert build_subject([], month="2026-06").startswith(
        "Databricks updates — no release notes in June 2026"
    )


def test_graph_message_payload():
    from dbx_onepager.notify import graph_message

    msg = graph_message("Subject", "<p>hi</p>", ["a@x.com", " b@x.com ", ""])
    assert msg["message"]["subject"] == "Subject"
    assert msg["message"]["body"] == {"contentType": "HTML", "content": "<p>hi</p>"}
    assert [r["emailAddress"]["address"] for r in msg["message"]["toRecipients"]] == [
        "a@x.com", "b@x.com",
    ]
    assert msg["saveToSentItems"] is False


def test_extract_json_tolerates_code_fences():
    from dbx_onepager.enrich import _extract_json

    assert _extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert _extract_json('here you go: {"a": 2} thanks') == {"a": 2}
    assert _extract_json('{"a": 3}') == {"a": 3}


def test_clean_text_strips_markdown_links_bold_and_leading_date():
    from dbx_onepager.enrich import _clean_text

    out = _clean_text("**June 8, 2026** External lineage is now GA. See [docs](/x).")
    assert out.startswith("External lineage")
    assert "[" not in out and "**" not in out
    assert "June 8, 2026" not in out


def test_store_refresh_overwrites_and_invalidates_onepager(tmp_path):
    from dbx_onepager.store import Store

    class _P:  # minimal Paths stand-in
        def __init__(self, base):
            self.releases = base / "releases"
            self.onepagers = base / "onepagers"
            self.docs = base / "docs"
            self.site = base / "site"
            self.site_onepagers = base / "site" / "onepagers"

        def ensure(self):
            for d in (self.releases, self.onepagers, self.docs,
                      self.site, self.site_onepagers):
                d.mkdir(parents=True, exist_ok=True)

    store = Store(_P(tmp_path))
    note = _note()
    store.add_notes([note])
    op = enrich_note(note, {"llm": {}, "source": {}, "doc": {"fetch_underlying": False}}, mock=True)
    store.save_onepager(op)
    assert store.has_onepager(note.id)

    assert store.add_notes([note]) == []            # already stored -> skipped
    saved = store.add_notes([note], refresh=True)    # refresh -> re-saved
    assert len(saved) == 1
    assert not store.has_onepager(note.id)           # stale one-pager dropped


def test_extract_links_resolves_relative_and_skips_anchors():
    from dbx_onepager.fetch import _extract_links

    html = (
        '<p>See <a href="/aws/en/ingestion/lakeflow-connect/row-filtering">'
        "Select rows to ingest</a> and <a href=\"#top\">top</a>.</p>"
    )
    links = _extract_links(html, "https://docs.databricks.com/aws/en/release-notes/product/")
    urls = [l.url for l in links]
    assert "https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/row-filtering" in urls
    assert not any(u.endswith("#top") for u in urls)  # in-page anchors skipped


def test_pick_primary_doc_prefers_tech_doc_over_release_note():
    from dbx_onepager.fetch import pick_primary_doc
    from dbx_onepager.models import RefLink

    note = _note(
        ref_links=[
            RefLink(text="another note", url="https://docs.databricks.com/aws/en/release-notes/product/2026/june"),
            RefLink(text="Select rows to ingest", url="https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/row-filtering"),
        ]
    )
    assert pick_primary_doc(note).endswith("/row-filtering")


def test_enrich_sets_docs_url_to_tech_reference():
    from dbx_onepager.models import RefLink

    note = _note(
        ref_links=[RefLink(text="doc", url="https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/row-filtering")]
    )
    cfg = {"llm": {}, "source": {}, "doc": {"fetch_underlying": False}}
    op = enrich_note(note, cfg, mock=True)
    assert op.docs_url.endswith("/row-filtering")     # tech doc, not the note
    assert op.source_url == note.url                  # provenance kept


def test_provider_falls_back_to_heuristic_when_unavailable():
    # provider=github-models but no GITHUB_TOKEN -> must not raise, degrades.
    import os

    cfg = {"llm": {"provider": "github-models"}, "source": {}}
    saved = os.environ.pop("GITHUB_TOKEN", None), os.environ.pop("GH_TOKEN", None)
    try:
        op = enrich_note(_note(), cfg)
        assert isinstance(op, OnePager)
        assert op.what_it_does
    finally:
        if saved[0]:
            os.environ["GITHUB_TOKEN"] = saved[0]
        if saved[1]:
            os.environ["GH_TOKEN"] = saved[1]


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
