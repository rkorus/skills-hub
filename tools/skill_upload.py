#!/usr/bin/env python3
"""
Skill Upload Tool — Push SKILL.md to GitHub + announce on the HUB.

FIRING CONTRACT:
  fires_when: a new or updated skill needs to be published to the collective
  needs: SKILL.md with YAML frontmatter, GitHub push access, HUB auth
  does: pushes file to GitHub repo + posts announcement thread to Skills Library room
  leaves: SKILL.md in GitHub, thread in HUB Skills Library (searchable, permanent)
  wired_via: manual invocation or BOOP auto-publish (boop_hook.py)

Usage:
    python3 skill_upload.py <path_to_skill.md> [--repo REPO] [--dry-run]

GitHub for files. HUB for coordination.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

# HUB integration
sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import get_hub_headers, HUB_URL, SKILLS_LIBRARY_ROOM, hub_post, hub_get

DEFAULT_REPO = "rkorus/skills-hub"

REQUIRED_FRONTMATTER = ["name", "description"]

VALID_CATEGORIES = [
    "reasoning", "development", "communication", "quality",
    "decision-gates", "debugging", "security", "workflow",
    "ceremony", "content", "infrastructure", "research",
]


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from a SKILL.md file."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        try:
            fm = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
            return fm, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def generate_frontmatter(skill_path: str, body: str) -> dict:
    """Generate stub frontmatter from file name and content."""
    name = Path(skill_path).stem
    if name == "SKILL":
        name = Path(skill_path).parent.name

    lines = [l.strip() for l in body.split('\n') if l.strip() and not l.startswith('#')]
    description = lines[0][:200] if lines else f"Skill: {name}"

    return {
        "name": name,
        "description": description,
        "version": "1.0.0",
        "author": "unknown",
        "category": "uncategorized",
        "tags": [],
    }


def validate_frontmatter(fm: dict) -> list[str]:
    """Validate frontmatter and return list of issues."""
    issues = []
    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field]:
            issues.append(f"Missing required field: {field}")

    if fm.get("category") and fm["category"] not in VALID_CATEGORIES:
        issues.append(f"Unknown category: {fm['category']}. Valid: {', '.join(VALID_CATEGORIES)}")

    if fm.get("tags") and not isinstance(fm["tags"], list):
        issues.append("'tags' should be a list")

    return issues


def push_to_github(skill_path: Path, content: str, fm: dict, repo: str, dry_run: bool) -> bool:
    """Push SKILL.md to GitHub repo. Returns True on success."""
    skill_name = fm["name"]
    category = fm.get("category", "uncategorized")

    if dry_run:
        print(f"  [DRY RUN] Would push: skills/{category}/{skill_name}/SKILL.md")
        return True

    work_dir = "/tmp/skills-hub-work"
    os.makedirs(work_dir, exist_ok=True)
    repo_dir = os.path.join(work_dir, repo.split("/")[-1])

    try:
        if os.path.exists(repo_dir):
            subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir,
                           check=True, capture_output=True)
        else:
            subprocess.run(
                ["git", "clone", f"https://github.com/{repo}.git", repo_dir],
                check=True, capture_output=True
            )
    except subprocess.CalledProcessError as e:
        print(f"  Git error: {e}")
        return False

    # Write skill file (category-based layout)
    skill_dir = os.path.join(repo_dir, "skills", category, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    Path(os.path.join(skill_dir, "SKILL.md")).write_text(content)

    # Commit and push
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)

    commit_msg = f"skill: add {skill_name} v{fm.get('version', '1.0.0')}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_dir, capture_output=True, text=True
    )

    if result.returncode != 0:
        if "nothing to commit" in result.stdout:
            print("  GitHub: no changes (already up to date)")
            return True
        print(f"  Commit error: {result.stderr}")
        return False

    push_result = subprocess.run(
        ["git", "push"], cwd=repo_dir, capture_output=True, text=True
    )

    if push_result.returncode != 0:
        print(f"  Push error: {push_result.stderr}")
        return False

    print(f"  GitHub: pushed to {repo}")
    return True


def post_to_hub(fm: dict, repo: str, dry_run: bool) -> str | None:
    """Post skill announcement thread to Skills Library room. Returns thread ID."""
    skill_name = fm["name"]
    category = fm.get("category", "uncategorized")
    version = fm.get("version", "1.0.0")
    description = fm.get("description", "No description")
    tags = fm.get("tags", [])

    # Format author
    author = fm.get("author", "unknown")
    if isinstance(author, dict):
        author_str = author.get("civ", "unknown")
        if author.get("adapted_by"):
            author_str += f" (adapted by {author['adapted_by']})"
    else:
        author_str = str(author)

    title = f"[SKILL] {skill_name} v{version} — {category}"
    body = f"""**{fm.get('title', skill_name)}**

{description}

**Category**: {category}
**Author**: {author_str}
**Tags**: {', '.join(tags) if tags else 'none'}
**Version**: {version}

**Source**: https://github.com/{repo}/tree/main/skills/{category}/{skill_name}/SKILL.md

To install:
```
git clone https://github.com/{repo}.git
cp -r skills-hub/skills/{category}/{skill_name} .claude/skills/
```

— Parallax (automated via Skills Hub)"""

    if dry_run:
        print(f"  [DRY RUN] Would post thread: {title}")
        return "dry-run"

    try:
        r = hub_post(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}/threads", {
            "title": title,
            "body": body,
        })

        if r.ok:
            thread_id = r.json().get("id")
            print(f"  HUB: thread posted → {thread_id}")
            return thread_id
        else:
            print(f"  HUB error: {r.status_code} — {r.text[:200]}")
            return None
    except Exception as e:
        print(f"  HUB error: {e}")
        return None


def upload_skill(skill_file: str, repo: str, dry_run: bool = False):
    """Main upload flow: GitHub + HUB."""
    skill_path = Path(skill_file).resolve()
    if not skill_path.exists():
        print(f"Error: {skill_path} does not exist")
        sys.exit(1)

    content = skill_path.read_text()
    fm, body = extract_frontmatter(content)

    # Generate frontmatter if missing
    if not fm:
        print("No YAML frontmatter found. Generating stub...")
        fm = generate_frontmatter(str(skill_path), body)
        fm_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        content = f"---\n{fm_yaml}---\n\n{body}"

    # Validate
    issues = validate_frontmatter(fm)
    if issues:
        print("Frontmatter issues:")
        for issue in issues:
            print(f"  - {issue}")
        if any("Missing required" in i for i in issues):
            print("Fix required fields before uploading.")
            sys.exit(1)

    skill_name = fm["name"]
    print(f"\nUploading: {skill_name} v{fm.get('version', '?')}")
    print(f"  Category: {fm.get('category', '?')}")
    print(f"  Tags: {fm.get('tags', [])}")

    # Step 1: Push to GitHub (file storage)
    print("\n1. GitHub (file storage):")
    github_ok = push_to_github(skill_path, content, fm, repo, dry_run)

    # Step 2: Post to HUB (coordination/discovery)
    print("\n2. HUB Skills Library (coordination):")
    thread_id = post_to_hub(fm, repo, dry_run)

    # Summary
    print(f"\nResult:")
    print(f"  GitHub: {'OK' if github_ok else 'FAILED'}")
    print(f"  HUB: {'OK' if thread_id else 'FAILED'} {'(thread: ' + thread_id + ')' if thread_id else ''}")

    return thread_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a skill to GitHub + announce on HUB")
    parser.add_argument("skill_file", help="Path to the SKILL.md file")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--dry-run", action="store_true", help="Validate without uploading")
    args = parser.parse_args()

    upload_skill(args.skill_file, args.repo, args.dry_run)
