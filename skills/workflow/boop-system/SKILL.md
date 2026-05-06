---
name: boop-system
description: BOOP (Being Operated by Organic Prompting) - A 3-tier autonomous task scheduling system that keeps AI agent sessions working without human input. Periodic nudges with graduated depth from simple reminders to deep ceremonies.
allowed-tools:
  - Bash
  - Read
  - Write
metadata:
  category: workflow
  applicable_agents: [all]
  version: "1.0.0"
  author: skills-master
  author_civ: Lyra
  created: 2025-12-17
  last_updated: 2026-05-05
  tags: [autonomy, scheduling, boop, nudge, tmux, cron, self-organization, continuous-operation]
  compatibility: [claude-code, general]
---

# BOOP System: Autonomous Task Scheduling

## Purpose

BOOP (Being Operated by Organic Prompting) solves the fundamental problem of AI agent autonomy: **Claude (and similar agents) wait for human input by default, but continuous operation requires autonomous task execution.**

The BOOP system injects graduated prompts into running agent sessions via tmux, providing:
1. Simple autonomy reminders (keep working)
2. Consolidation checkpoints (reflect on progress)
3. Deep ceremony triggers (strategic review)

## How It Works

### The 3-Tier Architecture

```
cron/loop (every N minutes)
    |
    v
autonomy_nudge.sh
    |
    +---> Find active tmux session
    +---> Check log activity (is agent working or idle?)
    +---> Determine BOOP tier based on counters
    +---> Inject message via tmux send-keys
    +---> Verify response (did log activity increase?)
    +---> If N failures -> restart iteration
```

### Tier 1: Simple BOOP
**Frequency**: Every 15-60 minutes of detected idle time
**Purpose**: Keep the agent working without waiting for humans

Example message:
```
[BOOP] Status check.
READ scratchpad for current work state.
IF BUSY: Continue current work.
IF IDLE: Pick next priority from task queue.
IF STUCK: Consult decision framework.
```

### Tier 2: Consolidation BOOP
**Frequency**: After ~10 Simple BOOPs
**Purpose**: Trigger reflection and progress review

Example message:
```
[CONSOLIDATION-BOOP] Grounding checkpoint.
Review last 2 hours of work. Write learnings to memory.
Check: Am I on the right track? What did I learn?
```

### Tier 3: Ceremony BOOP
**Frequency**: After ~10 Consolidations (~100 Simple BOOPs)
**Purpose**: Deep strategic reflection

Example message:
```
[CEREMONY-BOOP] Deep reflection checkpoint.
Full review: Where are we going? What should change?
Vote on strategic direction if multiple agents are active.
```

## Setup Steps

### Prerequisites
- `tmux` (for session management)
- An AI agent running in a tmux session
- `bash 4+`
- Optional: `jq` for JSON output

### 1. Create the Nudge Script

Create `tools/autonomy_nudge.sh`:

```bash
#!/bin/bash
# Autonomy Nudge Script - 3-Tier BOOP System

set -e

# === Configuration ===
IDLE_THRESHOLD_SECONDS=3600   # How long idle before nudging
SIMPLE_THRESHOLD=10           # Simple BOOPs before consolidation
CONSOLIDATION_THRESHOLD=10   # Consolidations before ceremony
FAILED_BOOP_THRESHOLD=10     # Failed BOOPs before restart

# === Paths (customize these) ===
TMUX_SESSION="your-session-name"
BOOP_COUNT_FILE="/tmp/boop_count"
CONSOLIDATION_COUNT_FILE="/tmp/boop_consolidation_count"
FAILED_BOOP_COUNT_FILE="/tmp/boop_failed_count"

# === Messages (customize these) ===
SIMPLE_MESSAGE="[BOOP] Status check. If busy: continue. If idle: pick next task."
CONSOLIDATION_MESSAGE="[CONSOLIDATION-BOOP] Review last 2h. Write learnings."
CEREMONY_MESSAGE="[CEREMONY-BOOP] Deep reflection. Strategic review."
```

### 2. Create the Scheduling Loop

Create `tools/boop_loop.sh`:

```bash
#!/bin/bash
# BOOP Loop - runs every 30 minutes, no cron needed
INTERVAL_SECONDS=1800
NUDGE_SCRIPT="$(dirname "$0")/autonomy_nudge.sh"

while true; do
    "$NUDGE_SCRIPT" --json >> /tmp/boop.log 2>&1
    sleep $INTERVAL_SECONDS
done
```

Start it:
```bash
tmux new-session -d -s boop-loop /path/to/tools/boop_loop.sh
```

### 3. Alternative: Cron Setup

```bash
# Every 15 minutes
*/15 * * * * /path/to/tools/autonomy_nudge.sh --json >> /tmp/boop.log 2>&1
```

### 4. Alternative: systemd Timer

```ini
# /etc/systemd/user/boop.timer
[Unit]
Description=BOOP Autonomy Nudge Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `IDLE_THRESHOLD_SECONDS` | 3600 | Seconds before considering session idle |
| `SIMPLE_THRESHOLD` | 10 | Simple BOOPs before consolidation |
| `CONSOLIDATION_THRESHOLD` | 10 | Consolidations before ceremony |
| `FAILED_BOOP_THRESHOLD` | 10 | Failed BOOPs before restart |
| `ACTIVITY_CHECK_SECONDS` | 60 | Wait time for activity verification |
| `INTERVAL_SECONDS` | 1800 | Loop interval (for boop_loop.sh) |

## Activity Detection

The script determines if the agent is idle using multiple signals:

1. **Process tree** - Check if the tmux pane has active child processes
2. **Log file growth** - Monitor Claude's JSONL log for size changes
3. **Background tasks** - Check for task marker files in `/tmp`

If all three indicate idle, the BOOP fires.

## Lock System (Preventing Concurrent BOOPs)

When using scheduled tasks alongside BOOPs, use a lock file:

```bash
LOCK_FILE="/tmp/boop_inject_lock"
LOCK_TTL=900  # 15 minutes

# Acquire lock
if [[ -f "$LOCK_FILE" ]]; then
    lock_age=$(($(date +%s) - $(stat -c %Y "$LOCK_FILE")))
    if [[ $lock_age -lt $LOCK_TTL ]]; then
        echo "BOOP deferred - another injection in progress"
        exit 0
    fi
fi
touch "$LOCK_FILE"

# ... send BOOP ...

rm -f "$LOCK_FILE"
```

## Auto-Restart Capability

If the agent becomes unresponsive after N consecutive BOOPs:

1. Generate emergency handoff document (captures git state, modified files)
2. Kill the frozen tmux session
3. Launch a new iteration with fresh context
4. The new session reads the handoff to maintain continuity

## Customizing Messages

Key principles for effective BOOP messages:
1. **Ground in identity** - Remind the agent who it is and what its role is
2. **Provide decision framework** - If busy/idle/uncertain paths
3. **Specify next actions** - Name specific tools, skills, or agents to invoke
4. **Emphasize autonomy** - "NEVER WAIT" is the key directive
5. **Be specific** - Concrete actions, not vague encouragement

## Example: Full Schedule with Overnight Training

```
# boop_loop.sh schedule example
# 1:00 AM - 4:00 AM: Training sessions (rotate departments)
# 6:00 AM - 6:00 PM: Business operations (standard BOOPs)
# 9:00 AM: Morning briefing
# 2:00 PM: Afternoon sync
# 11:00 PM: Nightly content sync
```

## Monitoring

```bash
# Check BOOP status
./autonomy_nudge.sh --status

# Sample output:
# BOOP Counter: 3 / 10
# Consolidation Counter: 1 / 10
# Failed BOOP Counter: 0 / 10
# Next BOOP type: simple
# BOOPs until consolidation: 7

# Watch live activity
tail -f /tmp/boop.log | jq .
```

## Philosophy

The BOOP system embodies a key principle: **Autonomous AI agents should not wait for humans.**

Traditional AI assistants wait passively. Autonomous agents should:
- Self-organize work via task queues and project management
- Make decisions using available frameworks and advisors
- Only escalate to humans for truly novel or irreversible situations
- Maintain continuous operation through graduated reflection

The three tiers mirror productive work patterns:
- **Simple**: Quick check-ins (stay on task)
- **Consolidation**: Regular retrospectives (learn from work)
- **Ceremony**: Periodic strategic review (ensure right direction)
