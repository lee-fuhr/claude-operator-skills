---
name: ww-notion-docs
description: Working with Notion documents via the Notion MCP. Covers Notion’s custom markdown syntax, content updates, tables, callouts, highlighting, database pages, and the comments-based review workflow. Load this before ANY Notion content work.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Notion docs

**The problem:** Notion’s block editor does not speak standard markdown. Pipe tables silently fail to render. Escaped `\n` sequences show up as literal backslash-n in the page instead of a line break. Curly braces meant to set a block color end up as visible text if they get escaped wrong. None of these fail loudly, they just fail quietly, and you don’t find out until you look at the page and something is broken.

This skill documents Notion’s actual markdown flavor so content stops silently failing to render right, plus the update patterns (fetch-before-edit, `update_content` vs `replace_content`) and the comments-based review workflow that make Notion usable as a real collaboration surface instead of a one-way publish target.

## When to use

- Creating or editing content in Notion pages
- Building deliverables in a Notion database
- Formatting tables, callouts, or highlighted content in Notion
- Reading and responding to a reviewer’s block comments on Notion pages
- Any task that touches Notion content via MCP

## Step 0: Fetch the markdown spec (mandatory)

Notion uses its OWN markdown flavor, not standard markdown. Before writing any content:

```
ReadMcpResourceTool → server: "Notion" (or whatever your Notion MCP connection is named), uri: "notion://docs/enhanced-markdown-spec"
```

Do this every session. Don’t rely on memory of the spec. It’s cheap and prevents silent formatting failures.

## Notion markdown reference

### What’s different from standard markdown

- **Tables:** `<table>` HTML tags, NOT pipe `|` tables. Pipe tables silently fail to render.
- **Callouts:** `<callout icon="emoji" color="Color">` tags, with Notion markdown inside (not HTML).
- **Background colors:** `{color="yellow_bg"}` at end of a block, or `<span color="yellow_bg">text</span>` inline.
- **Empty lines:** Stripped by Notion. Use `<empty-block/>` when you need vertical space.
- **Dividers:** `---`
- **Escape these characters:** `\ * ~ ` $ [ ] < > { } | ^`, all need backslash escaping in body text.

### Available background colors

`gray_bg`, `brown_bg`, `orange_bg`, `yellow_bg`, `green_bg`, `blue_bg`, `purple_bg`, `pink_bg`, `red_bg`

### Tables

```
<table header-row="true">
	<tr>
		<td>Header 1</td>
		<td>Header 2</td>
	</tr>
	<tr>
		<td>Data</td>
		<td>Data</td>
	</tr>
</table>
```

### Callouts

```
<callout icon="⚠️" color="yellow_bg">
	Content here. Use Notion markdown inside, not HTML.
</callout>
```

### Highlighting changes (diff-style)

When asked to highlight changes or show what’s new:
- **Block-level:** `{color="yellow_bg"}` at end of changed blocks
- **Inline:** `<span color="yellow_bg">changed text</span>` for changes within unchanged blocks
- Yellow is the default highlight color for changes

## Content update patterns

### Fetching before editing (mandatory)

ALWAYS `notion-fetch` the page before doing `notion-update-page` with `update_content`. The `old_str` must match the page’s current content exactly. Stale strings won’t match and the update silently fails.

### `replace_content` vs `update_content`

| Method | Use when | Risk |
|--------|----------|------|
| `replace_content` | New page, or full rewrite you control | Blows away ALL existing content including reviewer edits |
| `update_content` | Targeted edits to specific sections | Safe. Only touches matched strings |

**Default to `update_content`.** Only use `replace_content` for pages you just created or when a full rewrite is explicitly intended.

### Newlines must be real

The `new_str` parameter (and `replace_content` body) must use REAL newlines, not `\n` escape sequences. Escaped newlines render as literal `\n` text in Notion.

## Working with databases

### Creating pages in databases

- Use `data_source_id` (not `database_id`) when the database has multiple data sources
- Property values must match the database schema exactly (select values must be from the allowed list)
- Fetch the database first to see the schema and allowed property values

### Example: a deliverables database schema

A reasonable shape for a database of client-facing deliverables and review workflow, if you’re setting one up from scratch:

- **Properties:**
  - Name (title)
  - Client
  - Type (select): whatever categories fit your work, e.g. “Positioning audit”, “Messaging framework”, “Stakeholder questions”, “Kickoff plan”, “Proposal”, “Draft”, “Interview questions”, “Marketing strategy”, “Content calendar”
  - Status (select)
  - Session
  - Source file
  - Shared with
  - Notes

Find your own database’s `data_source_id` by fetching it first, and swap it in wherever this skill (or a skill that calls into it) references one.

## Comments workflow (review cycle)

The reviewer comments on blocks in Notion. Claude reads and responds via MCP.

1. **Read comments:** `notion-get-comments` with `include_all_blocks: true`
2. **Comments include `text-context`** showing which text they’re anchored to
3. **Process each comment** as feedback on that specific block
4. **Apply changes** via `update_content`, using the `text-context` to locate the right section
5. **Add contextual comments on EVERY change.** The reviewer cannot see what changed without them. This is the primary way they review your work. Every content update, no matter how small, gets a comment explaining what changed and why, anchored to the changed text.
6. **Reply to the reviewer’s comment threads** explaining how you addressed each one

**Comments are not optional. They ARE the review interface.** The reviewer reads the doc in Notion and sees Claude’s comments explaining changes. Without comments, changes are invisible and the reviewer has to re-read the entire document to find what moved. That’s unacceptable cognitive load.

**When to add comments:**
- After every `update_content` call: comment on the changed text
- After every `replace_content` call: comment on each major section that changed
- When replying to feedback: reply in the thread AND add a new comment on the updated text
- Even for “small” fixes (typos, rate changes, term swaps): add a comment

This is the preferred review workflow for deliverables. Don’t ask the reviewer to paste feedback into chat.

### Archive full text rule

When archiving previous versions below the current content, include the **full text** of each version, not just a summary. Reviewers use the archive for reference and comparison. One-line descriptions are not enough.

## Page icons

Always set a relevant emoji icon on every Notion page you create. Pick an icon that matches the content type:

| Content type | Icon |
|-------------|------|
| Proposal / pitch | 🤝 |
| Strategy / brainstorm | 💡 |
| Audit / analysis | 🔍 |
| Messaging framework | 🎯 |
| Interview questions | 🎤 |
| Content calendar | 📅 |
| Kickoff / project plan | 🚀 |
| Draft (general) | ✏️ |
| Meeting notes | 📝 |
| Pricing / financial | 💰 |
| Competitive analysis | ⚔️ |

Set via the `icon` parameter on `create-pages` or `update-page`. Never leave the default blank page icon.

## Document versioning and evolution

### When to use `replace_content` (full rewrite)

Use `replace_content` when:
- The document has 3+ layers of revision patches that need merging into one clean version
- Structural reorganization (heading hierarchy changes, section reordering)
- The page has no child pages or databases that would be destroyed

After a full rewrite, add tightly contextual comments (see below) explaining each major change.

### Prepend pattern (adding content at the top)

When you need to add new content at the beginning of an existing page without replacing everything:

1. Fetch the page to get the exact first content block
2. Use `update_content` with `old_str` matching that first block
3. Set `new_str` to: new content + original first block

This effectively prepends without touching the rest of the page. Safe for pages with active comments (comments on untouched blocks survive).

### Version separators

When archiving previous versions below current content:
- Add **5+ `<empty-block/>` tags** before the archive section
- Follow with `---` divider
- Add a clear heading: `## Previous versions (archive)`
- List each version with date and one-line summary of changes
- Old content follows below, clearly separated

### Comments must be contextual

**Anchor comments to specific selected text**, not whole sections or headings. Use `selection_with_ellipsis` with ~10 chars from start + ellipsis + ~10 chars from end. Comments explain what changed and why at the exact point of change.

Bad: comment on `## Engagement model` heading saying “this section was rewritten”
Good: comment on `fixed price, not...based rate` saying “v4.0: Replaced commitment-discounted rate language. Fixed-price for deliverables, not time-based billing.”

### Comment identity

Some Notion integrations (including the official Claude integration) show comments under their own name and icon, distinct from the human reviewer’s comments. Check what your specific integration shows before assuming you need to prefix comments with “Claude:”. If the identity is already visible in the Notion UI, a prefix is redundant.

## Common mistakes (avoid these)

1. **`\n` literals instead of real newlines.** Content renders as one giant block. Every newline must be an actual line break in the string.
2. **Pipe tables `| Col |`.** They don’t render in Notion. Use `<table>` tags.
3. **Skipping the fetch before `update_content`.** `old_str` won’t match current content. Always fetch first.
4. **Using `replace_content` when `update_content` would work.** Destroys reviewer edits. Default to `update_content`.
5. **Unescaped brackets in body text.** `[audience]` must be `\[audience\]` or Notion interprets it as a link/mention.
6. **Not fetching the markdown spec.** The spec may evolve. Fetch it, don’t guess.
7. **Block colors are treacherous.** `{color="yellow_bg"}` is a block attribute. `replace_content` preserves existing block colors. `update_content` that includes `{color="default"}` can work to clear colors, but if the braces get escaped they become visible literal text `\{color="yellow_bg"\}` in the document. **Safest approach:** Avoid setting block colors unless you plan to manage them carefully. If you must clear a block color, use `{color="default"}` via update_content. If literal escaped color tags appear in content, match them with escaped braces in old_str: `\\{color="yellow_bg"\\}`.
8. **Emoji vs. a real icon set.** If your reviewer prefers a proper line-icon set over emoji, source an icon URL from whatever icon service you use and pass it as the `icon` parameter on `create-pages` or `update-page` instead of an emoji character.
