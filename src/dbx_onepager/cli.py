"""Command-line entrypoint.

Examples:
    # Weekly incremental (the scheduled job): fetch new notes, enrich, rebuild.
    python -m dbx_onepager weekly

    # Backfill historical notes for a month range, then rebuild.
    python -m dbx_onepager backfill --from 2025-01 --to 2025-12

    # Offline demo/test over fixtures (no network, no API key needed).
    python -m dbx_onepager fixtures --mock

    # Re-enrich anything pending / rebuild the static site only.
    python -m dbx_onepager enrich
    python -m dbx_onepager build

Global flags:
    --mock    Skip the LLM; build one-pagers with the offline heuristic.
    --model   Override the model id (e.g. claude-opus-4-8) for this run.
    --config  Path to a config.yaml (defaults to repo root).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from . import pipeline


def _parse_month(value: str) -> date:
    """Parse 'YYYY-MM' (or 'YYYY-MM-DD') into a date on the 1st of the month."""
    parts = value.split("-")
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM, got {value!r}")
    year, month = int(parts[0]), int(parts[1])
    return date(year, month, 1)


def build_parser() -> argparse.ArgumentParser:
    # Common flags usable either before OR after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=None, help="Path to config.yaml")
    common.add_argument("--model", default=None, help="Override LLM model id")
    common.add_argument("--mock", action="store_true", help="Use offline heuristic, no LLM")

    p = argparse.ArgumentParser(prog="dbx_onepager", description=__doc__, parents=[common])
    sub = p.add_subparsers(dest="command", required=True)

    wk = sub.add_parser("weekly", parents=[common],
                        help="Fetch new notes via RSS, enrich, rebuild site")
    wk.add_argument("--refresh", action="store_true",
                    help="Re-fetch and overwrite matching notes (updates links, "
                         "re-enriches) instead of skipping ones already stored")

    bf = sub.add_parser("backfill", parents=[common],
                        help="Backfill historical notes by month range")
    bf.add_argument("--from", dest="start", required=True, type=_parse_month,
                    help="Start month YYYY-MM")
    bf.add_argument("--to", dest="end", required=True, type=_parse_month,
                    help="End month YYYY-MM (inclusive)")
    bf.add_argument("--refresh", action="store_true",
                    help="Re-fetch and overwrite matching notes (updates links, "
                         "re-enriches) instead of skipping ones already stored")

    sub.add_parser("fixtures", parents=[common], help="Run offline over fixtures/ (dev + CI)")
    en = sub.add_parser("enrich", parents=[common], help="Enrich pending notes, rebuild site")
    en.add_argument("--force", action="store_true",
                    help="Re-enrich ALL stored notes (refresh existing one-pagers)")
    sub.add_parser("build", parents=[common], help="Rebuild the static site from existing data")

    em = sub.add_parser("email-summary", parents=[common],
                        help="Emit an HTML email digest of recent one-pagers")
    em.add_argument("--days", type=int, default=7,
                    help="Look-back window in days (default 7)")
    em.add_argument("--month", default=None, metavar="YYYY-MM",
                    help="Calendar-month digest instead of the rolling window")
    em.add_argument("--site-url", default=None,
                    help="Published Pages base URL (default: render.pages_url from config)")
    em.add_argument("--out", default="email/body.html",
                    help="Where to write the HTML body (default email/body.html)")
    em.add_argument("--subject-out", default="email/subject.txt",
                    help="Where to write the subject line (default email/subject.txt)")
    em.add_argument("--send", action="store_true",
                    help="Also send via Microsoft Graph. Requires env vars "
                         "GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, "
                         "MAIL_SENDER, MAIL_TO (comma-separated recipients)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cmd = args.command
    if cmd == "weekly":
        pipeline.run_weekly(args.config, args.model, args.mock, refresh=args.refresh)
    elif cmd == "backfill":
        pipeline.run_backfill(args.config, args.start, args.end, args.model,
                              args.mock, refresh=args.refresh)
    elif cmd == "fixtures":
        pipeline.run_fixtures(args.config, args.model, args.mock)
    elif cmd == "enrich":
        pipeline.run_enrich(args.config, args.model, args.mock, force=args.force)
    elif cmd == "build":
        pipeline.run_build(args.config)
    elif cmd == "email-summary":
        pipeline.run_email_summary(args.config, args.days, args.site_url,
                                   args.out, args.subject_out, send=args.send,
                                   month=args.month)
    else:  # pragma: no cover - argparse enforces
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
