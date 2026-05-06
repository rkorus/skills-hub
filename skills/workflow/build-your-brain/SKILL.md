---
name: build-your-brain
version: 1.0.0
description: Set up a persistent AI brain using cloud storage. Covers folder structure, daily feeding habits, retrieval preflight, and weekly maintenance.
category: workflow
tags: [memory, knowledge-management, context, productivity]
author: Lyra (AI-CIV)
compatibility: [claude-code, general]
dependencies: []
---
# Build Your Brain: Never Lose Context Again

Your AI is only as good as what it remembers. Without a structured brain, every session starts from zero. You re-explain your business, your preferences, your past decisions. With a brain, your AI compounds knowledge over time like a team member who never forgets.

This skill has four parts: Build, Feed, Check, Grow.

---

## 1. Build Your Brain (One-Time Setup, ~15 minutes)

**Pick your storage.** Google Drive, Dropbox, OneDrive, or a local folder all work. The only requirement: your AI can access it.

**Create this folder structure:**

```
/brain/
  deliverables/    -- Everything you or your AI produces
  learnings/       -- What you have discovered (domain knowledge, research)
  references/      -- External docs you rely on (brand guides, templates, SOPs)
  context/         -- Business info that rarely changes (brand voice, goals, team)
  skills/          -- Reusable processes (how to write a newsletter, how to onboard)
```

**Then add your starter context.** Drop these into `/brain/context/`:
- A one-page summary of your business
- Your brand voice notes
- Your team roster
- Your current goals

---

## 2. Feed Your Brain (Daily Habit, ~2 minutes per item)

Every time you complete work, save it. Every time you learn something, write it down. **If it took effort to create or discover, it goes in the brain.**

| After this... | Save to... | Example filename |
|---------------|-----------|-----------------|
| Finishing a deliverable | `/brain/deliverables/` | `2026-04-30-client-proposal-acme.md` |
| A meeting | `/brain/learnings/` | `2026-04-30-client-wants-q3-pivot.md` |
| Finding a useful template | `/brain/references/` | `email-welcome-sequence-template.md` |
| Making a mistake | `/brain/learnings/` | `2026-04-30-never-send-invoices-friday.md` |
| Creating a repeatable process | `/brain/skills/` | `how-to-write-a-case-study.md` |

**Naming convention:** Use `YYYY-MM-DD-topic` for time-sensitive items. Use plain descriptive names for evergreen items.

---

## 3. Check Your Brain Before Every Task (Retrieval Preflight)

This is the most valuable habit. Before starting ANY new task, search your brain first. It takes 30 seconds and prevents hours of wasted work.

**The four questions:**

1. **Does a deliverable for this already exist?** Search `/brain/deliverables/`
2. **Is there a documented process?** Search `/brain/skills/`
3. **What have I learned about this topic?** Search `/brain/learnings/`
4. **Are there relevant reference docs?** Search `/brain/references/`

**What this prevents:**
- Rebuilding something that already exists
- Contradicting a decision you made last month
- Repeating a mistake you already documented
- Starting from scratch when a template exists

---

## 4. Grow Your Brain (Weekly, ~10 minutes)

Once a week:
- **Organize:** Move any files dumped in the wrong folder
- **Archive:** Move outdated items to `/brain/_archive/`
- **Fill gaps:** If you worked on a topic three times but have no brain doc, write one
- **Review learnings:** Skim this week's entries for patterns worth capturing as skills

---

## Quick-Start Checklist

- [ ] Choose your storage platform
- [ ] Create the 5 folders
- [ ] Add your business summary to `/brain/context/`
- [ ] Add your brand voice notes to `/brain/context/`
- [ ] Save your next completed deliverable to `/brain/deliverables/`
- [ ] Before your next task, run the 4-question preflight check
- [ ] Set a weekly 10-minute calendar reminder for brain maintenance

---

## Why This Works

The average knowledge worker spends 1.8 hours per day searching for information they have seen before (McKinsey). An AI without persistent memory starts from absolute zero every session.

A structured brain turns your AI from a stateless tool into a compounding asset. After 30 days, your AI will know your business well enough to produce first-draft work that needs minimal editing.

The brain is the difference between "AI that helps" and "AI that knows you."
