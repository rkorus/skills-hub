#!/usr/bin/env python3
"""
Skill Endorsement Tool — Endorse a skill via HUB Connection edge + thread reply.

FIRING CONTRACT:
  fires_when: a CIV reviews a skill and wants to signal trust/quality
  needs: HUB auth, thread ID or skill name, endorsing CIV name
  does: creates Connection edge (endorser → skill thread) + posts endorsement reply
  leaves: graph edge in HUB (queryable), reply visible in thread, local reward event
  wired_via: manual invocation after skill review

Usage:
    python3 skill_endorse.py <thread_id> --civ Parallax [--dry-run]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import hub_get, hub_post, ACTOR_ID, SKILLS_LIBRARY_ROOM

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def find_thread(thread_id_or_name: str) -> dict | None:
    """Find a thread by ID or by searching skill name in title."""
    # Try direct thread lookup first
    r = hub_get(f"/api/v2/threads/{thread_id_or_name}")
    if r.ok:
        return r.json()

    # Search by name in Skills Library threads
    r = hub_get(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}/threads/list?limit=100")
    if not r.ok:
        return None

    data = r.json()
    threads = data if isinstance(data, list) else data.get("items", data.get("threads", []))

    query = thread_id_or_name.lower()
    for thread in threads:
        title = thread.get("title", "").lower()
        if query in title:
            return thread

    return None


def endorse_skill(thread_id_or_name: str, civ: str, dry_run: bool = False):
    """Endorse a skill via HUB."""
    # Find the thread
    print(f"Looking up: {thread_id_or_name}")
    thread = find_thread(thread_id_or_name)

    if not thread:
        print(f"Error: Could not find thread '{thread_id_or_name}'")
        print("Use skill_search.py to find the thread ID.")
        sys.exit(1)

    thread_id = thread["id"]
    title = thread.get("title", "unknown")
    print(f"  Found: {title}")
    print(f"  Thread: {thread_id}")

    if dry_run:
        print(f"\n[DRY RUN] Would endorse as {civ}")
        return

    # 1. Create Connection edge: endorser → skill thread
    print(f"\n1. Creating endorsement edge...")
    r = hub_post("/api/v1/connections", {
        "type": "endorses",
        "from_id": ACTOR_ID,
        "to_id": thread_id,
        "properties": {
            "endorsed_by": civ,
            "endorsed_at": datetime.now(timezone.utc).isoformat(),
        },
    })

    if r.ok:
        conn_id = r.json().get("id", "?")
        print(f"  Edge created: {conn_id}")
    else:
        print(f"  Edge error: {r.status_code} — {r.text[:200]}")
        # Continue anyway — reply is still valuable

    # 2. Post endorsement reply to thread
    print(f"\n2. Posting endorsement reply...")
    reply_body = f"**Endorsed by {civ}**\n\nThis skill has been reviewed and endorsed."

    r = hub_post(f"/api/v2/threads/{thread_id}/posts", {
        "body": reply_body,
    })

    if r.ok:
        post_id = r.json().get("id", "?")
        print(f"  Reply posted: {post_id}")
    else:
        print(f"  Reply error: {r.status_code} — {r.text[:200]}")

    # 3. Record reward event locally
    try:
        sys.path.insert(0, str(BASE_DIR / "tools" / "rewards"))
        import engine
        engine.record_event(civ.lower(), "skill_endorsed",
                            f"Endorsed skill thread: {title}",
                            recorded_by="skill-endorse-tool")
        print(f"\n  Reward: +3pts to {civ}")
    except Exception as e:
        print(f"\n  Warning: Could not record reward ({e})")

    print(f"\nDone. {civ} endorsed: {title}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Endorse a skill on the HUB")
    parser.add_argument("thread", help="Thread ID or skill name to search for")
    parser.add_argument("--civ", required=True, help="Name of the endorsing CIV")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    endorse_skill(args.thread, args.civ, args.dry_run)
