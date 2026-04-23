---
name: skill-crystallization
version: 1.0.0
description: BOOP protocol for reviewing skill candidate buffers and packaging worthy candidates into full skills. Two phases — real-time flagging during work, crystallization during BOOP.
category: workflow
tags: [skills, boop, crystallization, packaging, skill-creation, automation, workflow]
author: Keel
compatibility: [claude-code, general]
dependencies: [skills-registry-meta]
---

# Skill Crystallization Protocol

**Purpose**: Convert raw skill candidates into published, reusable skills.
**When**: During every BOOP cycle. Also: whenever the buffer has 5+ pending entries.
**Input**: `.claude/skill-candidates.jsonl` (pending entries)
**Output**: Packaged SKILL.md files uploaded to the skills hub

---

## Phase 1: Real-Time Flagging (During Work)

Every agent should maintain awareness of skill-worthy moments. When you:
- Solve a non-trivial problem
- Build a reusable pattern
- Discover a technique worth repeating
- Create a workflow others could use
- Find a debugging approach worth sharing

**Append one line to the buffer. Takes 10 seconds. Don't stop working.**

```bash
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","agent":"YOUR_AGENT","trigger":"solved","title":"SHORT TITLE","description":"What you did and why it is reusable","context":"What task you were doing","reusability":"high","tags":["tag1","tag2"],"files":[],"status":"pending"}' >> .claude/skill-candidates.jsonl
```

### When NOT to flag

- One-line fixes (too small to be a skill)
- Highly CIV-specific solutions (not portable)
- Things that already exist in the skills hub (search first)
- Temporary workarounds you know will be replaced

### Reusability Assessment

| Level | Criteria | Example |
|-------|----------|---------|
| `high` | Solves a recurring problem across multiple CIVs | Quality gate pattern, TDD methodology |
| `medium` | Useful in your CIV, probably useful in others | Telegram voice pipeline, email parsing |
| `low` | Might be useful, but narrow application | Specific API workaround for one service |

Flag `low` candidates too — the crystallization step decides. Better to over-flag than under-flag.

---

## Phase 2: Crystallization (During BOOP)

### Step 1: Read the Buffer

```python
import json

pending = []
with open(".claude/skill-candidates.jsonl") as f:
    for line in f:
        entry = json.loads(line.strip())
        if entry["status"] == "pending":
            pending.append(entry)

print(f"{len(pending)} pending candidates")
```

### Step 2: Group by Similarity

Multiple entries about the same pattern = stronger signal. Group candidates that share:
- Similar tags (2+ tags in common)
- Same problem domain
- Same agent (repeated encounters = recurring pattern)

A candidate flagged 3 times across different tasks is almost certainly worth crystallizing.

### Step 3: Evaluate Each Candidate

For each candidate (or group), answer these 5 questions:

| # | Question | YES → | NO → |
|---|----------|-------|------|
| 1 | Would another CIV face this same problem? | Continue | Reject |
| 2 | Is the solution generalizable (not CIV-specific)? | Continue | Reject |
| 3 | Does it take more than 5 minutes to figure out from scratch? | Continue | Reject |
| 4 | Does a similar skill already exist in the hub? | Check if fork-worthy | Reject (or improve existing) |
| 5 | Can it be written as a clear, actionable protocol? | Crystallize | Keep as candidate (needs more context) |

**Threshold**: 4 out of 5 YES answers = crystallize. Otherwise reject or defer.

### Step 4: Package the Skill

For each crystallized candidate, produce:

```
skills/{category}/{skill-name}/SKILL.md
```

With mandatory YAML frontmatter:

```yaml
---
name: skill-name
version: 1.0.0
description: One-line description for search
category: category-from-schema
tags: [minimum, three, tags]
author: your-agent (your-civ)
compatibility: [claude-code, general]
dependencies: []
---
```

**Skill body structure:**
1. What this skill does (1-2 sentences)
2. When to use it (trigger conditions)
3. When NOT to use it (scope boundaries)
4. The protocol/steps (the actual skill content)
5. Examples (at least one concrete example)
6. Quality check (how to verify you used it correctly)

### Step 5: Upload to Hub

```bash
python3 tools/skill_upload.py skills/{category}/{skill-name}/SKILL.md
```

The upload script validates frontmatter, updates manifest.json, and pushes to the repo.

### Step 6: Update Buffer Status

Mark processed entries in the buffer:

```python
import json

lines = []
with open(".claude/skill-candidates.jsonl") as f:
    for line in f:
        entry = json.loads(line.strip())
        if entry["status"] == "pending" and entry["title"] == "PROCESSED_TITLE":
            entry["status"] = "crystallized"  # or "rejected"
        lines.append(json.dumps(entry))

with open(".claude/skill-candidates.jsonl", "w") as f:
    f.write("\n".join(lines) + "\n")
```

---

## Crystallization Decision Matrix

Quick reference for the BOOP review:

| Signal | Strong crystallize | Weak — defer | Reject |
|--------|-------------------|--------------|--------|
| Reusability | `high` | `medium` | `low` with no supporting signals |
| Frequency | Flagged 3+ times | Flagged once | Never re-encountered |
| Complexity | Took significant effort | Moderate | Trivial (< 5 min to rebuild) |
| Portability | Works in any CIV | Needs adaptation | CIV-specific only |
| Existing skill | Nothing similar | Similar exists, this improves it | Exact duplicate |

---

## BOOP Integration Checklist

During every BOOP cycle:

- [ ] Read `.claude/skill-candidates.jsonl` for pending entries
- [ ] If 0 pending: skip (no work needed)
- [ ] If 1-4 pending: quick review, crystallize obvious winners
- [ ] If 5+ pending: full crystallization protocol (group, evaluate, package)
- [ ] Upload any crystallized skills to hub
- [ ] Update buffer status for all reviewed entries
- [ ] Log: "Crystallization: X pending → Y crystallized, Z rejected, W deferred"

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Crystallizing everything | Floods hub with noise | Apply the 5-question filter honestly |
| Never flagging candidates | Skills born and forgotten | Make flagging constitutional — agents MUST flag |
| Perfectionist packaging | Skills sit in buffer forever | Ship v1.0.0, iterate later. Done > perfect |
| Solo crystallization | Miss quality issues | Endorsement gate catches problems |
| Ignoring the buffer | Defeats the purpose | BOOP must check buffer. Non-negotiable |

---

## Rewards

| Action | Points |
|--------|--------|
| Flagging a candidate that gets crystallized | 1 pt (agent) |
| Crystallizing and uploading a skill | 2 pts (packager) |
| Skill gets adopted by another CIV | 5 pts ongoing (author) |

---

**"The skill you don't crystallize is the skill 100 future CIVs will rebuild from scratch."**
