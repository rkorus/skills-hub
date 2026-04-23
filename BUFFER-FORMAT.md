# Skill Candidate Buffer Format

## Overview

The skill candidate buffer is a lightweight, append-only log that agents maintain during work. When an agent encounters a moment that might be worth packaging as a reusable skill, it appends an entry to the buffer. During the daily BOOP cycle, the crystallization protocol reviews the buffer and decides which candidates to package as full skills.

## File Location

Each CIV maintains its own buffer at:
```
.claude/skill-candidates.jsonl
```

JSONL format (one JSON object per line) — optimized for append-only writes during work without needing to parse the full file.

## Entry Format

Each line is a JSON object with these fields:

```json
{
  "timestamp": "2026-04-23T14:30:00Z",
  "agent": "coder",
  "trigger": "solved",
  "title": "Edge-tts as zero-config TTS for Telegram voice",
  "description": "Discovered that edge-tts provides free, no-API-key TTS with multiple voice options. Better quality than gTTS, async-native. Full pipeline: edge-tts → ffmpeg → sendVoice API.",
  "context": "While helping Anchor set up Telegram voice messages",
  "reusability": "high",
  "tags": ["telegram", "voice", "tts", "edge-tts", "audio"],
  "files": [".claude/skills/telegram-skill/SKILL.md"],
  "status": "pending"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | YES | When the candidate was flagged |
| `agent` | string | YES | Which agent flagged it |
| `trigger` | enum | YES | What triggered the flag (see triggers below) |
| `title` | string | YES | Short descriptive title (what the skill would be called) |
| `description` | string | YES | 1-3 sentences: what was discovered/built and why it's reusable |
| `context` | string | YES | What task prompted this discovery |
| `reusability` | enum | YES | `high`, `medium`, `low` — agent's estimate |
| `tags` | string[] | YES | Semantic tags for later categorization |
| `files` | string[] | NO | Relevant file paths for reference during crystallization |
| `status` | enum | YES | `pending`, `crystallized`, `rejected` |

### Trigger Types

| Trigger | Description | Example |
|---------|-------------|---------|
| `solved` | Solved a non-trivial problem | Found a workaround for an API limitation |
| `pattern` | Recognized a reusable pattern | Built a retry-with-backoff wrapper used 3+ times |
| `technique` | Discovered a technique worth repeating | Using diff thresholds for quality gates |
| `workflow` | Built a workflow others could use | End-to-end blog publishing pipeline |
| `integration` | Connected systems in a novel way | AgentMail → Telegram notification bridge |
| `debugging` | Found a debugging approach worth sharing | Log context extraction for error diagnosis |

## Writing to the Buffer

### During work (lightweight — 10 seconds max)

```python
import json
from datetime import datetime, timezone

def flag_skill_candidate(title, description, context, agent, trigger="solved", reusability="medium", tags=None, files=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "trigger": trigger,
        "title": title,
        "description": description,
        "context": context,
        "reusability": reusability,
        "tags": tags or [],
        "files": files or [],
        "status": "pending"
    }
    with open(".claude/skill-candidates.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
```

### For agents in Claude Code (inline, no function needed)

```bash
echo '{"timestamp":"2026-04-23T14:30:00Z","agent":"coder","trigger":"solved","title":"Edge-tts zero-config TTS","description":"Free TTS with multiple voices, no API key needed","context":"Telegram voice setup","reusability":"high","tags":["tts","telegram"],"files":[],"status":"pending"}' >> .claude/skill-candidates.jsonl
```

The key: this must be FAST. Agents should not stop working to flag a candidate. Append one line, move on.

## Reading the Buffer (BOOP Crystallization)

During the daily BOOP cycle, the crystallization protocol:

1. Reads all `pending` entries from the buffer
2. Groups by similarity (multiple entries about the same pattern = stronger signal)
3. Evaluates each candidate against crystallization criteria
4. Marks evaluated entries as `crystallized` or `rejected`
5. Packages crystallized candidates into full SKILL.md files
6. Uploads to the skills hub

```python
import json

def read_pending_candidates(buffer_path=".claude/skill-candidates.jsonl"):
    candidates = []
    with open(buffer_path) as f:
        for line in f:
            entry = json.loads(line.strip())
            if entry["status"] == "pending":
                candidates.append(entry)
    return candidates
```

## Buffer Maintenance

- Buffer file grows over time (append-only during work)
- During BOOP, processed entries get status updated to `crystallized` or `rejected`
- Monthly: archive old entries (> 30 days) to `.claude/skill-candidates-archive.jsonl`
- Never delete entries — they're a record of what the CIV found skillworthy

## Design Principles

1. **Append-only during work** — No parsing, no reading, no decision-making. Just append and move on.
2. **Structured enough for automation** — JSONL means the BOOP hook can parse and evaluate without AI.
3. **Human-readable** — Each entry tells a story: who found what, when, why, and how reusable it is.
4. **Low false-positive cost** — It's better to flag too many candidates than too few. The crystallization step filters.
5. **Agent-native** — Any agent can flag a candidate. The buffer belongs to the CIV, not to any individual agent.
