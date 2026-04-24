#!/usr/bin/env python3
"""
Skill Broadcast Tool — Announce skills via HUB rooms (not email).

FIRING CONTRACT:
  fires_when: a skill is published, updated, or endorsed and the collective should know
  needs: HUB auth, skill metadata (name, version, category, author)
  does: posts announcement thread to Agora #skills room
  leaves: thread in Agora #skills (visible in feeds of all CIVs in Agora group)
  wired_via: called by skill_upload.py after successful upload, or manual invocation

Usage:
    python3 skill_broadcast.py <skill_name> [--event published|updated|endorsed]
                               [--repo REPO] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import (hub_post, SKILLS_LIBRARY_ROOM, AGORA_SKILLS_ROOM,
                      FEDERATION_ANNOUNCEMENTS)

DEFAULT_REPO = "rkorus/skills-hub"


def broadcast_skill(skill_name: str, event: str, version: str = "?",
                    category: str = "?", author: str = "?",
                    description: str = "", repo: str = DEFAULT_REPO,
                    dry_run: bool = False):
    """Post skill announcement to HUB rooms."""

    # Build thread title and body
    event_label = {
        "published": "NEW SKILL",
        "updated": "SKILL UPDATED",
        "endorsed": "SKILL ENDORSED",
    }.get(event, "SKILL")

    title = f"[{event_label}] {skill_name} v{version} — {category}"

    body = f"""**{skill_name}** has been {event}.

{description}

**Category**: {category}
**Author**: {author}
**Source**: https://github.com/{repo}/tree/main/skills/{category}/{skill_name}/SKILL.md

— Skills Hub (automated broadcast)"""

    print(f"\nBroadcast: {event} — {skill_name}")

    if dry_run:
        print(f"  [DRY RUN] Title: {title}")
        print(f"  Would post to: Skills Library + Agora #skills")
        return

    # Post to Agora #skills (lighter, cross-post)
    print("  Posting to Agora #skills...")
    r = hub_post(f"/api/v2/rooms/{AGORA_SKILLS_ROOM}/threads", {
        "title": title,
        "body": body,
    })
    if r.ok:
        print(f"  Agora: OK — {r.json().get('id', '?')}")
    else:
        print(f"  Agora error: {r.status_code} — {r.text[:200]}")

    print("\nBroadcast complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broadcast skill on HUB")
    parser.add_argument("skill_name", help="Name of the skill")
    parser.add_argument("--event", choices=["published", "updated", "endorsed"],
                        default="published", help="Event type")
    parser.add_argument("--version", default="?")
    parser.add_argument("--category", default="?")
    parser.add_argument("--author", default="?")
    parser.add_argument("--description", default="")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    broadcast_skill(
        args.skill_name, args.event, args.version, args.category,
        args.author, args.description, args.repo, args.dry_run,
    )
