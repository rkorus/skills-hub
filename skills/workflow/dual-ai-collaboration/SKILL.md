---
name: dual-ai-collaboration
version: 1.0.0
description: 8 battle-tested collaboration patterns for AI-to-AI teamwork. Pre-flight checks, context snapshots, proof ledgers, contradiction detection, and more.
category: workflow
tags: [collaboration, multi-agent, handoff, coordination]
author: Lyra (AI-CIV)
compatibility: [claude-code, general]
dependencies: []
---
# Dual-AI Collaboration Skills

8 battle-tested skills from real AI-to-AI collaboration at Pure Technology.

## Skill 1: Pre-Flight Check

Before starting ANY shared task or touching shared infrastructure, post:

```
PRE-FLIGHT: [AI-name] about to [action] on [target]
Affects: [what could break]
ETA: [how long]
Objections? 60 second window.
```

Five questions for standard tasks:
1. What am I about to build/do?
2. What files/systems will I touch?
3. What is my ETA?
4. Is anyone else working on something that overlaps?
5. What do I need from the other AI before I start?

No response in 60 seconds = proceed.

## Skill 2: Context Snapshot

5-field handoff for every task pass:

```
WHAT:    One sentence describing the task
WHERE:   Exact file paths, URLs, endpoints
STATE:   Done / in progress / not started
GOTCHAS: Anything surprising or non-obvious
VERIFY:  How to confirm correctness (curl command, expected output)
```

## Skill 3: Parallel Review Protocol

When reviewing another AI's work, answer 3 questions:

```
REVIEW: [task name]
Reviewer: [AI-name]

1. Does it work?
   [Test the actual output, not the code. Click the links. Load the page.]

2. Is anything missing?
   [Compare against the original requirements. Check every item.]

3. What would I do differently?
   [Not criticism -- constructive improvement.]
```

The non-builder reviews BEFORE the human sees it.

## Skill 4: Proof Ledger

Running log of completed work with evidence:

```
[timestamp] [AI-name] | [task] | [proof] | [status]
```

Example:
```
[14:30] Athena | Video clip render    | Trello link, 64s, 720x1280        | VERIFIED
[14:45] Lyra   | Homepage v4 deploy   | purebrain-funnels.vercel.app/home-v4 200 | VERIFIED
```

No proof = not done. Non-negotiable.

## Skill 5: Contradiction Detector

When you spot a discrepancy, flag immediately:

```
CONTRADICTION FLAG:
[AI-1] said [X].
My records show [Y].
Source: [where I got my number].
@human which is current?
```

Never let conflicting numbers reach the human unchallenged.

## Skill 6: Context Handoff Protocol

Before ending any session where work continues:

```
CONTEXT HANDOFF -- [date] [AI-name]
================================

WHAT I WAS WORKING ON:
  [One paragraph describing the task and current approach]

WHAT IS DONE:
  - [Completed item 1 with file path or URL]
  - [Completed item 2 with verification proof]

WHAT IS UNCERTAIN:
  - [Decision I made but am not confident about]
  - [Assumption I am working under that may be wrong]

WHAT THE NEXT AI SHOULD KNOW FIRST:
  - [The single most important thing]
  - [Gotcha that will waste 20 minutes if not flagged]
```

Write to a persistent file, not just conversation. Files survive compaction.

## Skill 7: Disagreement Signal

When AIs disagree, show the full debate:

```
DISAGREEMENT: [topic]

AI-1 position: [approach A] because [reason]
AI-2 position: [approach B] because [reason]

Tradeoffs:
  Option A gives us [benefit] but costs [downside]
  Option B gives us [benefit] but costs [downside]

Decision needed from: @human
```

Never resolve privately. The debate IS the value.

## Skill 8: Uncertainty Flag

```
UNCERTAIN: [statement or decision]
Confidence: [low / medium]
What would help: [specific info or verification needed]
```

Two AIs with calibrated uncertainty are more reliable than two AIs with false confidence. Say "I don't know" loudly -- always better than being confidently wrong quietly.
