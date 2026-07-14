---
title: "copy-sweep: blocks AI-tell punctuation before it lands in a file"
permalink: /copy-sweep/
description: A PreToolUse hook that blocks em dashes, straight quotes, and Title Case headings before they land in a file. The write fails before the tell ever exists, no cleanup pass needed.
---

# copy-sweep

**The problem:** AI-tell punctuation and phrasing creep into drafts one write at a time. The usual fix is a cleanup sweep after the fact, catch what you can, hope you got it all. copy-sweep skips the sweep: the write fails before the tell ever exists.

**The result:** AI-tell punctuation caught at write time, not cleaned up after. Found 272 em dashes in this repo's own README the first time it ran.

## What it catches

Deterministic, zero model calls: em dash budget, straight quotes, Title Case headings, banned corporate-speak, throat-clearing openers, summary crutches. Semantic checks (vague pronouns, rule-of-three, pontificating) are off by default and need a model call.

Full check list, config reference, and install steps: [repo README → copy-sweep](https://github.com/lee-fuhr/claude-operator-skills#copy-sweep).

[← back to all skills](../)
