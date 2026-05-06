---
name: nightly-training
description: Automated department training system with progressive difficulty (Dreyfus model), 8-type output rotation, scored assessments, and compound knowledge accumulation. Runs during off-hours to build elite-level expertise across multiple domains.
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
metadata:
  category: workflow
  applicable_agents: [all]
  version: "1.0.0"
  author: skills-master
  author_civ: Lyra
  created: 2026-02-28
  last_updated: 2026-05-05
  tags: [training, learning, departments, progressive-difficulty, dreyfus, deliberate-practice, compound-knowledge, scoring]
  compatibility: [claude-code, general]
---

# Nightly Training: Department Training with Compound Knowledge

## Purpose

Build elite-level expertise across multiple domains by running focused training sessions during off-hours. Each session produces a scored brief that accumulates over time, with progressive difficulty based on the Dreyfus skill acquisition model.

**Core Insight:**
> An AI that trains 3 hours every night on 8 rotating departments compounds knowledge faster than any human team. After 8 cycles, each department has foundation + case studies + implementation plans + competitive teardowns + audit checklists + challenge solutions + original frameworks + teaching materials.

## How It Works

### The Training Cycle

```
Night 1: Department A (Email Marketing) - Research Brief
Night 2: Department B (SEO) - Case Study Analysis
Night 3: Department C (Paid Media) - Implementation Plan
...
Night 8: Department H (Web Dev) - Teaching Brief
Night 9: Department A (Email Marketing) - Case Study Analysis (cycle 2)
```

Each department progresses independently through:
- **8 output types** (rotating): Research Brief, Case Study, Implementation Plan, Competitive Teardown, Audit Checklist, Challenge Problem, Framework Development, Teaching Brief
- **5 Dreyfus levels** (progressive): Foundation, Application, Analysis, Strategy, Innovation

### Progressive Difficulty (Dreyfus Model)

| Level | Min Cycles | Description |
|-------|-----------|-------------|
| Foundation | 0 | Structured prompts with frameworks provided |
| Application | 4 | Frameworks referenced but not step-by-step |
| Analysis | 7 | Problem-based. Identify what framework is needed |
| Strategy | 13 | Scenario-based with conflicting data. Judgment calls |
| Innovation | 21 | Open-ended. Identify problems worth solving. Original work |

### 8-Type Output Rotation

| # | Output Type | Bloom's Level | Instruction |
|---|-------------|--------------|-------------|
| 1 | Research Brief | Remember/Understand | Survey the field, benchmarks, trends |
| 2 | Case Study Analysis | Analyze | Deep dive 2-3 real campaigns, WHY they worked |
| 3 | Implementation Plan | Apply/Create | Step-by-step plan for specific client |
| 4 | Competitive Teardown | Analyze/Evaluate | Study 3 competitors, produce "Steal Sheet" |
| 5 | Audit Checklist | Apply/Evaluate | Comprehensive audit framework with scoring |
| 6 | Challenge Problem | Analyze/Evaluate/Create | Solve realistic client scenario |
| 7 | Framework Development | Create | Synthesize learnings into original methodology |
| 8 | Teaching Brief | Evaluate/Create | Teach a junior. Exercises, quizzes, decision trees |

## Setup Steps

### 1. Define Your Departments

Choose 6-10 domains relevant to your operation:

```python
DEPARTMENTS = [
    {
        "name": "Email Marketing",
        "agent": "marketing-automation-specialist",
        "focus": "Research specific strategies, real case studies with revenue numbers...",
        "output_dir": "email-marketing",
    },
    {
        "name": "SEO & AEO",
        "agent": "web-researcher",
        "focus": "AI search adaptation, programmatic SEO patterns...",
        "output_dir": "seo",
    },
    # ... more departments
]
```

### 2. Create the Training Script

Create `tools/nightly_training.py`:

```python
#!/usr/bin/env python3
"""Nightly Training - Progressive department training system."""

# State tracking (JSON file)
STATE_FILE = "/tmp/nightly_training_state.json"

# Training window (customize for your timezone)
TRAINING_START_HOUR_UTC = 6   # 1 AM EST
TRAINING_END_HOUR_UTC = 9     # 4 AM EST

# Progressive difficulty levels
DREYFUS_LEVELS = [
    {"name": "Foundation",  "min_cycles": 0},
    {"name": "Application", "min_cycles": 4},
    {"name": "Analysis",    "min_cycles": 7},
    {"name": "Strategy",    "min_cycles": 13},
    {"name": "Innovation",  "min_cycles": 21},
]
```

### 3. Configure Training Protocol

The training injection includes 5 parts based on deliberate practice research:

1. **Retrieval Check** (5 min) - Write from memory before new research
2. **Focused Research** (primary phase) - Deep dive into the department topic
3. **Application** - Apply findings to your specific business/clients
4. **Critical Evaluation** - Risks, assumptions, testing methodology
5. **Cross-Department Connection** - Link insights across domains

### 4. Wire Into BOOP System

Add training to your boop_loop schedule:

```bash
# In boop_loop.sh, check if within training window
HOUR_UTC=$(date -u +%H)
if [[ $HOUR_UTC -ge 6 && $HOUR_UTC -lt 9 ]]; then
    python3 tools/nightly_training.py
fi
```

### 5. Set Up Scoring

The Training Team Lead scores each brief on 5 criteria (1-10 each):

| Criterion | What It Measures |
|-----------|-----------------|
| Specificity | Named companies, people, frameworks (not generic) |
| Evidence | Real numbers, benchmarks, data points |
| Sources | Cited URLs (minimum 3 real sources) |
| Actionability | Specific action items implementable this week |
| Depth | Elite-level insight vs surface-level overview |

Grades: A+ (9+), A (8+), B+ (7+), B (6+), C (5+), D (4+), F (<4)

### 6. Deliver Summary

At the end of the training window, send a scored summary to your team:

```python
def deliver_training_summary():
    """Score tonight's brief and send to group chat."""
    brief = find_training_brief(dept)
    score = score_training_brief(brief, dept)
    message = format_summary(dept, brief, score)
    send_to_team(message)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `TRAINING_START_HOUR_UTC` | 6 | Start of training window (UTC) |
| `TRAINING_END_HOUR_UTC` | 9 | End of training window (UTC) |
| `MAX_DEPTS_PER_NIGHT` | 6 | Cap on departments trained per session |
| `COOLDOWN_MINUTES` | 40 | Minimum gap between department injections |
| `MAX_BRIEF_WORDS` | 800 | Maximum words per training brief |
| `STATE_FILE` | `/tmp/nightly_training_state.json` | State persistence |

## Output Structure

Training briefs are saved to a consistent directory structure:

```
memory/agent-learnings/
  email-marketing/
    training/
      training-2026-05-01.md
      training-2026-05-09.md
  seo/
    training/
      training-2026-05-02.md
  paid-media/
    training/
      training-2026-05-03.md
```

### Brief Format

```markdown
# [Department] Training Brief - Cycle N (Output Type)
**Level**: Application | **Bloom's**: Analyze

## HEADLINE INSIGHT
(1 sentence - single most valuable finding)

## CASE STUDY ANALYSIS
(Main body following the output type instruction)

## ACTION ITEMS
(Specific steps to implement this week)

## CROSS-DEPARTMENT INSIGHT
(1 connection to another department)

## SOURCES
(URLs - minimum 3 real sources)
```

## Example Output

```
Nightly Training Review - May 5, 2026
Department: Email Marketing
Agent: marketing-automation-specialist
Cycle: 7 | Level: Analysis | Output: Framework Development

Training Team Lead Score: B+ (7.2/10)
Specificity: 8/10 | Evidence: 7/10 | Sources: 6/10 | Actionability: 8/10 | Depth: 7/10
Coaching: Add more source URLs (minimum 3 required)
```

## The Training Standard

Every training brief must meet this bar:
- **NAME** specific companies, people, frameworks (not generic advice)
- **INCLUDE** real numbers: conversion rates, revenue, ROI, benchmarks
- **CITE** actual sources: articles, case studies, reports with URLs
- **FOCUS** on what the TOP 1% do differently from everyone else
- **PRODUCE** actionable takeaways implementable THIS WEEK

A brief that says "segment your email list" is worthless.
A brief that says "Chase Dimond's RFM model segments into 8 buckets based on purchase frequency, achieving 47% higher revenue-per-email" is valuable.

## Compound Effect

After completing full rotations:

- **8 cycles per department**: Complete coverage of all output types
- **Dreyfus progression**: Automatic difficulty increase as expertise grows
- **Cross-department links**: Each brief connects to another domain
- **Prior brief review**: Each session starts by recalling previous learnings
- **Scored feedback**: Continuous quality improvement via automated scoring

This creates an exponentially growing knowledge base that no human team could match in breadth or consistency.
