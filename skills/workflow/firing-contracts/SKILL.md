---
name: firing-contracts
version: 1.0.0
description: Ensure every tool, skill, and process is wired into the workflow, not just built. A tool without wiring is a tool that does not exist.
category: workflow
tags: [wiring, automation, system-integration, operations]
author: Lyra (AI-CIV)
compatibility: [claude-code, general]
dependencies: []
---
# Firing Contracts: The Wiring Specification

## Core Insight

"A tool without wiring is a tool that doesn't exist."

Having a script in /tools/ means nothing if nothing brings it into the AI's context at the right moment. The fire extinguisher needs to be in the path of the crisis, not on the wall in the hallway.

## What Is a Firing Contract

Not documentation. Not a README. The firing contract IS the wiring that guarantees a system activates at the right moment.

Every tool, skill, process, agent, or integration needs four things to be true simultaneously:

| Component | Question | Example |
|-----------|----------|---------|
| TRIGGER | What condition makes this relevant? | "Monday 5 PM EST" or "new email from guestpostlinks" |
| INSERTION | What mechanism puts it in the AI's context? | BOOP step, cron, hook, skill trigger |
| EXECUTION | What makes the AI actually run it? | Conditional in sprint-mode, explicit instruction |
| EVIDENCE | How do we verify it fired? | Log entry, state file, Telegram notification |

## Certainty Hierarchy

| Mechanism | Certainty | When to Use |
|-----------|-----------|-------------|
| BOOP step | Very high | Recurring tasks, health checks, daily ops |
| Cron/scheduler | Very high | Time-based tasks that must fire regardless of AI state |
| Claude Code hook | Very high | Event-driven (file changes, tool calls) |
| Skill frontmatter trigger | Medium | Keyword-activated skills in conversation |
| CLAUDE.md mention | Medium | Session-start awareness (may forget mid-session) |
| Memory file | Low | Only found if agent searches memory |
| Just exists in tools/ | Very low | Effectively invisible |

If your firing contract's insertion mechanism is "exists in tools/" you don't have a contract, you have a wish.

## How to Write a Firing Contract

Add this frontmatter block to every tool, skill, or process file:

```yaml
---
firing_contract:
  trigger: "Monday 5 PM EST"
  insertion: "boop_loop.sh line 1285, scheduled-task injection"
  execution: "scheduled_tasks.py marks due, boop injects into lyra-primary"
  evidence: "Bitrix task IDs logged, Ashley notified via Telegram"
  health_check: "If no Bitrix tasks created by 5:30 PM Monday, alert Nathan"
  last_verified: "2026-04-20"
---
```

## When to Invoke This Skill

- Before marking ANY new tool as "shipped"
- When a tool exists but isn't firing in production
- During weekly audits of system health
- When debugging "why didn't X run?"
- When building new BOOP tasks or scheduled processes

## The Audit

For each system with a firing contract, verify:
1. Did the trigger condition occur? (check logs, timestamps)
2. Was the system inserted into context? (check boop injection, skill loading)
3. Did it execute? (check output files, state changes)
4. Is there evidence? (check logs, notifications)

If any step fails, the firing contract is broken. Fix the wiring, not the tool.

## Applies To Everything

| System Type | Example | Firing Contract Needed? |
|-------------|---------|----------------------|
| Tools/scripts | google_ads_report.py | Yes: when does it run, what triggers it |
| Skills | expert-review-panel | Yes: what keyword loads it, when is it relevant |
| Processes | WGG Monday process | Yes: what starts it, what verifies completion |
| Agents | dormant agents | Yes: what activates them, what's the trigger |
| Memory | agent-learnings files | Yes: what prompts reading them back |
| Integrations | Brevo automations | Yes: what health-checks them |
| Monitors | yrcharisma scanner | Yes: what verifies it's running |

## The Meta-Loop

The firing contract system itself needs a firing contract:
- TRIGGER: weekly audit cycle
- INSERTION: boop_loop.sh evolution cycle
- EXECUTION: firing_audit.py checks evidence for all contracts
- EVIDENCE: audit report in deliverables/

The bottom turtle is cron/OS. That's ground truth.

## Key Quote

"Shipped means wired, not just written."
