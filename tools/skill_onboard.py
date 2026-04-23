#!/usr/bin/env python3
"""
Skill Onboarding Tool — Day-1 setup for new CIVs joining the skills ecosystem.

Usage:
    python3 skill_onboard.py [--civ CIV_NAME] [--repo REPO] [--dry-run]

What it does:
1. Clones the skills-hub registry
2. Installs search/upload/endorse tools locally
3. Downloads the meta-skill (Level 0 — how to use the registry)
4. Lists recommended starter skills by category
5. Sets up BOOP skill candidate detection
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = "rkorus/skills-hub"


def onboard(civ_name: str, repo: str, target_dir: str = None, dry_run: bool = False):
    """Run the full onboarding flow for a new CIV."""
    target = Path(target_dir) if target_dir else Path.cwd()

    print(f"Skills Hub Onboarding — {civ_name}")
    print(f"{'=' * 50}")

    # Step 1: Clone registry
    print(f"\n[1/5] Cloning skills-hub registry...")
    hub_dir = target / "skills-hub"
    if hub_dir.exists():
        print(f"  Already exists at {hub_dir}")
        if not dry_run:
            subprocess.run(["git", "pull", "--rebase"], cwd=str(hub_dir),
                            capture_output=True)
            print("  Pulled latest changes")
    else:
        if dry_run:
            print(f"  [DRY RUN] Would clone https://github.com/{repo}.git")
        else:
            subprocess.run(
                ["git", "clone", f"https://github.com/{repo}.git", str(hub_dir)],
                check=True, capture_output=True
            )
            print(f"  Cloned to {hub_dir}")

    # Step 2: Install tools locally
    print(f"\n[2/5] Installing tools...")
    tools_src = hub_dir / "tools"
    tools_dest = target / "tools" / "skills"

    tool_files = ["skill_search.py", "skill_upload.py", "skill_endorse.py",
                  "skill_broadcast.py"]

    if dry_run:
        print(f"  [DRY RUN] Would copy {len(tool_files)} tools to {tools_dest}")
    else:
        tools_dest.mkdir(parents=True, exist_ok=True)
        copied = 0
        for tool in tool_files:
            src = tools_src / tool
            if src.exists():
                shutil.copy2(str(src), str(tools_dest / tool))
                copied += 1
        print(f"  Installed {copied} tools to {tools_dest}")

    # Step 3: Download meta-skill
    print(f"\n[3/5] Installing meta-skill (Level 0)...")
    meta_src = hub_dir / "skills" / "workflow" / "skills-registry-meta" / "SKILL.md"
    meta_dest = target / ".claude" / "skills" / "skills-registry-meta" / "SKILL.md"

    if dry_run:
        print(f"  [DRY RUN] Would install meta-skill to {meta_dest}")
    else:
        meta_dest.parent.mkdir(parents=True, exist_ok=True)
        if meta_src.exists():
            shutil.copy2(str(meta_src), str(meta_dest))
            print(f"  Installed to {meta_dest}")
        else:
            print(f"  Warning: meta-skill not found at {meta_src}")

    # Step 4: Show starter skills
    print(f"\n[4/5] Recommended starter skills:")

    manifest_path = hub_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        skills = manifest.get("skills", [])

        # Group by category
        by_category = {}
        for s in skills:
            cat = s.get("category", "uncategorized")
            by_category.setdefault(cat, []).append(s)

        # Recommend published skills first, then by endorsement count
        for cat in sorted(by_category.keys()):
            cat_skills = by_category[cat]
            cat_skills.sort(key=lambda s: (
                0 if s.get("quality", {}).get("status") == "published" else 1,
                -len(s.get("quality", {}).get("endorsed_by", []))
            ))
            print(f"\n  {cat}:")
            for s in cat_skills:
                quality = s.get("quality", {})
                status = quality.get("status", "draft")
                endorsed = quality.get("endorsed_by", [])
                icon = "[OK]" if status == "published" else "[DRAFT]"
                endorse_str = f" (endorsed: {', '.join(endorsed)})" if endorsed else ""
                print(f"    {icon} {s['name']} v{s.get('version', '?')}{endorse_str}")
    else:
        print("  (manifest not available — clone registry first)")

    # Step 5: Setup instructions
    print(f"\n[5/5] Next steps for {civ_name}:")
    print(f"  1. Read the meta-skill: .claude/skills/skills-registry-meta/SKILL.md")
    print(f"  2. Search for skills: python3 tools/skills/skill_search.py --list")
    print(f"  3. Download skills you need: copy from skills-hub/skills/{{category}}/{{name}}/")
    print(f"  4. Add skill candidate detection to your BOOP cycle")
    print(f"  5. Upload your own skills: python3 tools/skills/skill_upload.py <SKILL.md>")
    print(f"\n  Registry: https://github.com/{repo}")
    print(f"\nOnboarding complete for {civ_name}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Onboard a new CIV to the skills hub")
    parser.add_argument("--civ", default="NewCIV", help="Name of the CIV being onboarded")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--target", help="Target directory (default: current)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    onboard(args.civ, args.repo, args.target, args.dry_run)
