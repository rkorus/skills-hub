#!/usr/bin/env python3
"""
Skill Search Tool — Query the skills-hub registry for relevant skills.

Usage:
    python3 skill_search.py <query>                    # keyword search
    python3 skill_search.py --category reasoning       # browse by category
    python3 skill_search.py --list                     # list all skills
    python3 skill_search.py --task "set up telegram bot"  # task-based matching
    python3 skill_search.py --new 7                    # skills added in last N days

Results are ranked by relevance score (keyword match + adoption + usage + rating).
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DEFAULT_REPO = "rkorus/skills-hub"
MANIFEST_URL = "https://raw.githubusercontent.com/{repo}/main/manifest.json"


def fetch_manifest(repo: str) -> dict:
    """Fetch manifest.json from the registry."""
    # Try local cache first
    cache_path = Path("/tmp/skills-hub-manifest-cache.json")
    cache_age_limit = 3600  # 1 hour

    if cache_path.exists():
        age = datetime.now().timestamp() - cache_path.stat().st_mtime
        if age < cache_age_limit:
            return json.loads(cache_path.read_text())

    # Try local clone
    local_path = Path(f"/tmp/skills-hub-work/{repo.split('/')[-1]}/manifest.json")
    if local_path.exists():
        manifest = json.loads(local_path.read_text())
        cache_path.write_text(json.dumps(manifest))
        return manifest

    # Fetch from GitHub
    url = MANIFEST_URL.format(repo=repo)
    try:
        import requests
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            manifest = resp.json()
            cache_path.write_text(json.dumps(manifest))
            return manifest
    except Exception:
        pass

    # Try git clone
    try:
        work_dir = "/tmp/skills-hub-work"
        os.makedirs(work_dir, exist_ok=True)
        repo_dir = os.path.join(work_dir, repo.split("/")[-1])
        if not os.path.exists(repo_dir):
            subprocess.run(
                ["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", repo_dir],
                check=True, capture_output=True
            )
        manifest_file = os.path.join(repo_dir, "manifest.json")
        if os.path.exists(manifest_file):
            manifest = json.loads(Path(manifest_file).read_text())
            cache_path.write_text(json.dumps(manifest))
            return manifest
    except Exception:
        pass

    print(f"Error: Could not fetch manifest from {repo}")
    print("The registry may not exist yet. Create it first.")
    sys.exit(1)


def score_skill(skill: dict, query: str = "", task: str = "") -> float:
    """Score a skill by relevance to query/task + quality signals."""
    score = 0.0

    search_text = query.lower() if query else task.lower()
    if not search_text:
        return score

    words = search_text.split()
    name = skill.get("name", "").lower()
    desc = skill.get("description", "").lower()
    tags = [t.lower() for t in skill.get("tags", [])]
    category = skill.get("category", "").lower()

    # Exact name match
    if search_text in name:
        score += 10.0

    # Word matches in name (highest weight)
    for word in words:
        if word in name:
            score += 5.0

    # Word matches in description
    for word in words:
        if word in desc:
            score += 2.0

    # Tag matches
    for word in words:
        if word in tags:
            score += 3.0
        for tag in tags:
            if word in tag:
                score += 1.5

    # Category match
    for word in words:
        if word in category:
            score += 2.0

    # Quality signals from nested quality block (with flat fallback)
    quality = skill.get("quality", {})
    downloads = quality.get("downloads", skill.get("downloads", 0))
    usage = quality.get("usage_count", skill.get("usage_count", 0))
    rating = quality.get("rating", skill.get("rating", 0.0)) or 0.0
    endorsed_by = quality.get("endorsed_by", [])
    endorsements = len(endorsed_by) if isinstance(endorsed_by, list) else skill.get("endorsements", 0)

    score += min(downloads * 0.1, 2.0)   # cap at 2pts
    score += min(usage * 0.2, 3.0)       # usage weighted higher
    score += rating * 0.5                 # 0-5 scale
    score += min(endorsements * 0.3, 1.5) # endorsed = trusted

    # Published > draft
    status = quality.get("status", skill.get("status", "draft"))
    if status == "published":
        score += 1.0

    return round(score, 2)


def format_skill(skill: dict, score: float = 0.0, verbose: bool = False) -> str:
    """Format a skill entry for display."""
    quality = skill.get("quality", {})
    status = quality.get("status", skill.get("status", "draft"))
    status_icon = {
        "published": "[OK]",
        "draft": "[DRAFT]",
        "unendorsed": "[UNENDORSED]"
    }.get(status, "[?]")

    # Format author (handles both string and nested dict)
    author = skill.get("author", "?")
    if isinstance(author, dict):
        author_str = author.get("civ", "?")
        if author.get("adapted_by"):
            author_str += f" (adapted: {author['adapted_by']})"
    else:
        author_str = str(author)

    line = f"  {status_icon} {skill['name']} v{skill.get('version', '?')}"
    if score > 0:
        line += f" (score: {score})"
    line += f"\n    {skill.get('description', 'No description')[:100]}"
    line += f"\n    Category: {skill.get('category', '?')} | Author: {author_str}"

    if verbose:
        line += f"\n    Tags: {', '.join(skill.get('tags', []))}"
        downloads = quality.get("downloads", skill.get("downloads", 0))
        usage = quality.get("usage_count", skill.get("usage_count", 0))
        rating = quality.get("rating", skill.get("rating", 0))
        endorsed = quality.get("endorsed_by", [])
        line += f"\n    Downloads: {downloads} | Usage: {usage} | Rating: {rating}"
        if endorsed:
            line += f" | Endorsed by: {', '.join(endorsed)}"
        line += f"\n    Path: {skill.get('path', skill.get('file_path', '?'))}"

    return line


def search_skills(manifest: dict, query: str = "", category: str = "",
                   task: str = "", new_days: int = 0, list_all: bool = False,
                   verbose: bool = False, limit: int = 10):
    """Search the manifest and display results."""
    skills = manifest.get("skills", [])

    if not skills:
        print("Registry is empty. No skills uploaded yet.")
        return

    # Filter
    results = skills

    if category:
        results = [s for s in results if s.get("category", "").lower() == category.lower()]

    if new_days > 0:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=new_days)).isoformat()
        results = [s for s in results if s.get("created_at", "") >= cutoff]

    # Score and sort
    if query or task:
        scored = [(s, score_skill(s, query, task)) for s in results]
        scored = [(s, sc) for s, sc in scored if sc > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        results_with_scores = scored[:limit]
    elif list_all:
        results_with_scores = [(s, 0.0) for s in sorted(results, key=lambda x: x.get("name", ""))]
    else:
        results_with_scores = [(s, 0.0) for s in results[:limit]]

    # Display
    total = len(manifest.get("skills", []))
    showing = len(results_with_scores)

    if query:
        print(f"Search: \"{query}\" — {showing} results (of {total} total skills)\n")
    elif task:
        print(f"Task match: \"{task}\" — {showing} results (of {total} total skills)\n")
    elif category:
        print(f"Category: {category} — {showing} results (of {total} total skills)\n")
    elif new_days:
        print(f"New skills (last {new_days} days) — {showing} results (of {total} total skills)\n")
    else:
        print(f"All skills — {showing} listed (of {total} total)\n")

    for skill, score in results_with_scores:
        print(format_skill(skill, score, verbose))
        print()

    # Show categories summary
    if list_all or (not query and not task and not category):
        cats = {}
        for s in manifest.get("skills", []):
            cat = s.get("category", "uncategorized")
            cats[cat] = cats.get(cat, 0) + 1
        print("Categories:")
        for cat, count in sorted(cats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search the skills-hub registry")
    parser.add_argument("query", nargs="?", default="", help="Search keywords")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--task", "-t", help="Task-based matching (natural language)")
    parser.add_argument("--new", type=int, default=0, metavar="DAYS", help="Show skills added in last N days")
    parser.add_argument("--list", "-l", action="store_true", help="List all skills")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed info")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    args = parser.parse_args()

    manifest = fetch_manifest(args.repo)
    search_skills(
        manifest,
        query=args.query,
        category=args.category,
        task=args.task,
        new_days=args.new,
        list_all=args.list,
        verbose=args.verbose,
        limit=args.limit
    )
