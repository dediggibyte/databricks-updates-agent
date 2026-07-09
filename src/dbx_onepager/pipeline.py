"""Orchestration: wire fetch -> store -> enrich -> render together."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from . import fetch
from .config import Paths, load_config
from .enrich import enrich_note
from .models import ReleaseNote
from .render import build_site
from .store import Store


def _enrich_pending(
    store: Store, cfg: dict, model: Optional[str], mock: bool, force: bool = False
) -> int:
    pending = store.all_notes() if force else store.notes_needing_enrichment()
    verb = "re-enrich (forced)" if force else "enrich"
    print(f"{verb}: {len(pending)} note(s)")
    done = 0
    for note in pending:
        try:
            op = enrich_note(note, cfg, model=model, mock=mock, docs_cache=store.paths.docs)
            store.save_onepager(op)
            done += 1
            print(f"  ✓ {note.id}")
        except Exception as err:  # noqa: BLE001 - keep going on a single failure
            print(f"  ✗ {note.id}: {err}")
    return done


def _finish(store: Store, cfg: dict, paths: Paths) -> None:
    onepagers = store.all_onepagers()
    build_site(onepagers, cfg, paths)
    print(f"site: rebuilt with {len(onepagers)} one-pager(s) -> {paths.site}")


def run_weekly(
    config_path: Optional[str], model: Optional[str], mock: bool, refresh: bool = False
) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    print("fetch: pulling latest release notes (RSS → index fallback)…")
    notes = fetch.fetch_new(cfg)
    saved = store.add_notes(notes, refresh=refresh)
    print(f"fetch: {len(notes)} found, {len(saved)} {'refreshed' if refresh else 'new'}")
    _enrich_pending(store, cfg, model, mock)
    _finish(store, cfg, paths)


def run_backfill(
    config_path: Optional[str],
    start: date,
    end: date,
    model: Optional[str],
    mock: bool,
    refresh: bool = False,
) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    print(f"backfill: walking archives {start} … {end}")
    notes = fetch.fetch_archive_range(cfg, start, end)
    saved = store.add_notes(notes, refresh=refresh)
    print(f"backfill: {len(notes)} found, {len(saved)} {'refreshed' if refresh else 'new'}")
    _enrich_pending(store, cfg, model, mock)
    _finish(store, cfg, paths)


def run_fixtures(config_path: Optional[str], model: Optional[str], mock: bool) -> None:
    """Offline pipeline over sample notes in ``fixtures/`` — for dev and CI."""
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    notes = fetch.load_fixtures(paths.fixtures)
    new = store.add_notes(notes)
    print(f"fixtures: {len(notes)} loaded, {len(new)} new")
    _enrich_pending(store, cfg, model, mock)
    _finish(store, cfg, paths)


def run_enrich(
    config_path: Optional[str], model: Optional[str], mock: bool, force: bool = False
) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    _enrich_pending(store, cfg, model, mock, force=force)
    _finish(store, cfg, paths)


def run_build(config_path: Optional[str]) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    _finish(store, cfg, paths)


def run_email_summary(
    config_path: Optional[str],
    days: int,
    site_url: Optional[str],
    out: str,
    subject_out: str,
    send: bool = False,
    month: Optional[str] = None,
) -> None:
    """Write the weekly (or ``month`` calendar) email digest from stored data."""
    import os

    from .notify import send_via_graph, write_email

    cfg = load_config(config_path)
    store = Store(Paths(cfg))
    url = site_url or (cfg.get("render") or {}).get("pages_url", "")
    if not url:
        raise SystemExit("email-summary: set render.pages_url in config.yaml or pass --site-url")
    write_email(store.all_onepagers(), days, url, out, subject_out, month=month)
    if send:
        required = ("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET",
                    "MAIL_SENDER", "MAIL_TO")
        missing = [v for v in required if not os.environ.get(v)]
        if missing:
            raise SystemExit(f"email-summary --send: missing env vars: {', '.join(missing)}")
        send_via_graph(
            subject=Path(subject_out).read_text(encoding="utf-8").strip(),
            html_body=Path(out).read_text(encoding="utf-8"),
            sender=os.environ["MAIL_SENDER"],
            recipients=os.environ["MAIL_TO"].split(","),
            tenant_id=os.environ["GRAPH_TENANT_ID"],
            client_id=os.environ["GRAPH_CLIENT_ID"],
            client_secret=os.environ["GRAPH_CLIENT_SECRET"],
        )
