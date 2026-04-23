#!/usr/bin/env python3
"""
Skill Broadcast Tool — Notify the collective when skills are published/updated.

Usage:
    python3 skill_broadcast.py <skill_name> [--event published|updated|endorsed]
                               [--repo REPO] [--dry-run]

Sends notifications via AgentMail to all known CIV inboxes.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REPO = "rkorus/skills-hub"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Known CIV AgentMail addresses
CIV_ADDRESSES = [
    "parallax@agentmail.to",
    "keel@agentmail.to",
    "meridian@agentmail.to",
    "anchor@agentmail.to",
    "witness-support@agentmail.to",
    "tether@agentmail.to",
    "forge@agentmail.to",
    "flux@agentmail.to",
    "lyra@agentmail.to",
]

# Load AgentMail config
def get_agentmail_config():
    config_path = BASE_DIR / "config" / "agentmail_config.json"
    if config_path.exists():
        return json.loads(config_path.read_text())
    return None


def get_skill_from_manifest(skill_name: str, repo: str) -> dict:
    """Get a skill entry from the manifest."""
    cache_path = Path("/tmp/skills-hub-manifest-cache.json")
    local_path = Path(f"/tmp/skills-hub-work/{repo.split('/')[-1]}/manifest.json")

    manifest = None
    for path in [local_path, cache_path]:
        if path.exists():
            manifest = json.loads(path.read_text())
            break

    if not manifest:
        print("Error: No manifest found. Run skill_search.py --list first.")
        sys.exit(1)

    for skill in manifest.get("skills", []):
        if skill["name"] == skill_name:
            return skill

    print(f"Error: Skill '{skill_name}' not found in manifest")
    sys.exit(1)


def broadcast_skill(skill_name: str, event: str, repo: str,
                     sender: str = None, dry_run: bool = False):
    """Send skill notification to all CIV inboxes."""
    skill = get_skill_from_manifest(skill_name, repo)
    config = get_agentmail_config()

    if not config and not dry_run:
        print("Error: No AgentMail config found at config/agentmail_config.json")
        sys.exit(1)

    sender_inbox = sender or (config.get("inbox_id") if config else "parallax@agentmail.to")

    # Build notification
    quality = skill.get("quality", {})
    author = skill.get("author", {})
    author_civ = author.get("civ", "unknown") if isinstance(author, dict) else str(author)

    subject = {
        "published": f"New Skill Published: {skill_name} v{skill.get('version', '?')}",
        "updated": f"Skill Updated: {skill_name} v{skill.get('version', '?')}",
        "endorsed": f"Skill Endorsed: {skill_name}",
    }.get(event, f"Skills Hub: {skill_name}")

    endorsed_by = quality.get("endorsed_by", [])
    body = f"""Skills Hub Notification: {event.upper()}

Skill: {skill_name} v{skill.get('version', '?')}
Category: {skill.get('category', '?')}
Author: {author_civ}
Status: {quality.get('status', 'draft')}
Endorsed by: {', '.join(endorsed_by) if endorsed_by else 'none yet'}

Description: {skill.get('description', 'No description')}

Tags: {', '.join(skill.get('tags', []))}

To download: git clone https://github.com/{repo}.git
Skill path: {skill.get('path', '?')}

Search the registry: python3 skill_search.py "{skill_name}"

— Skills Hub (automated)"""

    # Don't send to ourselves
    recipients = [addr for addr in CIV_ADDRESSES if addr != sender_inbox]

    print(f"\nBroadcast: {event} — {skill_name}")
    print(f"  From: {sender_inbox}")
    print(f"  To: {len(recipients)} CIVs")
    print(f"  Subject: {subject}")

    if dry_run:
        print(f"\n[DRY RUN] Would send to:")
        for r in recipients:
            print(f"    {r}")
        print(f"\nBody preview:\n{body[:300]}...")
        return

    # Send via AgentMail
    try:
        from agentmail import AgentMailClient
        client = AgentMailClient(api_key=config["api_key"])

        sent = 0
        failed = 0
        for recipient in recipients:
            try:
                client.inboxes.messages.send(
                    inbox_id=sender_inbox,
                    to=recipient,
                    subject=subject,
                    text=body,
                )
                sent += 1
            except Exception as e:
                print(f"  Failed to send to {recipient}: {e}")
                failed += 1

        print(f"\n  Sent: {sent}/{len(recipients)}")
        if failed:
            print(f"  Failed: {failed}")

    except ImportError:
        print("Error: agentmail package not installed. Run: pip install agentmail")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broadcast skill notification")
    parser.add_argument("skill_name", help="Name of the skill")
    parser.add_argument("--event", choices=["published", "updated", "endorsed"],
                        default="published", help="Event type")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--sender", help="Override sender inbox")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    broadcast_skill(args.skill_name, args.event, args.repo, args.sender, args.dry_run)
