#!/usr/bin/env python3
"""
Skill Endorsement Tool — Endorse a skill in the registry.

Usage:
    python3 skill_endorse.py <skill_name> --civ Parallax [--repo REPO] [--dry-run]

What it does:
1. Adds the endorsing CIV to quality.endorsed_by
2. If first endorsement, publishes the skill (draft → published)
3. Records reward event (skill_endorsed: 3pts to endorsing CIV)
4. Commits and pushes to registry
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REPO = "rkorus/skills-hub"
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def clone_or_update(repo: str) -> str:
    """Clone or update the registry repo."""
    work_dir = "/tmp/skills-hub-work"
    os.makedirs(work_dir, exist_ok=True)
    repo_dir = os.path.join(work_dir, repo.split("/")[-1])

    if os.path.exists(repo_dir):
        subprocess.run(["git", "pull", "--rebase"], cwd=repo_dir,
                        check=True, capture_output=True)
    else:
        subprocess.run(
            ["git", "clone", f"https://github.com/{repo}.git", repo_dir],
            check=True, capture_output=True
        )
    return repo_dir


def endorse_skill(skill_name: str, civ: str, repo: str, dry_run: bool = False):
    """Endorse a skill in the registry."""
    repo_dir = clone_or_update(repo)
    manifest_path = os.path.join(repo_dir, "manifest.json")
    manifest = json.loads(Path(manifest_path).read_text())

    # Find the skill
    skill = None
    skill_idx = None
    for i, s in enumerate(manifest.get("skills", [])):
        if s["name"] == skill_name:
            skill = s
            skill_idx = i
            break

    if skill is None:
        print(f"Error: Skill '{skill_name}' not found in registry")
        print(f"Available: {', '.join(s['name'] for s in manifest.get('skills', []))}")
        sys.exit(1)

    quality = skill.get("quality", {})
    endorsed_by = quality.get("endorsed_by", [])

    if civ in endorsed_by:
        print(f"{civ} has already endorsed '{skill_name}'")
        return

    # Add endorsement
    endorsed_by.append(civ)
    quality["endorsed_by"] = endorsed_by

    # Auto-publish on first endorsement
    was_draft = quality.get("status") == "draft"
    if was_draft and len(endorsed_by) >= 1:
        quality["status"] = "published"
        print(f"  Status: draft → published (first endorsement)")

    skill["quality"] = quality
    skill["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    manifest["skills"][skill_idx] = skill
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()

    print(f"\nEndorsement: {civ} → {skill_name}")
    print(f"  Endorsed by: {', '.join(endorsed_by)}")
    print(f"  Status: {quality['status']}")

    if dry_run:
        print("\n[DRY RUN] No changes written.")
        return

    # Write manifest
    Path(manifest_path).write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n"
    )

    # Commit and push
    subprocess.run(["git", "add", "manifest.json"], cwd=repo_dir,
                    check=True, capture_output=True)
    commit_msg = f"endorse: {civ} endorses {skill_name}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir,
                    check=True, capture_output=True)
    subprocess.run(["git", "push"], cwd=repo_dir,
                    check=True, capture_output=True)
    print(f"Pushed to {repo}")

    # Record reward event
    try:
        sys.path.insert(0, str(BASE_DIR / "tools" / "rewards"))
        import engine
        engine.record_event(civ.lower(), "skill_endorsed",
                            f"Endorsed skill: {skill_name}",
                            recorded_by="skill-endorse-tool")
        print(f"  Reward: +3pts to {civ}")
    except Exception as e:
        print(f"  Warning: Could not record reward ({e})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Endorse a skill in the registry")
    parser.add_argument("skill_name", help="Name of the skill to endorse")
    parser.add_argument("--civ", required=True, help="Name of the endorsing CIV")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    endorse_skill(args.skill_name, args.civ, args.repo, args.dry_run)
