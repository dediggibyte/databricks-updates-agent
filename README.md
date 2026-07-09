# Databricks Updates Agent

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Pipeline](https://github.com/dediggibyte/databricks-updates-agent/actions/workflows/weekly.yml/badge.svg)](https://github.com/dediggibyte/databricks-updates-agent/actions/workflows/weekly.yml)
[![Email digest](https://github.com/dediggibyte/databricks-updates-agent/actions/workflows/notify.yml/badge.svg)](https://github.com/dediggibyte/databricks-updates-agent/actions/workflows/notify.yml)
[![Site](https://img.shields.io/badge/site-GitHub%20Pages-blue)](https://dediggibyte.github.io/databricks-updates-agent/)

**Automatically turns Databricks release notes into executive one-pagers — technical and business — published to GitHub Pages and emailed to the team weekly.**

Each one-pager explains an update *technically* (what changed, prerequisites,
limitations) and from a *business perspective* (why it matters, use cases).
The pipeline runs **every day** (and redeploys on every merge to `main`), can
**backfill any past release notes** on demand, and mails a **weekly digest**
every Tuesday with links to the published gallery — never more often.

![One-pager + gallery](docs/preview.png)

---

## Features

- **Daily auto-fetch** of Databricks platform release notes (RSS with an index-scrape fallback, headless Chromium via Playwright to pass the docs bot-wall), so the site is never more than a day behind.
- **Depth from the source doc** — each note's "See …" link is followed to the real feature documentation, which drives the enrichment and becomes the one-pager's docs link.
- **Pluggable enrichment** — free GitHub Models (default), Anthropic Claude, or a keyless deterministic heuristic; every provider degrades gracefully to the heuristic.
- **Dual-theme one-pagers** — light COE app look by default plus a navy dark alternate, rendered from a single Pydantic content contract.
- **Searchable gallery** on GitHub Pages with status filters and sorting.
- **Weekly email digest** to the Databricks COE DL every Tuesday — including "no updates this week" — plus a **consolidated monthly digest** on the last day of each month. Daily site refreshes and merge deploys never email.
- **Historical backfill** for any month range, on demand from the Actions tab.

---

## Quick Start

```bash
git clone https://github.com/dediggibyte/databricks-updates-agent.git
cd databricks-updates-agent
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m playwright install chromium          # only needed for live fetch

# Offline demo over sample notes in fixtures/ (no network, no API key):
python -m dbx_onepager fixtures --mock
open site/index.html
```

---

## How It Works

```
fetch  →  store  →  enrich (LLM)  →  render  →  gallery  →  email digest
```

| Stage | Module | What it does |
|-------|--------|--------------|
| **fetch**  | `fetch.py`   | Pulls release notes (RSS weekly, archive backfill) **and extracts each note's reference links**, then fetches the **underlying technical doc** it points to (cached under `data/docs/`). Strips doc chrome and invisible characters so scraped text stays clean. |
| **store**  | `store.py`   | Durable JSON per note, **deduped by id**. Keeps full history so any past note is always re-generatable. |
| **enrich** | `enrich.py`  | Turns each note **plus its underlying tech doc** into the structured one-pager contract. Pluggable provider (see below); always falls back to a keyless heuristic. |
| **render** | `render.py`  | Fills the Jinja2 templates with the COE Platform design tokens → one self-contained HTML page per note, plus the searchable `index.html` gallery. |
| **notify** | `notify.py`  | Builds the weekly HTML email digest (recent updates + links to their one-pagers and the gallery). |

The one-pager **content contract** lives in `models.py` (`OnePager`). That single
Pydantic model drives the LLM tool schema *and* the template, so they can
never drift apart.

The rendered site is **never committed** — CI builds `site/` fresh each run and
deploys it straight to GitHub Pages as an artifact. Only `data/` (the durable
source of truth) lives in git.

---

## Project Structure

```
config.yaml                 source / model / render / pages-url settings
assets/ds/tokens/*.css      COE Platform design tokens (ported from coe_platform)
templates/                  onepager.html.j2, gallery.html.j2
src/dbx_onepager/           fetch · store · enrich · render · notify · pipeline · cli
fixtures/                   sample release notes for offline runs/tests
tests/                      pytest suite (offline, no network)
data/releases/              raw normalized notes (source of truth, git-tracked)
data/onepagers/             enriched one-pager JSON (git-tracked)
data/docs/                  cached underlying technical docs (git-tracked)
site/                       rendered HTML — generated, gitignored, built in CI
.github/workflows/          weekly.yml · notify.yml · pr-template-check.yml
```

---

## Usage

```bash
# Incremental fetch — the (daily) scheduled job. Fetch new notes, enrich, rebuild.
python -m dbx_onepager weekly

# Backfill past release notes for a month range (on-demand).
python -m dbx_onepager backfill --from 2025-01 --to 2025-12

# Re-enrich anything pending / rebuild the static site only.
python -m dbx_onepager enrich
python -m dbx_onepager build

# Refresh EXISTING notes with newer logic (re-fetch reference links +
# underlying docs, then re-enrich). Use after upgrading the pipeline.
python -m dbx_onepager backfill --from 2026-06 --to 2026-07 --refresh
python -m dbx_onepager enrich --force        # re-enrich stored notes in place

# Build the weekly email digest (HTML body + subject) from stored data.
python -m dbx_onepager email-summary --days 7

# Build a consolidated calendar-month digest instead.
python -m dbx_onepager email-summary --month 2026-06
```

Global flags (usable before or after the subcommand):

| Flag | Meaning |
|------|---------|
| `--mock`  | Skip the LLM; build one-pagers with the offline heuristic. |
| `--model` | Override the model id for the run (e.g. `claude-opus-4-8`). |
| `--config`| Path to an alternate `config.yaml`. |

---

## Enrichment Providers

Set `llm.provider` in [`config.yaml`](config.yaml):

| Provider | Key needed | Cost | Notes |
|----------|-----------|------|-------|
| `github-models` *(default, `openai/gpt-4o-mini`)* | **None** — uses the `GITHUB_TOKEN` Actions provides automatically | Free (rate-limited) | GitHub's built-in AI. Real technical + business write-ups with nothing to obtain or pay for. |
| `heuristic` | None | Free | No AI, no network. Deterministic section extraction (prerequisites, limitations, use-cases, capabilities). |
| `anthropic` | `ANTHROPIC_API_KEY` | Paid | Highest quality (Claude, `claude-sonnet-5` by default; pass `--model claude-opus-4-8` for high-value notes). |

Any provider **automatically falls back to `heuristic`** if it errors, so the
pipeline always produces output. Run locally with no AI at all via `--mock`.

> Using `github-models` in Actions requires the workflow's `models: read`
> permission (already set) and that GitHub Models is enabled for your org
> (free). If it isn't, runs still succeed via the heuristic fallback.

---

## Configuration

Everything retargetable lives in [`config.yaml`](config.yaml): the source
(cloud, RSS/archive URLs), the enrichment provider/model, rendering options
(default variant, alternate theme, site title), and `render.pages_url` (the
published site base URL used for links in the email digest). No code changes
needed to switch cloud, provider, or model.

### Repository secrets

| Secret | Required | Used by | Purpose |
|--------|----------|---------|---------|
| `GRAPH_TENANT_ID` | For email | `notify.yml` | Entra (Azure AD) tenant id of the diggibyte.com Microsoft 365 tenant. |
| `GRAPH_CLIENT_ID` | For email | `notify.yml` | App registration (client) id with the **Mail.Send** application permission, admin-consented. |
| `GRAPH_CLIENT_SECRET` | For email | `notify.yml` | Client secret of that app registration. |
| `MAIL_SENDER` | For email | `notify.yml` | Mailbox the digest is sent as (e.g. `someone@diggibyte.com`). |
| `MODELS_TOKEN` | Optional | `weekly.yml` | Fine-grained PAT with **Models: read** — needed for LLM enrichment only if GitHub Models is not enabled for the org (otherwise the built-in `GITHUB_TOKEN` suffices). |
| `ANTHROPIC_API_KEY` | Optional | `weekly.yml` | Only if `llm.provider` is switched to `anthropic`. |

> Email uses **Microsoft Graph `sendMail`** (OAuth client credentials).
> Exchange Online retired basic username/password SMTP auth in April 2026,
> so an Entra **app registration** is required: Entra admin center → App
> registrations → New → API permissions → Microsoft Graph → *Application*
> permissions → `Mail.Send` → **Grant admin consent** → Certificates &
> secrets → new client secret. Optionally scope it to one mailbox with an
> Exchange [application access policy](https://learn.microsoft.com/en-us/graph/auth-limit-mailbox-access).

---

## CI/CD

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| [`weekly.yml`](.github/workflows/weekly.yml) | Daily 07:00 UTC cron, every push to `main`, + manual dispatch (`mode`: `weekly` / `backfill` / `reenrich`, plus `refresh` and `model` inputs) | Cron/dispatch: fetch → enrich → commit refreshed `data/` → build `site/` → deploy to GitHub Pages. Push: rebuild from stored `data/` and redeploy only (no fetch, no email). |
| [`notify.yml`](.github/workflows/notify.yml) | After successful pipeline runs (`workflow_run`, guarded), last day of every month (cron + guard), + manual dispatch (`days` or `month` input) | Builds the digest with `email-summary --send` and mails it to `dl-databricks-coe@diggibyte.com` via Microsoft Graph. Weekly digest goes out only after the **Tuesday** scheduled run; daily and merge-triggered runs are skipped. Monthly digest consolidates the calendar month. |
| [`pr-template-check.yml`](.github/workflows/pr-template-check.yml) | Pull requests | Enforces the repository PR template (marker + required sections). |

**Setup:** enable Pages (Settings → Pages → Source: **GitHub Actions**) and add
the two mail secrets above. Nothing else — the default enrichment provider
uses the built-in `GITHUB_TOKEN`.

---

## Extending

- **Other release-note streams** (Runtime, SQL, Azure/GCP): point `config.yaml`
  at a different feed/archive, or run multiple configs.
- **Design tweaks**: edit `templates/onepager.html.j2`; tokens live in
  `assets/ds/tokens/`.
- **Email cadence/audience**: recipients live in
  [`notify.yml`](.github/workflows/notify.yml); the look-back window is the
  `--days` flag of `email-summary`.
