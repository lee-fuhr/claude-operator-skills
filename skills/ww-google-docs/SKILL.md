---
name: ww-google-docs
description: Creates and edits Google Docs in your own exact house style (font, sizes, spacing, margins) via the Docs API, instead of Google’s defaults. Load this before any Google Docs work, creating a doc, writing or restyling content, converting a note into a polished doc, or building a client-facing deliverable. Covers the two reliable methods (copy a styled template vs. explicit named-style requests), hyperlinking rules, and the read-back verification step. Invoke any time a .gdoc, docs.google.com, “Google Doc”, “GDoc”, or the Docs/Drive API is in play.
triggers:
  - “google doc”
  - “gdoc”
  - “docs.google.com”
  - “create a doc”
  - “style this doc”
  - “google docs api”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Google Docs: matching your own house style, reliably

Google Docs defaults to Arial, default spacing, and default margins, none of which is anyone’s actual house style. If a doc is going in front of a client, a teammate, or anyone who’s seen your other docs before, the default look reads as generic in a way that’s easy to notice and hard to unsee once you’ve seen it. This skill is the fix: a repeatable way to make every doc the Docs API generates come out in your own style, not Google’s.

**Load this skill before any Google Docs work**: creating a doc, editing one, styling one, or handing one off. Any time a `.gdoc`, `docs.google.com`, “Google Doc”, “GDoc”, or the Docs/Drive API is in play, load this first.

## The problem this solves

The Docs API gives you two honest ways to set style, and both have a catch:

- Write content, then apply styles paragraph by paragraph. Reliable, but tedious, and easy to miss one.
- Copy an existing styled doc and pour new content into it. Fast, but only works if you remembered to keep a clean styled template around.

Neither is hard once you know the pattern. Both fail quietly if you skip the read-back verification step at the end: a successful API response is not proof the doc actually looks right.

## Example house style (swap for your own)

This is one real house style, captured here as a worked example so the pattern is concrete instead of abstract. Replace every row with your own values before using this for real.

| Style | Font | Weight | Size | Line spacing | Space above | Space below | Color |
|---|---|---|---|---|---|---|---|
| **TITLE** | Inter | 900 (black) | 30 | 100% | n/a | 32 | default (near-black) |
| **SUBTITLE** | Inter | 400 | 15 | default | n/a | 16 | grey 0.4/0.4/0.4 |
| **HEADING_1** | Inter | 400 + bold | 20 | 130% | 40 | n/a | default |
| **HEADING_2** | Inter | 400 + bold | 14 | 130% | 32 | n/a | default |
| **HEADING_3** | Inter | 400 + bold | 12 | 130% | 16 | 10 | default |
| **HEADING_4** | Inter | n/a | 12 | default | 14 | 4 | grey 0.4 |
| **HEADING_5/6** | Inter | n/a | 11 | default | 12 | 4 | grey 0.4 |
| **NORMAL_TEXT** | Inter | 400 | 11 | 115% | n/a | n/a | default |

- **Page margins:** 72pt (1 inch) on all four sides.
- Sizes are points, line spacing is a percentage (115 = 1.15x), space above and below are points.

Build your own version of this table before you start. Everything below assumes you already have one.

## How to apply it (two reliable methods)

**Method A: copy a styled template (guarantees an exact match).** `drive.files().copy()` a doc that’s already styled the way you want, delete its body (`deleteContentRange` [1, end-1]), then insert content and apply `namedStyleType` per paragraph. Because the copy retains the source doc’s named-style definitions and theme, the new content inherits your exact styles automatically. If you keep more than one template, pick the one that matches the target deliverable.

**Method B: explicit named-style requests.** On a fresh doc, `updateParagraphStyle` with `namedStyleType` (TITLE, HEADING_1, NORMAL_TEXT, and so on). A fresh doc’s named styles are Google’s defaults, so to match your spec you must also push your house-style table through `updateTextStyle` (weightedFontFamily, fontSize, bold) on each style’s range, plus paragraph `lineSpacing` / `spaceAbove` / `spaceBelow`. Method A is less work and less error-prone; prefer it when you have a template to copy.

## Rules (apply the same discipline you’d use for any structured content push)

- **Curly quotes, no em dashes** (use colons or commas instead), sentence case, or whatever your own typography rules say. Apply them here the same as you would anywhere else.
- **Hyperlink the descriptive text**: never a bare “link” (`updateTextStyle` with `link` and `underline` on the phrase’s range).
- **Verify by reading the doc back.** Re-`documents().get()` and confirm the named styles actually applied and the links actually resolved. A successful insert or update response is not proof; only the read-back is.
- **Ownership:** the OAuth token you authenticate with owns the doc. If a client or teammate needs to own it instead of you, either get a token scoped to their account (fragile, since tokens expire and go stale) or create the doc in your own account, share it, and have them transfer ownership on their end. The second path is more reliable and is what this skill assumes by default.
- Store the OAuth token wherever your project keeps credentials, and run the script with whatever Python environment has the Google API client libraries installed.

## Note on capturing your own house style

It’s common to discover your own past docs disagree with each other: one uses Arial body text, another uses something else, because the style drifted between projects before anyone wrote it down. When that happens, resolve it explicitly, pick one, write it into your table, and treat that resolution as canonical from then on. Don’t let the spec keep quietly drifting doc to doc. A fresh Google Doc always defaults to Arial no matter what you decide, so Method B has to explicitly set your font on every named style; Method A only matches if the template you’re copying is itself already in your chosen style.
