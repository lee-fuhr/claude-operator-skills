# Notion status board templates

The kickoff round markup, page title pattern, and update procedure for the client-grade status board described in SKILL.md, written for Notion specifically. Pair with the `notion-docs` skill (also in this repo) for the underlying markdown quirks (tables, callouts, escaping).

### Kickoff round template — skim-optimized (fill the blanks, push, move on)

Pass the 3-second glance test. Top of the page tells you in 3 seconds: health (color), what’s running right now, next update time. Everything else goes in toggles below. Use callouts over prose, tables over bulleted walls, columns for peer data, toggles for mass.

**Block types you’ll use:** `<callout icon="emoji" color="green_bg|yellow_bg|red_bg|blue_bg|gray_bg">`, `<columns><column>...</column></columns>`, `<table header-row="true">` with cell colors via `<td color="green_bg">`, `### Heading {toggle="true"}` with tab-indented children.

**Semantic emoji:** 🟢 green / 🟡 yellow / 🔴 red / ⏱️ timing / 🎯 scope / 🧭 decisions / ⚠️ risks / 🙋 needs-you / 🗂️ sources / 🎨 design / 🗣️ voice / 🛡️ guardrails / 📝 log.

```markdown
<callout icon="🟢" color="green_bg">
	**Health: [green | yellow | red].** [one line: current phase + staging guardrail]
	**Last updated:** [YYYY-MM-DD HH:MM TZ] — bump every time you touch this doc.
</callout>
<columns>
	<column>
		<callout icon="⏱️" color="blue_bg">
			**Next update**
			[~1:30am after Phase N]
		</callout>
	</column>
	<column>
		<callout icon="🛠️" color="gray_bg">
			**Right now**
			[one line: what's in flight this minute]
		</callout>
	</column>
	<column>
		<callout icon="🙋" color="yellow_bg">
			**Need from you**
			[Explicit. "Nothing until morning" is a valid answer.]
		</callout>
	</column>
</columns>
---
# Round 1 — kickoff and scope
<callout icon="📖" color="gray_bg">
	[3-4 sentences. What I'm building, why now, the approach, definition of done. This is the client-reads-in-30-seconds summary.]
</callout>
## 🎯 Scope and deliverables
<table header-row="true" fit-page-width="true">
	<tr><td>Deliverable</td><td>Status</td><td>Notes</td></tr>
	<tr>
		<td>[Page or component]</td>
		<td color="gray_bg">⚪ Not started</td>
		<td>[one line]</td>
	</tr>
	<tr>
		<td>[Shipped thing]</td>
		<td color="green_bg">🟢 Shipped</td>
		<td>[one line]</td>
	</tr>
</table>
## ⏱️ Cadence
<table header-row="true">
	<tr><td>Phase</td><td>ETA</td><td>Status</td></tr>
	<tr><td>[Phase name]</td><td>[~time]</td><td color="green_bg">🟢 Complete</td></tr>
</table>
---
<columns>
	<column>
		## 🧭 Decisions log
		<table header-row="true">
			<tr><td>Decision</td><td>Reversible?</td></tr>
			<tr>
				<td>[decision + one-line why]</td>
				<td color="green_bg">✅ Yes</td>
			</tr>
			<tr>
				<td>[irreversible decision]</td>
				<td color="red_bg">⚠️ No</td>
			</tr>
		</table>
	</column>
	<column>
		## ⚠️ Risks
		<table header-row="true">
			<tr><td>Risk</td><td>Level</td></tr>
			<tr>
				<td>[risk]</td>
				<td color="yellow_bg">🟡 Medium</td>
			</tr>
		</table>
	</column>
</columns>
---
## 📂 Detail (open on demand)
### 🗂️ Content sources {toggle="true"}
	<callout icon="📄" color="blue_bg">
		**[Source name]**
		[counts, path]
	</callout>
### 🎨 Design system {toggle="true"}
	<callout icon="✅" color="green_bg">
		[one-line status]
	</callout>
### 🗣️ Voice direction {toggle="true"}
	[paragraph]
### 🛡️ Guardrails {toggle="true"}
	<callout icon="🚫" color="red_bg">
		**Never**
		- [hard-stop bullet]
	</callout>
	<callout icon="⏲️" color="yellow_bg">
		**Budget**
		- [budget bullet]
	</callout>
### 📝 Session log {toggle="true"}
	#### Phase 0 — [name]
	<callout icon="🟢" color="green_bg">
		**Complete.** [one or two sentences]
	</callout>
	#### Phase 1 — [name]
	<callout icon="🟡" color="yellow_bg">
		**In progress.**
	</callout>
	- [bullet]
```

### Page title pattern (non-negotiable)

**Project first. Then the vital key stuff. Session/date last if at all.** The title is how you find the doc in Notion search, and how you orient to it when a dozen are open. Lead with what’s being built, not with “Overnight session — …” session-ops ceremony.

Format: `[Project] — [build type or deliverable] — [qualifier]`

Examples:
- ✅ `Acme site redesign — Webflow build — overnight 2026-04-12`
- ✅ `Northwind onboarding — positioning audit — round 3`
- ✅ `Analytics pipeline — L1 rollout — 2026-04-18`
- ❌ `Overnight session — Acme redesign (2026-04-12)` — session ceremony first, project buried.
- ❌ `2026-04-12 overnight` — date first, no project signal at all.

### Skim rules (non-negotiable)

- **3-second glance test.** Top of the page = health callout + 3-column status row. Nothing else above the fold.
- **`Last updated` lives in the health callout.** Bump the timestamp every time you touch the doc. Without it there’s no way to tell at a glance whether the session is still alive.
- **Callouts over prose.** Every status signal, risk, and “needs you” item is a colored callout, not a paragraph. Green healthy, yellow watch, red blocked, blue info, gray log.
- **Emoji as semantic shorthand.** Section headings AND callout icons, so you can grep by emoji at a glance.
- **Tables where tables earn their place.** Scope, decisions, risks, cadence. Every cell scannable: emoji + word, not a sentence. Use `<td color="green_bg">` for inline status labels.
- **Columns for peer data.** Decisions next to Risks. Content sources side-by-side. Don’t stack peers vertically.
- **Collapsible detail everywhere.** Upper doc = callouts + tables + columns. Lower doc = toggles for mass. Don’t stack 40 callouts; use toggles.
- **Dividers as rhythm.** `---` between thematic sections only. Sub-sections don’t get dividers.
- **No blank lines** between paragraphs. Notion handles spacing.
- **Curly quotes only. Sentence case. First person singular.** Non-negotiable.
- **Decisions capture why, not what.** So a decision made without you can be overruled later, and you both know exactly what’s being overruled.
- **“Need from you” is explicit.** Always. Even if “nothing until morning.”

### Update pattern (rounds 2+)

After each phase (or color change), add a new round at the top:
1. Convert the current top H1 (`# Round N — ...`) to `{toggle="true"}` and tab-indent its content
2. Add the new round as a regular H1 above it, with a refreshed status block pinned above it
3. Keep the decisions log, risks, and “what I need from you” current in the new round — don’t make the client scroll into an old round to learn what changed
