---
name: ww-smart-quote-fixer
description: Convert straight quotes (' and ") into proper typographic quotes, apostrophes, and primes. Use this skill whenever the user asks to fix quotes, fix typography, clean up AI-generated text, polish content for publication, or apply smart quotes, and apply it proactively when producing editorial prose (blog posts, articles, marketing copy, proposals, web copy, client deliverables) so output uses proper typography from the start. Handles contractions (don't → don’t), possessives (writer's → writer’s), nested quotes, decade abbreviations ('90s → ’90s), and measurements (6'2" → 6′2″). Triggers on phrases like "fix quotes," "smart quotes," "curly quotes," "clean up this text," or whenever editing pasted content from another tool. Skip inside code, file paths, regex, and technical syntax where literal quote characters matter.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Smart quote fixer

Every AI model and most word processors default to straight typewriter quotes: `'` and `"`. Real typography doesn’t. Editors and anyone who’s spent time in a design tool can spot a straight quote in a body of running text in about half a second, and it reads as unpolished, or machine-written, even when nothing else is wrong with the copy. Fixing it by hand means catching every apostrophe, every nested quote, every decade abbreviation, and every foot-and-inch mark without breaking the ones that were already correct, or the ones sitting inside a code block where a straight quote is the right answer. This skill does that conversion deterministically, handling the genuinely hard cases (`'90s` vs. `’90s`, `6'2"` vs. `6′2″`, nested quotes, code regions) instead of a naive find-and-replace that gets half of them wrong.

## When to apply this skill

**Apply automatically, without being asked:**
- When producing editorial prose: blog posts, articles, marketing copy, proposals, web content, client deliverables, public-facing documents.
- When the user pastes AI-generated or web-sourced text with straight quotes and asks for editorial cleanup, review, or polish.
- When working on content destined for publication.

**Apply on explicit request:**
- “Fix the quotes” / “Fix smart quotes” / “Fix typography”
- “Convert to curly quotes”
- “Clean this up” or “polish this” when the text has straight quotes

**Do NOT apply:**
- Inside fenced code blocks (``` ``` ```) or inline code (`` ` ``)
- In technical documentation where literal quote characters matter (regex examples, shell commands, JSON, CSV, config files)
- To file paths, URLs, or anything the user is treating as syntax rather than punctuation
- To text that’s already correctly typeset

## Conversion rules (US English defaults)

| Character | Context | Replacement |
|---|---|---|
| `"` | Opens a quotation (after whitespace, line start, or open punctuation) | `"` left double (U+201C) |
| `"` | Closes a quotation | `"` right double (U+201D) |
| `'` | Opens a nested single-quoted phrase | `'` left single (U+2018) |
| `'` | Closes a nested single-quoted phrase | `'` right single (U+2019) |
| `'` | Apostrophe in contractions (don't, can't, it's) | `'` (U+2019) |
| `'` | Apostrophe in possessives (writer's, Acme's) | `'` (U+2019) |
| `'` | Leading apostrophe in decade abbreviations ('90s, '00s) | `'` (U+2019) |
| `'` | Foot prime in measurements (digit followed by `'`) | `′` (U+2032) |
| `"` | Inch prime in measurements (digit followed by `"`) | `″` (U+2033) |

### The decade gotcha

The apostrophe in `’90s` is a **right** curly quote, not a left one, even though it appears at the start of the token. This is the most common typography mistake.
- Wrong: `‘90s` (looks like an opening quote)
- Right: `’90s`

### Nested quotes

US convention: outer double, inner single.

Input: `She said, "I heard 'no way' from him."`
Output: `She said, “I heard ‘no way’ from him.”`

## How to apply

### Short text (a sentence to a paragraph)

Apply the rules inline yourself, producing the corrected version directly without running the script. A few sentences pasted into chat is faster handled by reading carefully than by setting up a script call.

### Long text, full files, or anything where reliability matters

Run the bundled script at `scripts/fix_quotes.py`. It handles edge cases deterministically and preserves code regions.

**Plain text or markdown:**
```bash
python scripts/fix_quotes.py input.md > output.md
# or via stdin
cat input.txt | python scripts/fix_quotes.py > output.txt
```

**.docx files (preserves formatting: bold, italic, links, headings):**
```bash
python scripts/fix_quotes.py input.docx -o output.docx
```

The script auto-detects format from the file extension.

### Optional modes

The script accepts these flags for team or project-specific preferences:

- `--no-primes`: convert measurement quotes to straight `'` and `"` instead of primes. Some style guides prefer straight quotes for inches and feet.
- `--apostrophes-only`: safe mode, only fix apostrophes (contractions, possessives, decades). Leaves all double quotes alone. Useful when you’re unsure about quote pairing in a complex document.

## Editorial writing default

When producing editorial prose in any project that has this skill installed, proposals, blog drafts, marketing copy, web content, client deliverables, write with curly quotes from the start. Don’t produce straight quotes and rely on someone running the fixer after; produce the right characters in the first place.

- Apostrophes in contractions and possessives: `’`
- Quotations: `“…”`
- Nested quotations: `‘…’`
- Use straight quotes ONLY in code blocks, inline code, file paths, and verbatim technical content.

Example of what to produce:
> We’re excited to partner on the city’s website redesign. As the team’s design lead put it, “It’s about meeting people where they are.”

Not:
> We're excited to partner on the city's website redesign. As the team's design lead put it, "It's about meeting people where they are."

## Examples

**Contractions, possessives, and a quotation:**
```
Input:   "It's the '90s," she said, "and the writer's voice is everything."
Output:  “It’s the ’90s,” she said, “and the writer’s voice is everything.”
```

**Measurements:**
```
Input:   He's 6'2" and the room is 12' x 14'.
Output:  He’s 6′2″ and the room is 12′ x 14′.
```

**Nested quotes:**
```
Input:   The brief said, "We need a 'no surprises' approach."
Output:  The brief said, “We need a ‘no surprises’ approach.”
```

**Code preserved:**
````
Input:   Use `text.replace("'", "'")` to fix it. "Like so," she said.
Output:  Use `text.replace("'", "'")` to fix it. “Like so,” she said.
````
(The inline code is untouched; only the prose around it is converted.)

## Known limitations

- Documents with unusual punctuation or mixed languages may need manual review.
- Some apostrophe cases are genuinely ambiguous (e.g., `dogs' food` vs. `dog's food`); the script preserves the input’s structure but trust editorial judgment over the output.
- Poetic contractions starting with an apostrophe (`'tis`, `'twas`) and constructions like `rock 'n' roll` may convert to opening quotes; manually fix to closing apostrophes if needed.
- For documents with heavy technical content alongside prose, prefer `--apostrophes-only` and review double quotes manually.
