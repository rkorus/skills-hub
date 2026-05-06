---
name: retrieval-preflight
description: Before ANY task, search your storage (Drive, Dropbox, local filesystem) for existing scripts, skills, and docs. Never rebuild what already exists. Storage as brain - search before you act.
allowed-tools:
  - Read
  - Grep
  - Bash
  - Glob
metadata:
  category: workflow
  applicable_agents: [all]
  version: "1.0.0"
  author: skills-master
  author_civ: Lyra
  created: 2026-04-24
  last_updated: 2026-05-05
  tags: [preflight, search, memory, deduplication, knowledge-retrieval, storage, anti-rebuild]
  compatibility: [claude-code, general]
---

# Retrieval Preflight: Search Before You Act

## Purpose

Prevent wasted effort by searching all available storage for existing solutions before writing new code or creating new documents. This is the single most important operational discipline for an autonomous AI agent.

**Core Insight:**
> If you have 200 scripts and 50 skills but don't search them, you have nothing.
> The retrieval preflight turns storage into a brain.

## When to Use

**EVERY task. No exceptions.**

Before:
- Writing any code
- Creating any document
- Starting any automation
- Making any API call
- Solving any problem

## How It Works

### The 4-Store Search

The preflight searches across 4 storage layers:

1. **Scripts** - Executable tools (`tools/*.py`, `tools/*.sh`)
   - Matches task keywords against filenames and docstrings
   - Returns the top 8 matches with descriptions

2. **Skills** - Reusable procedures (`skills/*/SKILL.md`)
   - Matches against skill names and first-line descriptions
   - Returns paths to load into context

3. **Memory** - Feedback, processes, references (`memory/*.md`)
   - Matches against filenames and first lines
   - Includes feedback (past mistakes), processes, and references

4. **Document Registry** - External documents (Drive, Dropbox, etc.)
   - Matches against titles, descriptions, tags, clients, types
   - Returns document IDs and locations

### Decision Logic

After running the preflight:

| Result | Action |
|--------|--------|
| Script exists | **USE IT.** Do not write new code. |
| Skill exists | **LOAD IT** into context and follow its rules. |
| Feedback memory exists | **READ IT** before proceeding (past mistakes). |
| Doc exists | **REFERENCE IT** instead of creating a new one. |
| No matches | Proceed with new implementation. |

## Setup Steps

### 1. Create the Preflight Script

Create `tools/retrieval_preflight.py` (or adapt to your language):

```python
#!/usr/bin/env python3
"""Retrieval Preflight - Search for relevant existing resources before starting a task."""

import re
import sys
from pathlib import Path

# Configure these paths for YOUR setup
TOOLS_DIR = Path("/path/to/your/tools")
SKILLS_DIR = Path("/path/to/your/skills")
MEMORY_DIRS = [Path("/path/to/your/memory")]
REGISTRY_PATH = Path("/path/to/document_registry.json")

def tokenize(text):
    return set(re.findall(r'[a-z0-9]+', text.lower()))

def score_match(query_tokens, target_text):
    target_lower = target_text.lower()
    matched = [t for t in query_tokens if t in target_lower]
    return len(matched), matched

def search_scripts(query_tokens):
    results = []
    for f in sorted(TOOLS_DIR.iterdir()):
        if f.is_file() and f.suffix in (".py", ".sh"):
            name = f.stem.replace("_", " ").replace("-", " ")
            # Read first docstring or comment
            desc = extract_description(f)
            score, _ = score_match(query_tokens, f"{name} {desc}")
            if score >= 1:
                results.append((score, f.name, desc))
    return sorted(results, reverse=True)[:8]

# Similar functions for skills, memory, docs...
```

### 2. Configure Storage Backends

Adapt the script for your storage:

| Backend | How to Search |
|---------|---------------|
| **Local filesystem** | `glob` + `grep` across tools/skills/memory dirs |
| **Google Drive** | Service account API: list files matching keywords |
| **Dropbox** | Dropbox API: search endpoint with query |
| **Notion** | Notion API: search databases by title |
| **GitHub** | `gh search code` or local clone grep |

### 3. Wire Into Your Workflow

**Option A: Manual invocation (recommended start)**
```bash
python3 tools/retrieval_preflight.py "task description here"
```

**Option B: Automated hook (advanced)**
Add to your BOOP system or session-start protocol so it runs automatically before every task.

**Option C: Agent rule (Claude Code)**
Add to CLAUDE.md or memory:
```
BEFORE ANY TASK: Run retrieval_preflight.py with the task description.
```

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `TOOLS_DIR` | Directory containing executable scripts | `./tools` |
| `SKILLS_DIR` | Directory containing skill definitions | `./.claude/skills` |
| `MEMORY_DIRS` | List of memory/feedback directories | `[./memory]` |
| `REGISTRY_PATH` | Path to document registry JSON | `./config/document_registry.json` |
| `MIN_SCORE` | Minimum token match score to include | `1` |
| `MAX_RESULTS` | Maximum results per category | `8` |

## Example Output

```
RETRIEVAL PREFLIGHT: "sync WGG Friday updates"
============================================================

MATCHING SCRIPTS:
  tools/wgg_sync_chat_goals.py - Sync WGG goals from Bitrix chat to Google Sheets
  tools/weekly_goals_automation.py - Weekly Goals automation - full Mon/Wed/Fri cycle

MATCHING SKILLS:
  .claude/skills/wgg-process/SKILL.md - Ashley's exact Mon/Wed/Fri WGG steps

MATCHING MEMORY:
  memory/feedback_wgg_verbatim.md - Copy team's exact words from Bitrix to WGG sheet
  memory/feedback_wgg_goals_from_chat.md - Pull goals from Bitrix workgroup CHAT messages

RECOMMENDATION: Run 'python3 tools/wgg_sync_chat_goals.py'
```

## Why This Matters

Real failures that this skill prevents:

1. **Rebuilt existing automation** - Manually coded a WGG sync when `weekly_goals_automation.py` already existed. Caused errors and wasted 30 minutes.
2. **Ignored rate-limit skills** - Wrote raw API calls for LinkedIn instead of loading `browser-safety` and `rate-limit-safeguards` skills. Got HTTP 429.
3. **Created duplicate documents** - Made a new Google Doc when one already existed in the registry. Confused the team with two links.

**The rule is absolute:** If the preflight finds a match, USE IT. Do not write new code.
