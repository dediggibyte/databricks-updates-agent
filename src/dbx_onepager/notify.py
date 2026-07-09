"""Build and send the HTML email digest from stored one-pagers.

Three cadences from one builder, selected by the CLI flags:

* **daily**   — ``email-summary --days 1``  (compact header, no stats strip)
* **weekly**  — ``email-summary --days 7``  (stats strip + item list; default)
* **monthly** — ``email-summary --month YYYY-MM`` (calendar-month consolidation)

Selects one-pagers whose note date (the ``YYYY-MM-DD`` prefix of ``note_id``,
the same convention ``render._sort_key`` relies on) falls within the window
and emits a self-contained HTML body plus a subject line. Consumed by
``.github/workflows/notify.yml``.

Delivery is Microsoft Graph ``sendMail`` with OAuth client credentials —
Exchange Online retired basic (username/password) SMTP auth in April 2026,
so an Entra app registration with the ``Mail.Send`` application permission
is the supported way to send from a Microsoft 365 mailbox.

Design notes: email clients ignore external stylesheets, so the markup is
table-based with inline styles and concrete hex colors mirroring the COE
Platform theme (Databricks navy header #1B3139, Lava rail #FF3621, lava
action #E62D1A, warm oat surfaces, soft-fill status badges from ui.tsx).
It renders correctly in Outlook desktop (Word
engine: no flexbox, border-radius degrades gracefully), Outlook web, and
Gmail. Fonts fall back Segoe UI → Helvetica → Arial; mono is Consolas.
"""

from __future__ import annotations

import html
import json
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from .models import OnePager

# Maturity → (accent, soft fill): accent colors the 3px left rail + badge
# text, soft fill is the badge background — the COE Platform Badge tones
# (coe_platform src/frontend/src/components/ui.tsx).
_STATUS_TONES = {
    "ga": ("#1F7A3D", "#E7F1E8"),              # green
    "public-preview": ("#1B5162", "#EAF1F2"),  # blue (teal)
    "gated-preview": ("#7A3B82", "#F2E7F3"),   # violet
    "beta": ("#B45309", "#FBEEDD"),            # amber
    "changed": ("#5A6B72", "#ECE6DC"),         # slate
    "eol": ("#C2362B", "#FCE6E2"),             # red
}

_FONT = "'Segoe UI',Helvetica,Arial,sans-serif"
_MONO = "Consolas,'Courier New',monospace"

# Concrete palette (email-safe mirror of the COE Platform tailwind theme).
_NAVY = "#1B3139"         # header surface (navy)
_LAVA = "#FF3621"         # brand square + accent rail (brand-600)
_ACTION = "#E62D1A"       # links/buttons on light (brand-700)
_PAPER_PAGE = "#EFEBE3"   # page behind the card (oat)
_PAPER_CARD = "#FFFFFF"   # item surface
_PAPER_WELL = "#FAF8F4"   # CTA well (oat-50)
_LINE = "#ECE6DC"         # card border (oat-200)
_LINE_SOFT = "#F1ECE4"    # inner separators
_TEXT_1 = "#1B3139"       # primary text (navy)
_TEXT_2 = "#5A6B72"       # secondary (muted)
_TEXT_3 = "#7B8A90"       # mono meta, dates
_TEXT_FOOT = "#8F887C"    # footer on page bg


def note_date(note_id: str) -> Optional[date]:
    """Parse the YYYY-MM-DD prefix of a note id; None if it has none."""
    try:
        return date.fromisoformat(note_id[:10])
    except ValueError:
        return None


def recent_onepagers(
    onepagers: list[OnePager], days: int, today: Optional[date] = None
) -> list[OnePager]:
    """One-pagers dated within the last ``days`` days, newest first."""
    today = today or date.today()
    cutoff = today - timedelta(days=days)
    picked = [
        op for op in onepagers
        if (d := note_date(op.note_id)) is not None and cutoff <= d <= today
    ]
    return sorted(picked, key=lambda op: op.note_id, reverse=True)


def month_onepagers(onepagers: list[OnePager], month: str) -> list[OnePager]:
    """One-pagers dated in calendar month ``month`` (``YYYY-MM``), newest first."""
    picked = [
        op for op in onepagers
        if note_date(op.note_id) is not None and op.note_id[:7] == month
    ]
    return sorted(picked, key=lambda op: op.note_id, reverse=True)


def month_label(month: str) -> str:
    """Human label for a ``YYYY-MM`` month, e.g. 'July 2026'."""
    return date.fromisoformat(month + "-01").strftime("%B %Y")


def build_subject(
    items: list[OnePager],
    today: Optional[date] = None,
    month: Optional[str] = None,
    days: Optional[int] = None,
) -> str:
    """Subject line. ``days=1`` switches to the daily wording; the weekly and
    monthly wordings are stable (relied on by tests and inbox rules)."""
    n = len(items)
    if month:
        label = month_label(month)
        if not items:
            return f"Databricks updates — no release notes in {label} (monthly digest)"
        return f"Databricks updates — {label} monthly digest ({n} release note{'s' if n != 1 else ''})"
    stamp = (today or date.today()).strftime("%b %d, %Y")
    if days == 1:
        if not items:
            return f"Databricks daily — no new release notes ({stamp})"
        return f"Databricks daily — {n} new release note{'s' if n != 1 else ''} ({stamp})"
    if not items:
        return f"Databricks updates — no new release notes ({stamp})"
    return f"Databricks updates — {n} new release note{'s' if n != 1 else ''} ({stamp})"


def _truncate(text: str, limit: int = 220) -> str:
    """Word-safe truncation for taglines so items stay scannable."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:")
    return cut + "…"


def _item_html(op: OnePager, site_url: str, last: bool, compact: bool) -> str:
    """One release note as a table row: status-tinted left rail, soft-fill
    badge + date, linked title, tagline, one-pager link."""
    accent, soft = _STATUS_TONES.get(op.status, _STATUS_TONES["changed"])
    link = f"{site_url}/onepagers/{op.note_id}.html"
    pad_v = "18px" if compact else "20px"
    title_size = "16px" if compact else "17px"
    sep = "" if last else f"border-bottom:1px solid {_LINE_SOFT};"
    return f"""\
          <tr>
            <td style="background:{_PAPER_CARD};border-left:1px solid {_LINE};border-right:1px solid {_LINE};padding:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:{pad_v} 26px 16px 23px;border-left:3px solid {accent};{sep}">
                    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td><span style="display:inline-block;padding:3px 9px;border-radius:9px;background:{soft};color:{accent};font-family:{_FONT};font-size:10px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;">{html.escape(op.status_label)}</span></td>
                        <td align="right" style="font-family:{_MONO};font-size:11px;color:{_TEXT_3};">{html.escape(op.updated)}</td>
                      </tr>
                    </table>
                    <div style="padding-top:10px;"><a href="{html.escape(link)}" style="font-family:{_FONT};font-size:{title_size};font-weight:700;line-height:1.35;color:{_TEXT_1};text-decoration:none;">{html.escape(op.product)}</a></div>
                    <div style="padding-top:6px;font-family:{_FONT};font-size:13px;line-height:1.55;color:{_TEXT_2};">{html.escape(_truncate(op.tagline))}</div>
                    <div style="padding-top:10px;"><a href="{html.escape(link)}" style="font-family:{_FONT};font-size:13px;font-weight:600;color:{_ACTION};text-decoration:none;">Read the one-pager &rarr;</a></div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>"""


def _stats_html(items: list[OnePager]) -> str:
    """NEW / NOW GA / IN PREVIEW strip (weekly + monthly digests)."""
    n = len(items)
    ga = sum(1 for op in items if op.status == "ga")
    prev = sum(1 for op in items if op.status in ("public-preview", "gated-preview", "beta"))
    cell = (
        '<td width="33%" align="center" style="padding:16px 8px 14px;{border}">'
        '<div style="font-family:' + _MONO + ';font-size:22px;font-weight:700;color:{color};">{value}</div>'
        '<div style="padding-top:4px;font-family:' + _FONT + ';font-size:10px;font-weight:600;'
        'letter-spacing:1.4px;color:' + _TEXT_3 + ';">{label}</div></td>'
    )
    sep = f"border-right:1px solid {_LINE_SOFT};"
    return f"""\
          <tr>
            <td style="background:{_PAPER_CARD};border-left:1px solid {_LINE};border-right:1px solid {_LINE};border-bottom:1px solid {_LINE};padding:0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
{cell.format(border=sep, color=_ACTION, value=n, label="NEW&nbsp;UPDATES")}
{cell.format(border=sep, color=_TEXT_1, value=ga, label="NOW&nbsp;GA")}
{cell.format(border="", color=_TEXT_1, value=prev, label="IN&nbsp;PREVIEW")}
                </tr>
              </table>
            </td>
          </tr>"""


def _empty_html(period: str) -> str:
    return f"""\
          <tr>
            <td style="background:{_PAPER_CARD};border-left:1px solid {_LINE};border-right:1px solid {_LINE};padding:26px;">
              <div style="font-family:{_FONT};font-size:14px;font-weight:600;color:{_TEXT_1};">No Databricks platform updates in {html.escape(period)}.</div>
              <div style="padding-top:6px;font-family:{_FONT};font-size:13px;line-height:1.55;color:{_TEXT_2};">Nothing new this period — the gallery below has every past update.</div>
            </td>
          </tr>"""


def build_html(
    items: list[OnePager], site_url: str, days: int, month: Optional[str] = None
) -> str:
    """The digest body. ``month`` → monthly, ``days == 1`` → daily, else weekly."""
    site_url = site_url.rstrip("/")
    n = len(items)
    today = date.today()

    if month:
        mode_tag, compact = "MONTHLY&nbsp;DIGEST", False
        period = month_label(month)
        headline = f"{n} platform update{'s' if n != 1 else ''} in {period}" if n else "A quiet month"
        subline = f"{period} &middot; Databricks platform release notes"
        cadence = "on the last day of each month"
    elif days == 1:
        mode_tag, compact = "DAILY&nbsp;DIGEST", True
        period = "the last day"
        headline = f"{n} new update{'s' if n != 1 else ''} today" if n else "No new updates today"
        subline = f"{today.strftime('%A, %b %d, %Y')} &middot; Databricks platform release notes"
        cadence = "after its daily check. Quiet days are skipped"
    else:
        mode_tag, compact = "WEEKLY&nbsp;DIGEST", False
        period = f"the last {days} days"
        headline = f"{n} platform update{'s' if n != 1 else ''} this week" if n else "A quiet week"
        start = (today - timedelta(days=days - 1)).strftime("%b %d")
        subline = f"{start} &ndash; {today.strftime('%b %d, %Y')} &middot; Databricks platform release notes"
        cadence = "after its weekly refresh"

    preheader = (
        "; ".join(op.product for op in items[:3]) + " — from the Databricks release notes."
        if items else f"No Databricks platform updates in {period}."
    )

    parts: list[str] = []
    if items and not compact:
        parts.append(_stats_html(items))
    if items:
        for i, op in enumerate(items):
            parts.append(_item_html(op, site_url, last=(i == n - 1), compact=compact))
    else:
        parts.append(_empty_html(period))
    body_rows = "\n".join(parts)

    head_pad = "18px 26px 20px" if compact else "22px 26px 24px"
    headline_size = "20px" if compact else "24px"

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <title>{html.escape(headline)}</title>
</head>
<body style="margin:0;padding:0;background:{_PAPER_PAGE};">
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{html.escape(preheader)}&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{_PAPER_PAGE};">
    <tr>
      <td align="center" style="padding:28px 12px 32px;">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="width:640px;max-width:100%;">

          <tr>
            <td style="background:{_NAVY};border-radius:10px 10px 0 0;padding:{head_pad};">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <table role="presentation" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="width:10px;height:10px;background:{_LAVA};font-size:0;line-height:0;">&nbsp;</td>
                        <td style="padding-left:9px;font-family:{_FONT};font-size:14px;font-weight:700;color:#ffffff;">databricks</td>
                        <td style="padding-left:11px;font-family:{_FONT};font-size:10px;font-weight:600;letter-spacing:1.6px;color:#7E8C92;">UPDATE&nbsp;ONE-PAGERS</td>
                      </tr>
                    </table>
                  </td>
                  <td align="right" style="font-family:{_MONO};font-size:11px;letter-spacing:1px;color:#7E8C92;">{mode_tag}</td>
                </tr>
              </table>
              <div style="padding-top:18px;font-family:{_FONT};font-size:{headline_size};font-weight:700;line-height:1.25;color:#ffffff;">{html.escape(headline)}</div>
              <div style="padding-top:6px;font-family:{_FONT};font-size:13px;color:#AEBBC0;">{subline}</div>
            </td>
          </tr>
          <tr><td style="height:3px;background:{_LAVA};font-size:0;line-height:0;">&nbsp;</td></tr>

{body_rows}

          <tr>
            <td align="center" style="background:{_PAPER_WELL};border:1px solid {_LINE};border-top:1px solid {_LINE};border-radius:0 0 10px 10px;padding:26px 26px 24px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:{_ACTION};border-radius:6px;">
                    <a href="{html.escape(site_url)}/" style="display:inline-block;padding:12px 30px;font-family:{_FONT};font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;">Browse all one-pagers</a>
                  </td>
                </tr>
              </table>
              <div style="padding-top:12px;font-family:{_MONO};font-size:11px;color:{_TEXT_3};">{html.escape(site_url.replace('https://', '').replace('http://', ''))}</div>
            </td>
          </tr>

          <tr>
            <td align="center" style="padding:18px 20px 0;">
              <div style="font-family:{_FONT};font-size:11px;line-height:1.7;color:{_TEXT_FOOT};">
                Sent automatically by the <a href="https://github.com/dediggibyte/databricks-updates-agent" style="color:{_TEXT_FOOT};">Databricks Updates Agent</a> {cadence}.<br>
                <a href="{html.escape(site_url)}/" style="color:{_ACTION};text-decoration:none;">Gallery</a>&nbsp;&nbsp;&middot;&nbsp;&nbsp;<a href="https://github.com/dediggibyte/databricks-updates-agent" style="color:{_ACTION};text-decoration:none;">GitHub repo</a>&nbsp;&nbsp;&middot;&nbsp;&nbsp;<a href="https://docs.databricks.com/aws/en/release-notes/product/" style="color:{_ACTION};text-decoration:none;">Release notes</a>
              </div>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def graph_message(subject: str, html_body: str, recipients: list[str]) -> dict:
    """The Microsoft Graph sendMail request payload."""
    return {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [
                {"emailAddress": {"address": r.strip()}} for r in recipients if r.strip()
            ],
        },
        "saveToSentItems": False,
    }


def send_via_graph(
    subject: str,
    html_body: str,
    sender: str,
    recipients: list[str],
    tenant_id: str,
    client_id: str,
    client_secret: str,
) -> None:
    """Send the digest as ``sender`` via Microsoft Graph client credentials."""
    token_req = urllib.request.Request(
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
        data=urllib.parse.urlencode(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            }
        ).encode(),
        method="POST",
    )
    with urllib.request.urlopen(token_req, timeout=30) as resp:  # noqa: S310
        token = json.loads(resp.read())["access_token"]

    send_req = urllib.request.Request(
        f"https://graph.microsoft.com/v1.0/users/{urllib.parse.quote(sender)}/sendMail",
        data=json.dumps(graph_message(subject, html_body, recipients)).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(send_req, timeout=30) as resp:  # noqa: S310
        # Graph returns 202 Accepted with an empty body on success.
        print(f"email-send: sent as {sender} to {', '.join(recipients)} (HTTP {resp.status})")


def write_email(
    onepagers: list[OnePager],
    days: int,
    site_url: str,
    out: str,
    subject_out: str,
    month: Optional[str] = None,
) -> int:
    """Write the HTML body and subject files; return the item count.

    ``month`` (``YYYY-MM``) switches from the rolling ``days`` window to a
    calendar-month digest; ``days=1`` produces the compact daily digest.
    """
    items = month_onepagers(onepagers, month) if month else recent_onepagers(onepagers, days)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_html(items, site_url, days, month=month), encoding="utf-8")
    subject_path = Path(subject_out)
    subject_path.parent.mkdir(parents=True, exist_ok=True)
    subject_path.write_text(build_subject(items, month=month, days=days) + "\n", encoding="utf-8")
    window = month_label(month) if month else ("today" if days == 1 else f"last {days} day(s)")
    print(f"email-summary: {len(items)} item(s) in {window} -> {out}")
    return len(items)
