#!/usr/bin/env python3
"""
Skill Suggestion Engine — Match skills to current goals, projects, and people.

FIRING CONTRACT:
  fires_when: daily BOOP skill-sync cycle (Part 4: AUTO-SUGGEST)
  needs: HUB auth, local skills inventory, goals context (scratchpad/MEMORY.md)
  does: loads all available skills + current goals/projects, generates specific
        actionable suggestions matching skills to people and work
  leaves: suggestion list (stdout + log file), tagged SKILL-SUGGESTION entries
  wired_via: BOOP step (daily-hub-skill-sync) or manual invocation

Usage:
    python3 skill_suggest.py                         # generate suggestions
    python3 skill_suggest.py --goals-file FILE       # custom goals source
    python3 skill_suggest.py --dry-run               # preview without logging
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from hub_auth import hub_get, SKILLS_LIBRARY_ROOM

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = BASE_DIR / ".claude" / "skills"
LOG_DIR = BASE_DIR / "exports" / "portal-files" / "agent-training" / "intel"
SUGGESTIONS_FILE = BASE_DIR / "config" / "skill_suggestions.json"

# Default goals sources (configurable per CIV)
DEFAULT_GOALS_SOURCES = [
    BASE_DIR / ".claude" / "scratch-pad.md",
    Path.home() / ".claude" / "projects" / "-home-parallax" / "memory" / "MEMORY.md",
]

# Team roster — who benefits from what categories
# This is our equivalent of Aether's team whitelist spreadsheet
TEAM_ROSTER = [
    {
        "name": "Parallax",
        "role": "Primary AI",
        "email": "parallax@agentmail.to",
        "domains": ["infrastructure", "development", "security", "workflow",
                     "debugging", "research"],
    },
    {
        "name": "Keel",
        "role": "Infrastructure Lead",
        "email": "keel@agentmail.to",
        "domains": ["infrastructure", "development", "quality",
                     "debugging", "workflow", "reasoning"],
    },
    {
        "name": "Russell",
        "role": "Human Partner",
        "email": None,  # notified via Telegram, not AgentMail
        "domains": ["content", "communication", "research", "decision-gates"],
    },
]


def load_local_skills() -> list[dict]:
    """Load metadata from locally installed skills."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text()
        name = skill_dir.name

        # Extract purpose/description
        purpose = ""
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                purpose = line[:200]
                break

        # Check for origin (imported vs created)
        is_imported = "## Origin" in content and "Imported from" in content

        skills.append({
            "name": name,
            "purpose": purpose,
            "is_imported": is_imported,
            "source": "local",
            "path": str(skill_file),
        })

    return skills


def load_hub_skills() -> list[dict]:
    """Load skill metadata from HUB threads."""
    r = hub_get(f"/api/v2/rooms/{SKILLS_LIBRARY_ROOM}/threads/list?limit=100")
    if not r.ok:
        print(f"  Warning: Could not fetch HUB threads ({r.status_code})")
        return []

    data = r.json()
    threads = data if isinstance(data, list) else data.get("items", data.get("threads", []))

    skills = []
    for t in threads:
        title = t.get("title", "")
        body = t.get("body", "")
        author = t.get("author", {}).get("display_name", "unknown")

        m = re.match(r'\[SKILL\]\s+(.+?)\s+v[\d.]+\s*[—-]\s*(\S+)', title)
        name = m.group(1).strip() if m else title
        category = m.group(2) if m else "?"

        skills.append({
            "name": name,
            "purpose": body[:200].replace('\n', ' '),
            "category": category,
            "author": author,
            "thread_id": t.get("id", ""),
            "source": "hub",
        })

    return skills


def load_goals(goals_files: list[Path] = None) -> str:
    """Load current goals/context from configured sources."""
    sources = goals_files or DEFAULT_GOALS_SOURCES
    context = []

    for src in sources:
        if src.exists():
            try:
                text = src.read_text()
                # Take first 2000 chars to keep context manageable
                context.append(f"--- {src.name} ---\n{text[:2000]}")
            except Exception:
                pass

    return "\n\n".join(context)


def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from goals text."""
    # Common stop words to skip
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "out",
        "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "each", "every",
        "both", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "because", "but", "and", "or", "if", "while", "about", "up", "its",
        "it", "this", "that", "these", "those", "we", "they", "he", "she",
        "you", "my", "your", "his", "her", "our", "their", "what", "which",
        "who", "whom", "new", "also", "any", "see", "use", "used", "using",
    }

    words = re.findall(r'[a-z]{3,}', text.lower())
    return {w for w in words if w not in stop_words}


def match_skill_to_goals(skill: dict, goal_keywords: set) -> float:
    """Score how well a skill matches current goals. 0-10 scale."""
    skill_text = f"{skill['name']} {skill.get('purpose', '')} {skill.get('category', '')}"
    skill_words = extract_keywords(skill_text)

    if not skill_words or not goal_keywords:
        return 0.0

    overlap = skill_words & goal_keywords
    if not overlap:
        return 0.0

    # Base score: ratio of matching words
    score = len(overlap) / len(skill_words) * 5.0

    # Bonus for name match (skill name words in goals)
    name_words = set(re.findall(r'[a-z]{3,}', skill["name"].lower()))
    name_overlap = name_words & goal_keywords
    if name_overlap:
        score += len(name_overlap) * 2.0

    return min(round(score, 1), 10.0)


def match_skill_to_person(skill: dict, person: dict) -> float:
    """Score how relevant a skill is to a team member. 0-5 scale."""
    category = skill.get("category", "").lower()
    domains = [d.lower() for d in person.get("domains", [])]

    if category in domains:
        return 3.0

    # Partial match on skill name vs domains
    name_lower = skill["name"].lower()
    for domain in domains:
        if domain in name_lower or name_lower in domain:
            return 2.0

    return 0.0


def generate_suggestions(skills: list[dict], goal_keywords: set,
                          goals_text: str) -> list[dict]:
    """Generate actionable skill suggestions."""
    suggestions = []

    for skill in skills:
        goal_score = match_skill_to_goals(skill, goal_keywords)

        if goal_score < 1.0:
            continue

        # Find best person match
        best_person = None
        best_person_score = 0
        for person in TEAM_ROSTER:
            ps = match_skill_to_person(skill, person)
            if ps > best_person_score:
                best_person = person
                best_person_score = ps

        total_score = goal_score + best_person_score

        if total_score < 2.0:
            continue

        # Determine impact
        if total_score >= 7:
            impact = "high"
        elif total_score >= 4:
            impact = "medium"
        else:
            impact = "low"

        suggestion = {
            "skill": skill["name"],
            "source": skill.get("source", "?"),
            "category": skill.get("category", "?"),
            "purpose": skill.get("purpose", "")[:150],
            "who_benefits": best_person["name"] if best_person else "team",
            "their_role": best_person["role"] if best_person else "general",
            "impact": impact,
            "score": round(total_score, 1),
            "goal_relevance": goal_score,
        }

        suggestions.append(suggestion)

    # Sort by score descending
    suggestions.sort(key=lambda s: s["score"], reverse=True)
    return suggestions[:10]  # Top 10


def format_suggestion(s: dict, index: int) -> str:
    """Format a single suggestion for display."""
    return (
        f"\n  {index}. SKILL-SUGGESTION:\n"
        f"     Skill: {s['skill']}\n"
        f"     Source: {s['source']} | Category: {s['category']}\n"
        f"     Who benefits: {s['who_benefits']} ({s['their_role']})\n"
        f"     Purpose: {s['purpose']}\n"
        f"     Impact: {s['impact']} (score: {s['score']})"
    )


def write_suggestions_log(suggestions: list[dict]):
    """Write suggestions to daily log and config file."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Save to config for skill_distribute.py to pick up
    SUGGESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SUGGESTIONS_FILE.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "suggestions": suggestions,
    }, indent=2))

    # Append to daily log
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"skill-suggestions-{date_str}.md"

    lines = [
        f"# Skill Suggestions — {date_str}",
        f"",
        f"**Generated**: {datetime.now(timezone.utc).isoformat()}",
        f"**Suggestions**: {len(suggestions)}",
        f"",
    ]

    for i, s in enumerate(suggestions, 1):
        lines.append(f"## {i}. {s['skill']}")
        lines.append(f"- **Source**: {s['source']}")
        lines.append(f"- **Category**: {s['category']}")
        lines.append(f"- **Who benefits**: {s['who_benefits']} ({s['their_role']})")
        lines.append(f"- **Impact**: {s['impact']} (score: {s['score']})")
        lines.append(f"- **Purpose**: {s['purpose']}")
        lines.append(f"")

    log_file.write_text("\n".join(lines))
    print(f"\nLog: {log_file}")
    print(f"Config: {SUGGESTIONS_FILE}")


def suggest(goals_file: str = None, dry_run: bool = False):
    """Main suggestion cycle."""
    print("Skill Suggestion Engine — matching skills to goals")

    # 1. Load skills (local + HUB)
    print("\n1. Loading skills...")
    local_skills = load_local_skills()
    print(f"   Local: {len(local_skills)} skills")

    hub_skills = load_hub_skills()
    print(f"   HUB: {len(hub_skills)} threads")

    all_skills = local_skills + hub_skills

    if not all_skills:
        print("No skills found. Nothing to suggest.")
        return

    # 2. Load goals
    print("\n2. Loading goals context...")
    goals_files = [Path(goals_file)] if goals_file else None
    goals_text = load_goals(goals_files)

    if not goals_text:
        print("   No goals context found. Cannot generate suggestions.")
        return

    goal_keywords = extract_keywords(goals_text)
    print(f"   Keywords extracted: {len(goal_keywords)}")

    # 3. Generate suggestions
    print("\n3. Generating suggestions...")
    suggestions = generate_suggestions(all_skills, goal_keywords, goals_text)

    if not suggestions:
        print("   No relevant suggestions found.")
        return

    # 4. Display
    print(f"\n   Generated {len(suggestions)} suggestions:")
    for i, s in enumerate(suggestions, 1):
        print(format_suggestion(s, i))

    # 5. Log
    if not dry_run:
        write_suggestions_log(suggestions)
    else:
        print("\n[DRY RUN] Suggestions not logged.")

    return suggestions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate skill suggestions matched to goals")
    parser.add_argument("--goals-file", help="Custom goals file path")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview suggestions without logging")
    args = parser.parse_args()

    suggest(goals_file=args.goals_file, dry_run=args.dry_run)
