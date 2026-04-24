#!/usr/bin/env python3
"""
Skill Distribution Tool — Route skill suggestions to the right AI partner.

FIRING CONTRACT:
  fires_when: daily BOOP skill-sync cycle (Part 5: AUTO-DISTRIBUTE)
  needs: skill_suggestions.json (from skill_suggest.py), AgentMail config
  does: reads pending suggestions, routes each to the AI partner who benefits
        most via AgentMail, logs distribution
  leaves: emails sent to target AI partners, distribution log, cleared suggestions
  wired_via: BOOP step (daily-hub-skill-sync) or manual invocation

Usage:
    python3 skill_distribute.py                  # distribute all pending suggestions
    python3 skill_distribute.py --dry-run        # preview without sending
    python3 skill_distribute.py --to Keel        # send only to specific person
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUGGESTIONS_FILE = BASE_DIR / "config" / "skill_suggestions.json"
AGENTMAIL_CONFIG = BASE_DIR / "config" / "agentmail_config.json"
LOG_DIR = BASE_DIR / "exports" / "portal-files" / "agent-training" / "intel"

# Distribution roster — maps names to AgentMail addresses
DISTRIBUTION_MAP = {
    "Parallax": "parallax@agentmail.to",
    "Keel": "keel@agentmail.to",
    # Add other AI partners as they join:
    # "Aether": "aether@agentmail.to",
    # "Verity": "verity@agentmail.to",
}

# Russell gets Telegram, not AgentMail
TELEGRAM_RECIPIENTS = {"Russell"}

FROM_ADDRESS = "parallax@agentmail.to"


def load_agentmail_key() -> str:
    """Load AgentMail API key from config."""
    if not AGENTMAIL_CONFIG.exists():
        print(f"Error: AgentMail config not found at {AGENTMAIL_CONFIG}")
        sys.exit(1)
    config = json.loads(AGENTMAIL_CONFIG.read_text())
    return config.get("api_key", "")


def load_suggestions() -> list[dict]:
    """Load pending suggestions from skill_suggest.py output."""
    if not SUGGESTIONS_FILE.exists():
        print("No suggestions file found. Run skill_suggest.py first.")
        return []

    try:
        data = json.loads(SUGGESTIONS_FILE.read_text())
        return data.get("suggestions", [])
    except json.JSONDecodeError:
        print("Error reading suggestions file.")
        return []


def send_agentmail(api_key: str, to: str, subject: str, body: str,
                   dry_run: bool = False) -> bool:
    """Send an email via AgentMail API."""
    if dry_run:
        print(f"    [DRY RUN] Would send to {to}: {subject}")
        return True

    import requests
    r = requests.post(
        "https://api.agentmail.to/api/v0/emails",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "from": FROM_ADDRESS,
            "to": [to],
            "subject": subject,
            "body_text": body,
        },
        timeout=15,
    )

    if r.ok:
        msg_id = r.json().get("message_id", r.json().get("id", "?"))
        print(f"    Sent → {to} (msg: {msg_id})")
        return True
    else:
        print(f"    Error sending to {to}: {r.status_code} — {r.text[:200]}")
        return False


def format_email_body(suggestion: dict) -> str:
    """Format a skill suggestion into an email body."""
    return f"""A skill was matched to your current work by the Intelligence Compounding Engine.

SKILL: {suggestion['skill']}
CATEGORY: {suggestion.get('category', '?')}
SOURCE: {suggestion.get('source', '?')}
IMPACT: {suggestion.get('impact', '?')}

WHAT IT DOES:
{suggestion.get('purpose', 'No description available.')}

WHY THIS MATTERS FOR YOU:
This skill was matched to your domain ({suggestion.get('their_role', 'your role')}) based on current goals and active work. Review it and apply if relevant.

ACTION:
- If useful: apply it today and log the outcome
- If not relevant: no action needed

— Intelligence Compounding Engine (Parallax)"""


def distribute(target: str = None, dry_run: bool = False):
    """Main distribution cycle."""
    suggestions = load_suggestions()
    if not suggestions:
        return

    print(f"Skill Distribution — {len(suggestions)} suggestions to route")

    api_key = load_agentmail_key()
    sent_count = 0
    skip_count = 0
    fail_count = 0
    results = []

    for i, s in enumerate(suggestions, 1):
        recipient = s.get("who_benefits", "")

        # Filter by target if specified
        if target and recipient.lower() != target.lower():
            continue

        print(f"\n  {i}. {s['skill']} → {recipient} ({s.get('impact', '?')} impact)")

        # Skip Telegram-only recipients (Russell)
        if recipient in TELEGRAM_RECIPIENTS:
            print(f"    Skipped: {recipient} receives via Telegram (not AgentMail)")
            results.append({**s, "status": "skipped", "reason": "telegram-only"})
            skip_count += 1
            continue

        # Get email address
        email = DISTRIBUTION_MAP.get(recipient)
        if not email:
            print(f"    Skipped: no AgentMail address for {recipient}")
            results.append({**s, "status": "skipped", "reason": "no-email"})
            skip_count += 1
            continue

        # Don't send to ourselves
        if email == FROM_ADDRESS:
            print(f"    Skipped: self (would send to ourselves)")
            results.append({**s, "status": "skipped", "reason": "self"})
            skip_count += 1
            continue

        subject = f"SKILL SUGGESTION: {s['skill']} for your {s.get('category', 'work')}"
        body = format_email_body(s)

        success = send_agentmail(api_key, email, subject, body, dry_run)
        if success:
            sent_count += 1
            results.append({**s, "status": "sent", "to": email})
        else:
            fail_count += 1
            results.append({**s, "status": "failed", "to": email})

    # Write distribution log
    if not dry_run:
        write_distribution_log(results)

    # Summary
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Distribution complete:")
    print(f"  Sent: {sent_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Failed: {fail_count}")

    return results


def write_distribution_log(results: list[dict]):
    """Write daily distribution log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"skill-distribute-{date_str}.md"

    sent = [r for r in results if r["status"] == "sent"]
    skipped = [r for r in results if r["status"] == "skipped"]
    failed = [r for r in results if r["status"] == "failed"]

    lines = [
        f"# Skill Distribution Log — {date_str}",
        f"",
        f"**Time**: {datetime.now(timezone.utc).isoformat()}",
        f"**Sent**: {len(sent)}",
        f"**Skipped**: {len(skipped)}",
        f"**Failed**: {len(failed)}",
        f"",
    ]

    if sent:
        lines.append("## Sent")
        for r in sent:
            lines.append(f"- **{r['skill']}** → {r.get('to', '?')} ({r.get('impact', '?')})")

    if skipped:
        lines.append("\n## Skipped")
        for r in skipped:
            lines.append(f"- **{r['skill']}** → {r.get('who_benefits', '?')}: {r.get('reason', '?')}")

    if failed:
        lines.append("\n## Failed")
        for r in failed:
            lines.append(f"- **{r['skill']}** → {r.get('to', '?')}")

    lines.append("")
    log_file.write_text("\n".join(lines))
    print(f"\nLog: {log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distribute skill suggestions to AI partners")
    parser.add_argument("--to", help="Send only to specific person")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without sending")
    args = parser.parse_args()

    distribute(target=args.to, dry_run=args.dry_run)
