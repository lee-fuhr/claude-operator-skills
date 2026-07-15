---
name: ww-notion-proposal-hardener
description: Safe patterns for iterating Notion proposals with inline reviewer comments: verification after patches, uniqueness check before anchoring, comment-preserving rewrites. Load when iterating a reviewed Notion doc.
triggers:
  - notion proposal
  - proposal revision
  - apply comments
  - proposal iteration
  - inline comments notion
metadata:
  filePattern: []
  bashPattern: []
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Notion proposal hardener

The Notion MCP will tell you an edit succeeded when it silently didn’t, and tell you a comment anchor is unique when it isn’t. Trust either response at face value and you’ll ship a revision that looks complete but dropped half its patches, or a comment that anchors to the wrong sentence three paragraphs down. Both failures are invisible until someone reads the live doc closely, usually the reviewer you were revising for. This skill documents the specific ways the API misleads you and the checks that catch it before you call a round done.

Load this skill when iterating a Notion document that has inline reviewer comments (e.g. a proposal with `discussion://` anchors).

---

## The three failure modes

### 1. `update_content` silent skip

`update_content` returns `{"status": "success"}` even when individual `old_str` patches don’t match. The non-matching patches are silently dropped. No error, no indication.

**Common causes:**
- Punctuation mismatch: em dash (`—`) vs semicolon (`;`). Notion auto-converts dashes, and a reviewer editing the live doc in place can leave it out of sync with whatever you fetched
- Bold markup: doc has `**finalized**` but `old_str` has `finalized`
- Discussion span wrappers around the target text (see Failure Mode 3)
- Curly vs straight apostrophes or quotes

**Fix:** Always re-fetch after `update_content` and verify each patch. Never trust the response.

---

### 2. `selection_with_ellipsis` greedy matching

Notion inline comment anchoring uses `start...end` pattern matching that searches the ENTIRE document greedily. If `end` appears more than once anywhere after `start` in the doc, Notion finds multiple valid spans and the comment fails.

**The trap:** Local uniqueness is not enough. A phrase that appears once in your target block can still fail if the same phrase appears anywhere later in the document.

**Fix:** Before anchoring, count how many times the `end` phrase appears in the full document. If more than one, tighten it to a phrase unique to the exact sentence you’re anchoring.

---

### 3. Discussion span wrappers block `old_str`

When a Notion comment is anchored to text, that text gets wrapped: `<span discussion-urls="discussion://abc123">the text</span>`. `update_content`’s `old_str` matching cannot penetrate this wrapper. Even if the text content is identical, the patch silently skips.

**Detection:** Fetch with `include_discussions: true`. Look for `<span discussion-urls=` around your target text.

**Fix options (in priority order):**
1. **Include the span markup in `old_str`**: match the full `<span discussion-urls="discussion://...">exact text</span>`. The span disappears in the output (the comment anchor is lost but the edit applies cleanly).
2. **Fall back to `replace_content` for that block**: rewrites the paragraph, destroying the comment anchor.
3. **Skip the content edit**: if the thread matters more than the edit, document the change in a page-level comment instead.

---

### 4. Comment reads are incomplete (silent under-return)

`notion-get-comments` and the REST `GET /comments?block_id=X` **silently omit comments**: they return an empty list for a block that visibly has an open comment in the UI, with no error. An empty result is indistinguishable from “no comments here,” so a full block-by-block sweep can look exhaustive and still miss threads.

**Observed in production:** a live reviewer comment on a callout returned zero results across two different Notion API versions, while comments on blocks the integration itself had created returned fine. Not a version issue: the endpoint genuinely can’t surface some comments (best guess: comments on blocks the integration didn’t create, or older UI-anchored inline comments).

**Fix:** treat the API comment list as a FLOOR, never the complete set. Never claim “I read all the comments” from the API alone. State the count as *API-visible only* and confirm completeness: ask the doc owner for their own count, or a screenshot of the comment sidebar. The rendered panel, or their screenshot, is ground truth.

---

## Standard iteration workflow

One complete round: read comments → plan patches → pre-flight → apply → verify.

```
STEP 1: READ COMMENTS
notion-get-comments(page_id, include_all_blocks: true)
→ Map each comment to its anchor text
→ Identify which threads are open vs resolved

STEP 2: FETCH CURRENT CONTENT
notion-fetch(page_id, include_discussions: true)
→ Note which lines have <span discussion-urls= wrappers
→ Get exact current text (punctuation, dashes, bold markup) for every line you plan to patch

STEP 3: PRE-FLIGHT
For each planned patch:
  a. Does your old_str match the EXACT current text? (check dashes, bold, apostrophes)
  b. Is the target text wrapped in a discussion span? If yes, use the span-aware pattern below.

For each planned inline comment:
  a. Count occurrences of the end phrase in the full document
  b. If end appears > 1 time: pick a tighter end phrase from the same sentence
  c. Only proceed when (start, end) yields exactly one valid span

STEP 4: APPLY PATCHES
Single update_content call with all patches batched.

STEP 5: VERIFY (mandatory)
Re-fetch immediately.
For each patch:
  ✓ old_str absent AND new_str present → patch applied
  ✗ old_str still present → patch failed (report likely cause)
Report every failure. Do not mark a round complete until all patches verified.
```

---

## Span-aware patching

When a line has a `<span discussion-urls=` wrapper, use the wrapper verbatim in `old_str`:

```
Fetched content shows:
  Some text before. <span discussion-urls="discussion://abc123">finalized framework; cohesive</span> and more text.

Your old_str:
  <span discussion-urls="discussion://abc123">finalized framework; cohesive</span>

Your new_str:
  finalized framework, cohesive, ready for use
```

The span is in `old_str`, absent from `new_str`. Notion replaces the span-wrapped text with plain new text. The inline comment thread loses its anchor (the discussion-url is gone), but the edit lands cleanly.

**Note:** The discussion_id still exists in Notion’s comment system. It just loses its visual anchor in the doc. The doc owner will still see the comment in the comments panel.

---

## Comment-safe full rewrite (version bump)

When `replace_content` is unavoidable (major restructure, new version):

```
BEFORE replace_content:
1. notion-get-comments(page_id, include_all_blocks: true)
2. Record each thread:
   - discussion_id
   - anchor_text (original selection)
   - thread summary (what the comment said + any replies)
   - resolved? (yes/no)

APPLY replace_content with new version content.

AFTER replace_content:
3. Post ONE page-level summary comment:
   "---
   Version [N] changes applied. Comment threads that lost anchors:

   • "[original anchor text]": [one-line thread summary]
   • "[original anchor text]": [one-line thread summary]

   Threads already resolved: [list or 'none']
   ---"
```

This gives the doc owner an explicit record of what was lost and whether it matters. They can decide which lost threads need re-anchoring on the new content.

---

## Uniqueness scan (inline)

Before posting a `notion-create-comment` with a `selection` anchor, do this scan inline:

1. Fetch page content as plain text
2. Find all positions of `end_phrase` in the document
3. Find all positions of `start_phrase` before those end positions
4. If there is more than one valid (start before end) pair: the anchor is ambiguous

**Tightening the end phrase:** Pick trailing text from the SAME sentence as your selection. Generic phrases (“own content,” “the work,” “phase two”) appear throughout a proposal. Never use them as the end anchor.

**Good end phrase:** the last five to eight words of the specific sentence you’re anchoring, as long as that exact phrase only appears once in the document.

---

## Quick reference

| Situation | Right approach | Failure mode to watch |
|-----------|---------------|----------------------|
| Surgical edit, no comment anchor | `update_content` | Silent skip; verify after |
| Surgical edit, line has comment anchor | `update_content` with span markup in `old_str` | Span wrapper breaks plain `old_str` |
| Multiple edits, some anchored | Batch in one `update_content` call | Each patch verified independently after |
| Major version bump | `replace_content` + pre-save threads | Nukes all inline anchors, document them first |
| Post inline comment | `notion-create-comment` with `selection` | Greedy ellipsis; count end-phrase occurrences first |
| Check if patch applied | `notion-fetch` → scan for `old_str` | API success ≠ patch applied |

---

## Known MCP ceiling: block-level anchoring only

The Notion MCP’s `selection_with_ellipsis` anchors comments at the **block level**: the whole paragraph, bullet, or callout. It identifies *which block* to pin the comment to, but it cannot target specific words or characters within a block.

The Notion UI supports character-offset anchoring (highlight “off-peak data,” comment on exactly those two words). The MCP does not expose character offsets. There is no way to replicate this through the current MCP tools.

**Practical consequence:** One comment per block, maximum. If you need to comment on two different phrases within the same paragraph, use a page-level comment that quotes both phrases inline.

**Workaround:** Break long paragraphs into shorter blocks before commenting, so each sentence or idea becomes its own block, and thus its own commentable unit. This is only practical when you control the doc structure.

**Mandatory comment style when targeting sub-block text:** Because the anchor highlights the whole block, the comment text MUST quote the specific phrase being addressed. Without a quote, the reader has no idea which part of the paragraph the comment is about.

```
❌ "This sentence should be on the homepage."
   (reader sees the whole paragraph highlighted, which sentence?)

✓ "'You've been paying peak rates for off-peak data.' should be on
   the homepage. Clearest single-line indictment of the status quo."
```

Always lead with the quoted phrase in single curly quotes, then the comment. No exceptions when the target block has more than one sentence.

This is a hard MCP limitation, not a selection-precision issue. All discussions return `context="block"`.

## Working alongside a general Notion working-doc standard

If your own setup keeps a separate skill or convention for general Notion working-doc standards (changelog pattern, deliverables tracking, page structure), load that one for the baseline, and load this skill specifically when you’re in a comment-iteration loop on a reviewed proposal and need patches to actually land.
