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


def _enrich_pending(store: Store, cfg: dict, model: Optional[str], mock: bool) -> int:
    pending = store.notes_needing_enrichment()
    print(f"enrich: {len(pending)} note(s) pending")
    done = 0
    for note in pending:
        try:
            op = enrich_note(note, cfg, model=model, mock=mock)
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


def run_weekly(config_path: Optional[str], model: Optional[str], mock: bool) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    print("fetch: pulling latest release notes (RSS → index fallback)…")
    notes = fetch.fetch_new(cfg)
    new = store.add_notes(notes)
    print(f"fetch: {len(notes)} found, {len(new)} new")
    _enrich_pending(store, cfg, model, mock)
    _finish(store, cfg, paths)


def run_backfill(
    config_path: Optional[str],
    start: date,
    end: date,
    model: Optional[str],
    mock: bool,
) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    print(f"backfill: walking archives {start} … {end}")
    notes = fetch.fetch_archive_range(cfg, start, end)
    new = store.add_notes(notes)
    print(f"backfill: {len(notes)} found, {len(new)} new")
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


def run_enrich(config_path: Optional[str], model: Optional[str], mock: bool) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    _enrich_pending(store, cfg, model, mock)
    _finish(store, cfg, paths)


def run_build(config_path: Optional[str]) -> None:
    cfg = load_config(config_path)
    paths = Paths(cfg)
    store = Store(paths)
    _finish(store, cfg, paths)
