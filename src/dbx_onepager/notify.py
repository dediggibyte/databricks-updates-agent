"""Build and send the weekly HTML email digest from stored one-pagers.

Selects one-pagers whose note date (the ``YYYY-MM-DD`` prefix of ``note_id``,
the same convention ``render._sort_key`` relies on) falls within the last N
days and emits a self-contained HTML body plus a subject line. Consumed by
``.github/workflows/notify.yml`` after every weekly pipeline run — including
"no updates this week" runs.

Delivery is Microsoft Graph ``sendMail`` with OAuth client credentials —
Exchange Online retired basic (username/password) SMTP auth in April 2026,
so an Entra app registration with the ``Mail.Send`` application permission
is the supported way to send from a Microsoft 365 mailbox.

Email clients ignore external stylesheets, so the markup uses inline styles
and concrete colors instead of the site's CSS design tokens.
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

# Maturity → badge color (mirrors render.STATUS_COLOR, but as plain hex).
_STATUS_HEX = {
    "ga": "#16a34a",
    "public-preview": "#2563eb",
    "gated-preview": "#7c3aed",
    "beta": "#d97706",
    "eol": "#dc2626",
    "changed": "#64748b",
}


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
    items: list[OnePager], today: Optional[date] = None, month: Optional[str] = None
) -> str:
    n = len(items)
    if month:
        label = month_label(month)
        if not items:
            return f"Databricks updates — no release notes in {label} (monthly digest)"
        return f"Databricks updates — {label} monthly digest ({n} release note{'s' if n != 1 else ''})"
    stamp = (today or date.today()).strftime("%b %d, %Y")
    if not items:
        return f"Databricks updates — no new release notes ({stamp})"
    return f"Databricks updates — {n} new release note{'s' if n != 1 else ''} ({stamp})"


def _item_html(op: OnePager, site_url: str) -> str:
    color = _STATUS_HEX.get(op.status, _STATUS_HEX["changed"])
    link = f"{site_url}/onepagers/{op.note_id}.html"
    return f"""\
      <tr>
        <td style="padding:14px 18px;border-bottom:1px solid #e2e8f0;">
          <a href="{html.escape(link)}"
             style="font-size:16px;font-weight:600;color:#0f172a;text-decoration:none;">
            {html.escape(op.product)}</a>
          <span style="display:inline-block;margin-left:8px;padding:2px 8px;border-radius:10px;
                       font-size:11px;font-weight:600;color:#ffffff;background:{color};
                       vertical-align:middle;">{html.escape(op.status_label)}</span>
          <div style="font-size:12px;color:#64748b;margin-top:2px;">{html.escape(op.updated)}</div>
          <div style="font-size:14px;color:#334155;margin-top:6px;line-height:1.5;">
            {html.escape(op.tagline)}</div>
          <div style="margin-top:6px;">
            <a href="{html.escape(link)}" style="font-size:13px;color:#2563eb;">Read the one-pager →</a>
          </div>
        </td>
      </tr>"""


def build_html(
    items: list[OnePager], site_url: str, days: int, month: Optional[str] = None
) -> str:
    site_url = site_url.rstrip("/")
    period = month_label(month) if month else f"the last {days} days"
    if items:
        n = len(items)
        intro = f"{n} Databricks platform update{'s' if n != 1 else ''} in {period}."
        rows = "\n".join(_item_html(op, site_url) for op in items)
    else:
        intro = f"No Databricks platform updates in {period}."
        rows = (
            '      <tr><td style="padding:18px;font-size:14px;color:#64748b;">'
            "Nothing new this period — the gallery below has every past update."
            "</td></tr>"
        )
    return f"""\
<html>
<body style="margin:0;padding:24px;background:#f1f5f9;
             font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:12px;
                border:1px solid #e2e8f0;overflow:hidden;">
    <tr>
      <td style="padding:22px 18px;background:#0f172a;">
        <div style="font-size:18px;font-weight:700;color:#ffffff;">Databricks Update One-Pagers</div>
        <div style="font-size:13px;color:#cbd5e1;margin-top:4px;">{html.escape(intro)}</div>
      </td>
    </tr>
{rows}
    <tr>
      <td style="padding:18px;background:#f8fafc;">
        <a href="{html.escape(site_url)}/"
           style="font-size:14px;font-weight:600;color:#2563eb;">Browse all one-pagers →</a>
        <div style="font-size:11px;color:#94a3b8;margin-top:8px;">
          Sent automatically by the Databricks Updates Agent after its weekly refresh.
        </div>
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
    calendar-month digest.
    """
    items = month_onepagers(onepagers, month) if month else recent_onepagers(onepagers, days)
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_html(items, site_url, days, month=month), encoding="utf-8")
    subject_path = Path(subject_out)
    subject_path.parent.mkdir(parents=True, exist_ok=True)
    subject_path.write_text(build_subject(items, month=month) + "\n", encoding="utf-8")
    window = month_label(month) if month else f"last {days} day(s)"
    print(f"email-summary: {len(items)} item(s) in {window} -> {out}")
    return len(items)
