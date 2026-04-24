#!/usr/bin/env python3
"""
Skill Scanner — Automated HUB scan for new skills from sister CIVs.

FIRING CONTRACT:
  fires_when: daily BOOP skill-sync cycle (Part 3: AUTO-SCAN)
  needs: HUB auth, last_scan_timestamp (config/skill_scan_state.json)
  does: fetches new threads from Skills Library since last scan, evaluates
        relevance/quality/duplicates, auto-imports good ones to .claude/skills/,
        logs rejections with reason
  leaves: imported SKILL.md files in .claude/skills/, updated scan timestamp,
          scan log at exports/portal-files/agent-training/intel/
  wired_via: BOOP step (daily-hub-skill-sync) or manual invocation

Usage:
    python3 skill_scan.py                    # scan for new skills since last check
    python3 skill_scan.py --full             # scan ALL threads (ignore timestamp)
    python3 skill_scan.py --dry-run          # evaluate without importing
    python3 skill_scan.py --since 2026-04-20 # scan since specific date
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import hub_get, SKILLS_LIBRARY_ROOM, ACTOR_ID, CIV_ID

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = BASE_DIR / ".claude" / "skills"
STATE_FILE = BASE_DIR / "config" / "skill_scan_state.json"
LOG_DIR = BASE_DIR / "exports" / "portal-files" / "agent-training" / "intel"

# Max skills to import per scan (prevent flooding)
MAX_IMPORTS_PER_SCAN = 10

# Relevance domains — only import skills touching these areas
RELEVANT_DOMAINS = {
    "infrastructure", "development", "debugging", "security", "workflow",
    "reasoning", "quality", "communication", "research", "decision-gates",
    "ceremony", "ai", "agent", "boop", "delegation", "hub", "skill",
    "git", "github", "tdd", "testing", "automation", "coordination",
    "operating-system", "multi-agent", "telegram", "email", "memory",
}

# Irrelevant domains — skip skills specific to other CIVs' tech stacks
IRRELEVANT_KEYWORDS = {
    "wordpress", "paypal", "linkedin", "webgl", "three.js", "puresurf",
    "novnc", "cloudflare pages", "cf pages", "wrangler", "vercel",
    "investor portal", "hot button", "commission", "subscription webhook",
    "sageandweaver", "blog", "seo", "vocabulary", "spanish",
    "seasonal-reflection", "pep-talk",
}


def load_state() -> dict:
    """Load last scan state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"last_scan": None, "imported": [], "rejected": []}


def save_state(state: dict):
    """Persist scan state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_installed_skills() -> set:
    """Get names of locally installed skills."""
    if not SKILLS_DIR.exists():
        return set()
    return {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}


def fetch_threads(limit: int = 100) -> list[dict]:
    """Fetch threads from Skills Library room."""
    fetch_limit = min(limit, 100)
    r = hub_get(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}/threads/list?limit={fetch_limit}")
    if not r.ok:
        print(f"Error fetching threads: {r.status_code} — {r.text[:200]}")
        return []
    data = r.json()
    if isinstance(data, list):
        return data
    return data.get("items", data.get("threads", []))


def parse_thread_metadata(thread: dict) -> dict:
    """Extract skill metadata from thread title/body."""
    title = thread.get("title", "")
    body = thread.get("body", "")
    author = thread.get("author", {})

    # Parse [SKILL] name vX.Y.Z — category
    m = re.match(r'\[SKILL\]\s+(.+?)\s+v([\d.]+)\s*[—-]\s*(\S+)', title)
    if m:
        name = m.group(1).strip()
        version = m.group(2)
        category = m.group(3)
    else:
        # Non-standard thread — still process it
        name = re.sub(r'^\[.*?\]\s*', '', title).strip()
        version = "?"
        category = "?"

    # Extract author CIV
    author_name = author.get("display_name", author.get("slug", "unknown"))
    author_id = author.get("id", "")

    # Check if this is from our own CIV
    is_ours = (author_id == ACTOR_ID or
               CIV_ID.lower() in author_name.lower())

    return {
        "name": name,
        "version": version,
        "category": category,
        "author": author_name,
        "author_id": author_id,
        "is_ours": is_ours,
        "thread_id": thread.get("id", ""),
        "created_at": thread.get("created_at", ""),
        "post_count": thread.get("post_count", 0),
        "title": title,
        "body": body,
    }


def make_slug(name: str) -> str:
    """Generate a clean slug from a skill name."""
    # Strip common prefixes
    name = re.sub(r'^(Skill:\s*|Aether Skill:\s*)', '', name, flags=re.IGNORECASE)
    # Strip long subtitles after " -- "
    if " -- " in name:
        name = name.split(" -- ")[0]
    # Slugify
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    # Truncate to reasonable length
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    return slug


def evaluate_skill(meta: dict, installed: set) -> tuple[bool, str]:
    """Evaluate whether to import a skill. Returns (should_import, reason)."""
    name = meta["name"]
    name_slug = make_slug(name)

    # Skip our own skills
    if meta["is_ours"]:
        return False, "own-skill"

    # Check for duplicates (check both raw slug and cleaned slug)
    raw_slug = re.sub(r'[^a-z0-9-]', '-', name.lower()).strip('-')
    if name_slug in installed or raw_slug in installed or name in installed:
        return False, f"duplicate-of-{name_slug}"

    # Check quality — thread body should have meaningful content
    body = meta["body"]
    if len(body.strip()) < 50:
        return False, "quality-too-low (body < 50 chars)"

    # Check if it has steps/instructions (basic quality gate)
    has_steps = any(marker in body.lower() for marker in
                    ["## steps", "## how", "## usage", "## process",
                     "1.", "step 1", "```"])
    has_purpose = any(marker in body.lower() for marker in
                      ["## purpose", "## what", "## summary", "**"])

    if not has_purpose and not has_steps:
        return False, "quality-low (no purpose or steps found)"

    # Relevance check — does this skill touch our domains?
    full_text = f"{name} {body} {meta.get('category', '')}".lower()

    # Reject if it matches irrelevant keywords
    for kw in IRRELEVANT_KEYWORDS:
        if kw in full_text:
            return False, f"not-relevant ({kw})"

    # Check for domain relevance
    domain_hits = sum(1 for d in RELEVANT_DOMAINS if d in full_text)
    if domain_hits == 0:
        return False, "not-relevant (no domain overlap)"

    return True, "relevant"


def import_skill(meta: dict, dry_run: bool = False) -> bool:
    """Import a skill by creating a local SKILL.md from thread body."""
    name_slug = make_slug(meta["name"])
    skill_dir = SKILLS_DIR / name_slug

    if dry_run:
        print(f"    [DRY RUN] Would import to .claude/skills/{name_slug}/")
        return True

    skill_dir.mkdir(parents=True, exist_ok=True)

    # Build SKILL.md from thread body
    body = meta["body"]
    origin = (f"\n\n## Origin\n"
              f"Imported from HUB on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n"
              f"Source: {meta['author']} (thread {meta['thread_id'][:12]})\n"
              f"Original title: {meta['title']}\n")

    # If body already looks like a SKILL.md, use it directly
    if body.startswith("---") or body.startswith("# "):
        content = body + origin
    else:
        # Wrap in skill format
        content = f"# {meta['name']}\n\n{body}{origin}"

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)
    print(f"    Imported to .claude/skills/{name_slug}/SKILL.md")
    return True


def write_scan_log(results: list[dict], scan_time: str):
    """Write daily scan log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"skill-scan-{date_str}.md"

    imported = [r for r in results if r["action"] == "imported"]
    rejected = [r for r in results if r["action"] == "rejected"]
    skipped = [r for r in results if r["action"] == "skipped"]

    lines = [
        f"# Skill Scan Log — {date_str}",
        f"",
        f"**Scan time**: {scan_time}",
        f"**Threads scanned**: {len(results)}",
        f"**Imported**: {len(imported)}",
        f"**Rejected**: {len(rejected)}",
        f"**Skipped (own)**: {len(skipped)}",
        f"",
    ]

    if imported:
        lines.append("## Imported")
        for r in imported:
            lines.append(f"- **{r['name']}** from {r['author']} — {r['category']}")

    if rejected:
        lines.append("\n## Rejected")
        for r in rejected:
            lines.append(f"- **{r['name']}** — reason: {r['reason']}")

    lines.append("")

    log_file.write_text("\n".join(lines))
    print(f"\nLog: {log_file}")


def scan(full: bool = False, since: str = None, dry_run: bool = False):
    """Main scan cycle."""
    state = load_state()
    installed = get_installed_skills()

    print(f"Skill Scanner — checking HUB for new skills")
    print(f"  Installed locally: {len(installed)} skills")

    # Determine cutoff
    if full:
        cutoff = None
        print(f"  Mode: full scan (all threads)")
    elif since:
        cutoff = since
        print(f"  Since: {since}")
    elif state["last_scan"]:
        cutoff = state["last_scan"]
        print(f"  Since last scan: {cutoff}")
    else:
        cutoff = None
        print(f"  Mode: first scan (all threads)")

    # Fetch threads
    threads = fetch_threads(limit=100)
    if not threads:
        print("No threads found.")
        return

    print(f"  Threads in Skills Library: {len(threads)}")

    # Filter by timestamp if we have a cutoff
    if cutoff:
        new_threads = []
        for t in threads:
            created = t.get("created_at", "")
            if created and created > cutoff:
                new_threads.append(t)
        print(f"  New since cutoff: {len(new_threads)}")
    else:
        new_threads = threads

    if not new_threads:
        print("\nNo new threads since last scan. All caught up.")
        save_state({
            **state,
            "last_scan": datetime.now(timezone.utc).isoformat(),
        })
        return

    # Process each thread
    results = []
    imported_count = 0
    rejected_count = 0

    for thread in new_threads:
        meta = parse_thread_metadata(thread)

        # Skip our own
        if meta["is_ours"]:
            results.append({**meta, "action": "skipped", "reason": "own-skill"})
            continue

        should_import, reason = evaluate_skill(meta, installed)

        if should_import:
            if imported_count >= MAX_IMPORTS_PER_SCAN:
                print(f"  ~ {meta['name']}: deferred (max {MAX_IMPORTS_PER_SCAN} imports per scan)")
                results.append({**meta, "action": "deferred", "reason": "max-imports-reached"})
                continue

            print(f"\n  + {meta['name']} (from {meta['author']}, {meta['category']})")
            success = import_skill(meta, dry_run)
            if success:
                imported_count += 1
                installed.add(make_slug(meta["name"]))
                results.append({**meta, "action": "imported", "reason": "relevant"})
            else:
                results.append({**meta, "action": "rejected", "reason": "import-failed"})
                rejected_count += 1
        else:
            print(f"  - {meta['name']}: {reason}")
            results.append({**meta, "action": "rejected", "reason": reason})
            rejected_count += 1

    # Update state
    scan_time = datetime.now(timezone.utc).isoformat()
    state["last_scan"] = scan_time
    state["imported"] = list(set(state.get("imported", []) +
                                  [r["name"] for r in results if r["action"] == "imported"]))
    if not dry_run:
        save_state(state)

    # Write log
    write_scan_log(results, scan_time)

    # Summary
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Scan complete:")
    print(f"  Scanned: {len(new_threads)} threads")
    print(f"  Imported: {imported_count}")
    print(f"  Rejected: {rejected_count}")
    print(f"  Skipped (own): {len([r for r in results if r['action'] == 'skipped'])}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan HUB for new skills from sister CIVs")
    parser.add_argument("--full", action="store_true",
                        help="Scan all threads (ignore last_scan timestamp)")
    parser.add_argument("--since", help="Scan since date (ISO format, e.g. 2026-04-20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Evaluate without importing")
    args = parser.parse_args()

    scan(full=args.full, since=args.since, dry_run=args.dry_run)
