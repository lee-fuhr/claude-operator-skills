---
name: qq-audit-tracker
description: Creates and maintains a live Notion tracking doc for audit runs. Standard format with overview table, live feed, per-domain sections, and findings summary. Used by qq-audit-master automatically.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "create audit tracker"
  - "audit tracking doc"
  - "audit notion doc"
---

# Audit tracking doc (Notion)

Create and update a standard Notion tracking doc for live audit runs, recording progress per framework and fix.

Standard format for live audit tracking in Notion. Created at audit start, updated after every framework and fix. The user monitors this doc while agents work autonomously.

---

## When to create

At the start of every audit run (invoked by qq-audit-master). Use your own Notion deliverables/tracking database — set its data source ID in your project config rather than hardcoding one here.

## Page properties

```
Name: "Audit: [Product] — [date]"
Project: [client name or your own org name]
Status: "Draft" → "Final" when complete
Session: [session name]
Notes: "[domain count] domains, [framework count] frameworks, target [N]/10"
Icon: 🔍
```

## Page structure

### 1. Exec summary (very top, before everything)

3-5 sentences. No jargon. What was audited, overall score, biggest problem, improvement from last audit. Updated after each domain completes.

### 2. Overview table

```markdown
<table fit-page-width="true" header-row="true">
  <tr><td>Phase</td><td>Domain</td><td>Score</td><td>Target</td><td>Rounds</td><td>Status</td></tr>
  <tr><td>UX</td><td>UX (N frameworks)</td><td>—</td><td>9.0</td><td>0/3</td><td>⏳ Pending</td></tr>
  ...
</table>
```

Status emoji: ⏳ pending, 🔄 in progress, ✅ score/10, ⚠️ hit max rounds, ⏭️ skipped

### 3. Live feed (reverse-chron, below overview)

Running log of the spiciest findings as each framework and fix completes. Newest at top.

**Entry format:**
```
**HH:MM — [Event name]** ⬆️ old→new
One sentence: the finding or fix that matters most.
→ N fixes applied, N remaining
```

**Rules:**
- Lead with the finding that would make the user say “oh shit”
- Include score change (⬆️ old→new)
- Skip bureaucratic language
- Only log frameworks/fixes that found something

### 4. Per-domain toggle sections

One H1 toggle per domain. Inside each:
- 1-2 sentence exec summary (plain language, no framework names)
- Score trajectory if multiple rounds
- Per-framework score table (if detailed)
- Fixes applied count

```markdown
# UX domain {toggle="true"}

  [Product]’s UX scored 8.8/10 across 20 frameworks. Biggest gap was consistency...

  **Fixes:** 14 changes across 25 files
```

### 5. Findings summary (bottom)

Populated after all domains converge:
- Total findings across all domains
- Total fixes applied
- Remaining items by severity
- Overall quality verdict
- Score table by domain

## Update frequency

- After EVERY framework: update live feed
- After EVERY domain: update overview table + domain section + exec summary
- After ALL domains: populate findings summary
- After re-audit rounds: update with Round 2/3 trajectory

## Integration with qq-audit-master

The master orchestrator should:
1. Call this skill at audit start to create the page
2. Store the page_id for updates
3. Update after each framework via Notion MCP
4. Check for the user’s comments before starting each new domain

## Notion MCP tools used

- `notion-create-pages` — initial creation
- `notion-update-page` with `update_content` — all subsequent updates
- `notion-fetch` with `include_discussions: true` — check for the user’s comments
