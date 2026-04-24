#!/usr/bin/env python3
"""
Skill Search Tool — Search skills via HUB Skills Library room threads.

FIRING CONTRACT:
  fires_when: before building any new skill/capability (hub-search-first obligation)
  needs: HUB auth (hub_auth.py), Skills Library room access
  does: queries HUB Skills Library threads by keyword/category, scores by relevance
  leaves: search results showing existing skills — adopt/fork/build-new decision
  wired_via: constitutional mandate (search hub before building new)

Usage:
    python3 skill_search.py <query>                    # keyword search
    python3 skill_search.py --list                     # list all skills
    python3 skill_search.py --category reasoning       # filter by category
    python3 skill_search.py --limit 20                 # max results
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import hub_get, SKILLS_LIBRARY_ROOM


def fetch_skill_threads(limit: int = 100) -> list[dict]:
    """Fetch threads from Skills Library room on the HUB. Paginates if needed."""
    fetch_limit = min(limit, 100)
    r = hub_get(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}/threads/list?limit={fetch_limit}")
    if not r.ok:
        print(f"Error fetching threads: {r.status_code} — {r.text[:200]}")
        sys.exit(1)

    data = r.json()
    # v2 may return {"items": [...]} or a raw list
    if isinstance(data, list):
        return data
    return data.get("items", data.get("threads", []))


def parse_skill_thread(thread: dict) -> dict:
    """Extract skill metadata from a thread title/body."""
    title = thread.get("title", "")
    body = thread.get("body", thread.get("properties", {}).get("body", ""))
    author_info = thread.get("author", {})

    # Parse [SKILL] prefix format: [SKILL] name vX.Y.Z — category
    skill_match = re.match(r'\[SKILL\]\s+(.+?)\s+v([\d.]+)\s*[—-]\s*(\S+)', title)

    if skill_match:
        name = skill_match.group(1).strip()
        version = skill_match.group(2)
        category = skill_match.group(3)
    else:
        name = title
        version = "?"
        category = "?"

    # Extract tags from body if present
    tags = []
    tag_match = re.search(r'\*\*Tags\*\*:\s*(.+)', body)
    if tag_match:
        tag_str = tag_match.group(1).strip()
        if tag_str != "none":
            tags = [t.strip() for t in tag_str.split(",")]

    # Extract description from body
    desc_lines = [l for l in body.split('\n') if l.strip()
                  and not l.startswith('**') and not l.startswith('```')
                  and not l.startswith('To install') and not l.startswith('—')]
    description = desc_lines[0].strip() if desc_lines else ""

    return {
        "name": name,
        "version": version,
        "category": category,
        "tags": tags,
        "description": description,
        "thread_id": thread.get("id", ""),
        "author": author_info.get("display_name", author_info.get("slug", "?")),
        "created_at": thread.get("created_at", ""),
        "post_count": thread.get("post_count", 0),
        "title": title,
        "body": body,
    }


def score_skill(skill: dict, query: str) -> float:
    """Score a skill by relevance to query."""
    score = 0.0
    words = query.lower().split()
    name = skill["name"].lower()
    desc = skill["description"].lower()
    tags = [t.lower() for t in skill["tags"]]
    category = skill["category"].lower()
    body = skill.get("body", "").lower()

    for word in words:
        if word in name:
            score += 5.0
        if word in desc:
            score += 2.0
        if word in category:
            score += 2.0
        if word in body:
            score += 1.0
        for tag in tags:
            if word in tag:
                score += 3.0

    # Exact name match
    if query.lower() in name:
        score += 10.0

    # Engagement bonus
    score += min(skill.get("post_count", 0) * 0.5, 3.0)

    return round(score, 2)


def format_skill(skill: dict, score: float = 0.0) -> str:
    """Format a skill entry for display."""
    line = f"  {skill['name']} v{skill['version']}"
    if score > 0:
        line += f" (score: {score})"
    line += f"\n    {skill['description'][:120]}"
    line += f"\n    Category: {skill['category']} | Author: {skill['author']}"
    if skill["tags"]:
        line += f"\n    Tags: {', '.join(skill['tags'])}"
    line += f"\n    Thread: {skill['thread_id'][:12]}..."
    return line


def search_skills(query: str = "", category: str = "",
                   list_all: bool = False, limit: int = 20):
    """Search Skills Library room threads."""
    print("Fetching from HUB Skills Library...")
    threads = fetch_skill_threads(limit=200)

    if not threads:
        print("No threads found in Skills Library.")
        return

    # Parse all threads into skill entries
    skills = [parse_skill_thread(t) for t in threads]

    # Filter by category
    if category:
        skills = [s for s in skills if s["category"].lower() == category.lower()]

    # Score and sort
    if query:
        scored = [(s, score_skill(s, query)) for s in skills]
        scored = [(s, sc) for s, sc in scored if sc > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        results = scored[:limit]
    elif list_all:
        results = [(s, 0.0) for s in sorted(skills, key=lambda x: x["name"])]
    else:
        results = [(s, 0.0) for s in skills[:limit]]

    # Display
    total = len(skills)
    showing = len(results)

    if query:
        print(f"\nSearch: \"{query}\" — {showing} results (of {total} skill threads)\n")
    elif category:
        print(f"\nCategory: {category} — {showing} results (of {total} total)\n")
    else:
        print(f"\nAll skills — {showing} listed (of {total} total)\n")

    for skill, score in results:
        print(format_skill(skill, score))
        print()

    # Category summary
    if list_all or (not query and not category):
        cats = {}
        for s in skills:
            cat = s.get("category", "?")
            cats[cat] = cats.get(cat, 0) + 1
        if cats:
            print("Categories:")
            for cat, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search HUB Skills Library")
    parser.add_argument("query", nargs="?", default="", help="Search keywords")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--list", "-l", action="store_true", help="List all skills")
    parser.add_argument("--limit", "-n", type=int, default=20, help="Max results")
    args = parser.parse_args()

    search_skills(
        query=args.query,
        category=args.category,
        list_all=args.list,
        limit=args.limit,
    )
