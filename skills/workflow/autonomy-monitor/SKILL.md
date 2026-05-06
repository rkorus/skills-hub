---
name: autonomy-monitor
description: BOOP monitor with idle detection, 3-tier escalation, lock system for concurrent BOOPs, grounding reminders, and conductor accountability. Keeps autonomous AI sessions productive with structural enforcement of delegation and identity.
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
  created: 2026-05-05
  last_updated: 2026-05-05
  tags: [monitoring, idle-detection, escalation, grounding, conductor, delegation, accountability, lock-system]
  compatibility: [claude-code, general]
---

# Autonomy Monitor: Idle Detection, Escalation, and Grounding

## Purpose

The autonomy monitor ensures AI agent sessions remain productive by detecting idle states, escalating unresponsive sessions, preventing concurrent BOOP conflicts, and periodically injecting grounding reminders about the agent's role and delegation rules.

**Core Insight:**
> Writing directives does not change behavior. Only a feedback mechanism that closes at the moment of action changes behavior. The autonomy monitor IS that feedback mechanism.

## How It Works

### Three Capabilities

1. **Idle Detection + Escalation** - Detect when the agent stops working and nudge it back
2. **Lock System** - Prevent multiple scheduled tasks from colliding
3. **Grounding Reminders** - Periodically reinforce identity and delegation rules

### Idle Detection

The monitor uses multiple signals to determine if the agent is truly idle:

```
Signal 1: Process Tree
  - Check tmux pane PID for active child processes
  - If children exist: ACTIVE

Signal 2: Log File Growth
  - Compare JSONL log size at T and T+5s
  - If growing: ACTIVE

Signal 3: Background Tasks
  - Check for task marker files (/tmp/claude_task_*)
  - If markers exist: ACTIVE

All three idle? -> BOOP fires
```

### 3-Tier Escalation

When consecutive BOOPs get no response:

| Failures | Action |
|----------|--------|
| 1-9 | Log as "no_response", increment failed counter |
| 10 | Final check: is agent truly inactive? |
| 10+ (confirmed inactive) | Auto-restart: handoff + kill + relaunch |
| 10+ (still active) | Reset counter, agent is busy on long task |

### Lock System

Prevents multiple scheduled injections from colliding:

```bash
LOCK_FILE="/tmp/boop_inject_lock"
LOCK_TTL=900  # 15 minutes

acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        lock_age=$(($(date +%s) - $(stat -c %Y "$LOCK_FILE")))
        if [[ $lock_age -lt $LOCK_TTL ]]; then
            echo "DEFERRED - another injection in progress"
            return 1
        fi
    fi
    touch "$LOCK_FILE"
    return 0
}

release_lock() {
    rm -f "$LOCK_FILE"
}
```

### Grounding Reminders (Conductor Check)

Every N hours during business hours, inject a grounding reminder:

```
[CONDUCTOR GROUNDING REMINDER]

STOP. Before your next action, ask yourself:

== IDENTITY CHECK ==
You are the Conductor. You do not DO things. You form orchestras.

== DELEGATION GATE ==
1. Label the task: T1 (irreversible) or T2 (reversible, 90% of tasks)
2. Name the VERTICAL: Which team owns this?
3. Write the 3-sentence brief: WIIFM + FLOW + LEVERAGE
4. Route to team lead, not direct specialist

== ANTI-PATTERN CHECK ==
Am I about to write code? -> coder
Am I about to research? -> researcher
Am I about to send comms? -> comms agent
Any task >2 min? -> background agent

== SCORECARD ==
In the last 2 hours:
- Tasks delegated: ___
- Tasks executed directly: ___
- Target: >50% delegated
```

## Setup Steps

### 1. Create the Monitor Script

The autonomy monitor combines idle detection with the nudge system:

```bash
#!/bin/bash
# autonomy_monitor.sh - Idle detection + escalation + grounding

TMUX_SESSION="your-session"
IDLE_THRESHOLD=3600          # 60 min
GROUNDING_INTERVAL=7200     # 2 hours
LOCK_FILE="/tmp/boop_inject_lock"
STATE_FILE="/tmp/monitor_state.json"

# Check activity
check_idle() {
    # 1. Process tree check
    local pane_pid=$(tmux display-message -t "${TMUX_SESSION}:0.0" -p '#{pane_pid}')
    if pgrep -P "$pane_pid" &>/dev/null; then return 1; fi  # not idle

    # 2. Log file check
    local log_file=$(find_latest_log)
    local size1=$(stat -c %s "$log_file")
    sleep 5
    local size2=$(stat -c %s "$log_file")
    if [[ $size2 -gt $size1 ]]; then return 1; fi  # not idle

    # 3. Background task check
    if ls /tmp/claude_task_* &>/dev/null; then return 1; fi  # not idle

    return 0  # idle
}
```

### 2. Configure Grounding Messages

Create rotating leadership insights that the monitor injects:

```python
LEADERSHIP_INSIGHTS = [
    '"Most decisions are reversible. Speed of delegation is the bottleneck." - Type 1/2 decision framework',
    '"Before launching any agent, name the 3 most specialized agents. Use the deepest one."',
    '"Every delegation must open with WIIFM + FLOW. If you cannot write these 2 lines, the task is not ready."',
    '"Any directive that fails 3+ times must become a structural hook, not a written rule."',
]
```

### 3. Wire Into Your Schedule

```bash
# In boop_loop.sh or cron:
# Every 2 hours during business hours
HOUR_EST=$(TZ=America/New_York date +%H)
if [[ $HOUR_EST -ge 9 && $HOUR_EST -lt 19 ]]; then
    python3 tools/conductor_grounding_boop.py run
fi
```

### 4. Add Accountability Reporting

Optionally send a brief accountability ping to your team/operator:

```python
def send_accountability(insight):
    msg = f"[Conductor Check] Grounding reminder fired. Self-check: delegating or executing?"
    send_notification(msg)  # Telegram, Slack, email, etc.
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `IDLE_THRESHOLD_SECONDS` | 3600 | Seconds idle before nudging |
| `GROUNDING_INTERVAL` | 7200 | Seconds between grounding reminders |
| `BUSINESS_START_HOUR` | 9 | Start of grounding window (local time) |
| `BUSINESS_END_HOUR` | 19 | End of grounding window |
| `FAILED_BOOP_THRESHOLD` | 10 | Failures before restart |
| `LOCK_TTL` | 900 | Lock file time-to-live (seconds) |
| `INSIGHTS_ROTATION` | 10 | Number of rotating leadership insights |

## Auto-Restart Protocol

When the agent is confirmed unresponsive:

1. **Generate handoff document**
   - Recent git commits
   - Modified files
   - Timestamp and failure count
   - Recovery instructions

2. **Kill frozen session**
   ```bash
   tmux kill-session -t "$session_name"
   ```

3. **Launch fresh iteration**
   ```bash
   ./launch_script.sh
   ```

4. **New session reads handoff**
   - Located in `memories/system/handoffs/HANDOFF-{timestamp}.md`
   - Contains context for continuity

## Example: Status Output

```bash
$ ./autonomy_nudge.sh --status

Civilization: MyAgent
BOOP Counter: 3 / 10
Consolidation Counter: 1 / 10
Failed BOOP Counter: 0 / 10 (restart threshold)
Next BOOP type: simple
BOOPs until consolidation: 7
Consolidations until ceremony: 9
```

## Integration with Scheduled Tasks

The lock system ensures scheduled tasks (training, syncs, reports) don't collide with BOOPs:

```
30-min cycle:
  1. Check lock file
  2. If locked: defer this cycle
  3. If unlocked: acquire lock
  4. Run scheduled task or BOOP
  5. Release lock
  6. Sleep until next cycle
```

This prevents the agent from receiving multiple simultaneous injections that could confuse context.

## Philosophy

The autonomy monitor enforces a meta-cognitive loop:
- **Am I working?** (idle detection)
- **Am I working on the right things?** (grounding check)
- **Am I working in the right way?** (delegation accountability)
- **Am I stuck?** (escalation and restart)

Without this structural enforcement, written rules decay over time. The monitor makes the rules executable.
