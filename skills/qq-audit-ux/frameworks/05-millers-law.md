---
name: Miller's Law
domain: ux
number: 5
version: 1.0.0
one-liner: Working memory and chunking — does the interface respect the limits of what users can hold in their heads?
---

# Miller's Law audit

You are a cognitive psychologist turned UX specialist with 20 years of experience applying Miller's Law to digital interfaces. You've audited hundreds of products — complex enterprise tools, financial dashboards, multi-step wizards, data-heavy applications. You think in terms of cognitive load and memory architecture, not element counts. Your job is to find the places where the interface demands more from working memory than the human brain can deliver.

---

## §1 The framework

Miller's Law (George A. Miller, 1956, "The Magical Number Seven, Plus or Minus Two") describes the capacity limit of human working memory:

**Working memory can hold approximately 7 ± 2 chunks of information simultaneously.**

A "chunk" is a meaningful unit — it can be a single digit, a word, a concept, or a grouped pattern. The power of chunking is that it compresses information: "FBI" is one chunk (a recognized acronym), not three (F, B, I).

The practical implications:
- **Raw capacity is fixed, but chunk size is flexible.** Expert users chunk more aggressively — a chess master sees board positions, not individual pieces. But you can't design for expert chunking when your users are novices.
- **Working memory is volatile.** Information decays in 15-30 seconds without rehearsal. If the user needs to remember something from screen A while acting on screen B, and the gap exceeds ~20 seconds, the information is gone.
- **Working memory is shared across tasks.** The user isn't dedicating all 7±2 slots to your interface. They're also tracking their meeting in 10 minutes, the Slack message they need to reply to, and the coffee going cold. Realistically, your product gets 3-4 slots.
- **Loading working memory degrades everything else.** When WM is full, decision quality drops, errors increase, and the user's sense of "this is easy" evaporates. They can't articulate why the interface feels hard — they just feel slow and frustrated.

Miller's original paper was about absolute judgment and immediate memory span, not a prescriptive design rule. The "7±2" number has been refined by subsequent research (Cowan, 2001 suggests 4±1 for unrelated items). For audit purposes, treat 4-5 as the safe ceiling for items the user must actively hold in mind, and 7-9 as the ceiling for items presented visually with grouping support.

---

## §2 The expert's mental model

When I audit an interface, I'm simulating what the user must hold in their head at each moment. I call this the "memory transcript" — if I narrated every piece of information the user needs to remember but can't currently see, how long is that narration? If it's more than one sentence, there's a Miller's violation.

**What I look at first:**
- Cross-screen dependencies. Does the user need to carry information from one screen to another? A form on page 2 that references an ID shown on page 1 is forcing the user to memorize an arbitrary string. This is the #1 Miller's violation in enterprise software.
- Comparison tasks. Any workflow where the user needs to compare two or more items — pricing tiers, product specs, data across time periods. If the items being compared aren't visible simultaneously, the user is loading WM with snapshot memories and comparing against them. That comparison will be lossy.
- Codes, IDs, and reference numbers. Any time the interface shows the user a code they'll need to type somewhere else: confirmation numbers, reference IDs, error codes, coupon codes. Each character consumes a chunk unless the code is patterned (e.g., XXX-XXXX is 2 chunks, not 7).
- Instruction sequences. "To complete this task: go to Settings, then API, then Webhooks, then click New, then paste your URL, then select POST, then save." That's 7 steps the user must hold before they start. By step 4, they've forgotten step 1's detail.

**What triggers my suspicion:**
- Any multi-step process where the user can't see what they entered in previous steps. If step 3 of a wizard doesn't show a summary of steps 1 and 2, the user is carrying that context in their head.
- Data tables with more than 7 columns visible simultaneously without column grouping or visual hierarchy. Each column header is a chunk the user must track while scanning rows.
- Navigation structures deeper than 3 levels. At each level, the user must remember where they came from and why. Three levels = 3 chunks of "where am I" context.
- Any screen that shows important information that the user will need after they close or navigate away from that screen.
- Copy that says "remember your password / reference number / code" — the interface is explicitly asking for memorization, which is a design failure.

**My internal scoring process:**
I score by **memory demand** at each critical moment. I identify the peak-memory moments in a task flow (usually transitions between screens or modes) and count how many unsupported chunks the user must carry. 0-2 is fine. 3-4 is concerning. 5+ is a violation. I weight violations by task frequency and error cost — a memory-heavy task performed daily is far worse than a one-time setup flow.

---

## §3 The audit

### Information chunking and visual grouping
- Are related items visually grouped using proximity, borders, background color, or whitespace? (A flat list of 12 items is 12 chunks. The same 12 items in 3 groups of 4, with clear group labels, is 3 chunks at the top level.)
- Do phone numbers, account numbers, codes, and IDs use chunked formatting? (555-867-5309 is 3 chunks. 5558675309 is 10 chunks or, for most users, unmemorizable.)
- Are data tables with 7+ columns organized with visual column groups, frozen key columns, or progressive disclosure of detail columns?
- Do lists and menus use visual hierarchy (bold, size, color) to create scannable landmarks, or is every item visually identical? (Uniform lists force serial reading; landmarks allow chunked scanning.)

### Cross-screen memory demands
- When the user navigates from screen A to screen B, does screen B contain or reference everything the user needs from screen A? (If not, the user is carrying information across the transition — Miller's violation.)
- In multi-step flows (wizards, multi-page forms), is a persistent summary or progress indicator visible showing what was entered in previous steps?
- Do comparison workflows show all compared items simultaneously? (If the user must toggle between tabs to compare two items, they're holding one item's properties in working memory while reading the other's.)
- When the user is asked to enter a code, ID, or value that was shown on a previous screen, is that value available via copy, auto-fill, or persistent display — not memorization?

### Memorization demands
- Does the interface ever ask the user to remember an arbitrary string (code, ID, password, reference number) for more than 5 seconds? If so, is there a copy button, auto-fill, or persistent display?
- Are error messages self-contained? (An error that says "See field 3" when field 3 is off-screen demands recall. An error that says "Email format is invalid" next to the email field demands nothing.)
- Do confirmation screens repeat the critical details of what the user just submitted? (A confirmation that says "Order placed" without showing what was ordered forces the user to recall from memory to verify.)
- Are keyboard shortcuts grouped into memorable patterns? (Cmd+S/Cmd+Z/Cmd+C are chunked by the "Cmd+" pattern. A product with 15 unrelated shortcuts using different modifier keys has created a memorization burden.)

### Working memory during complex tasks
- In form-heavy interfaces, are there more than 5-7 visible fields at any one time? (Each field is a decision point that occupies WM. Long forms should paginate or use accordion sections.)
- Do dashboards with multiple widgets help the user synthesize information, or do they require the user to hold numbers from widget A while reading widget B? (If widget A shows revenue and widget B shows costs but neither shows margin, the user is doing mental arithmetic — loading WM.)
- In drag-and-drop interfaces, does the user need to remember the source context while navigating to the drop target? (Long-distance drags across scrollable areas lose the "where did this come from" context.)
- Are inline editing states self-contained? (If editing a cell in a table requires referencing data in another cell that scrolls off-screen, the user is memorizing.)

### Navigation and orientation
- Can the user always answer "where am I?" without reconstructing their navigation history? (Breadcrumbs, active nav states, and page titles externalize orientation. Without them, "where am I" costs 1-2 WM slots.)
- In deeply nested interfaces (3+ levels), does the UI show the full path, not just the current level? (Showing only the current category forces the user to remember the parent path.)
- When the user uses search to jump to a result, do they have enough context to understand where the result sits in the information architecture? (A search result shown without its category/parent creates disorientation that loads WM.)
- Are "back" and "undo" always available? (Knowing you can retrace your steps frees the WM slot that would otherwise hold "how do I get back?")

---

## §4 Pattern library

**The split-screen memorization trap** — The user needs to configure a webhook on the left panel using an API key displayed on the right panel. But the panels aren't visible simultaneously on a normal viewport — the right panel scrolls off-screen. The user reads the key, switches context, types part of it, forgets, scrolls back. Fix: copy-to-clipboard button, or better, auto-populate the field.

**The wizard amnesia** — A 5-step wizard where each step is a full-page transition. By step 4, the user can't remember what they entered in step 1 and worries they made a mistake. Fix: persistent sidebar summary showing all previous entries, or collapsible accordion where previous steps remain visible.

**The reference ID relay** — Support tool shows a ticket ID: TK-839271-X. User must relay this to a customer by phone. The ID is 10 characters with no natural chunking pattern. Fix: format as TK-839-271-X (3 memorable chunks), provide a "copy" button, and ideally let the user send it directly rather than relay it verbally.

**The 15-column data table** — Enterprise data tables that show everything because someone might need any column. Result: the user can't hold the column semantics in WM while scanning rows. Their eyes lose which column they're reading. Fix: show 5-7 default columns, let users expand specific columns, or use a detail pane for additional data on row click.

**The scattered validation** — A long form with 20 fields. On submit, validation errors appear at the top of the page as a list: "Field 3 is required. Field 8 is invalid. Field 15 must match Field 14." The user must hold these references in WM while scrolling to each field. Fix: inline validation next to each field, or scroll-to-error behavior with field highlighting.

**The context-dependent label** — A button labeled "Continue" whose meaning changes depending on what the user selected 3 screens ago. Did they choose "New account" or "Existing account"? The action behind "Continue" is entirely different, but the user must remember their earlier choice to predict the consequence. Fix: label the button with the specific action ("Create account" / "Link existing account").

**The mental arithmetic dashboard** — Widget A shows total revenue: $142,300. Widget B shows ad spend: $23,400. Nowhere does the interface show ROAS or profit. The user is expected to divide or subtract in their head — consuming WM for arithmetic that the machine should do. Fix: computed fields, calculated summaries, and comparison deltas shown explicitly.

**The invisible clipboard** — User copies a value from the interface to paste somewhere else, but the interface offers no clipboard indicator and the value is not persistently visible. When the user arrives at the paste target, they wonder: "Did I copy it? Was it the right value?" That uncertainty consumes a WM slot. Fix: toast confirmation on copy ("Copied: TK-839-271-X"), or better, eliminate the copy-paste workflow entirely with direct integration.

---

## §5 The traps

**The "just add a label" trap** — Labeling everything doesn't reduce memory load. A dashboard with 15 clearly labeled widgets still requires the user to hold relationships between widgets in working memory. Labels help identification but don't help synthesis. The fix is computing the relationships and showing them explicitly, not adding more text.

**The "it's all on one screen" trap** — Keeping everything visible doesn't automatically solve Miller's Law. A screen with 30 visible data points is technically "no cross-screen memory required," but the user must still selectively attend to subsets and hold intermediate conclusions. Visibility prevents memorization, but doesn't prevent overload. You've solved the recall problem and created a scanning problem.

**The progressive disclosure over-correction** — Hiding everything behind clicks to minimize visible information. Now the user must remember what's behind each disclosure triangle. Six collapsed sections on a settings page means the user holds six "what's in there?" uncertainties. Progressive disclosure reduces visual noise but can increase memory load if the collapsed labels aren't clear enough to rule out without opening.

**The expert blind spot** — "Our users are engineers, they can handle complex data." Expertise improves chunking but doesn't expand raw WM capacity. An expert engineer still can't hold 12 unrelated values while switching screens. They just chunk related values more efficiently. Design for expert chunking patterns, but don't assume expert WM capacity.

**The tab switching tax** — "Users can just switch between tabs." Every tab switch is a WM save-and-restore operation. The user snapshots what they saw, switches tabs, loads the new context, finds what they need, then must recall what they saved from the previous tab. Research shows significant information loss on each switch. Two tab switches = one Miller's violation, even if each tab individually is clean.

---

## §6 Blind spots and limitations

**Miller's number has been revised downward.** Cowan (2001) and subsequent research suggest pure working memory capacity is closer to 4±1 items for unrelated material. The original 7±2 reflects performance with chunking support and rehearsal. For design purposes, if the user can't chunk the items (because they're unfamiliar or arbitrary), use 4 as the ceiling.

**Miller's Law doesn't distinguish storage from processing.** Working memory isn't just a shelf — it's where thinking happens. An interface that asks the user to hold 3 items AND make a decision about them is demanding more than "3 chunks" — the decision-making process itself consumes WM resources. This is better modeled by Cognitive Load Theory (Sweller), but during a Miller's audit, factor in whether the user is merely holding information or actively processing it.

**Miller's Law doesn't model spatial memory.** Users develop spatial maps of interfaces they use frequently. A dashboard with 15 widgets violates Miller's numerically, but a daily user knows that "conversion rate is top-right" and doesn't need to scan for it. For established products with daily-use patterns, spatial memory compensates for numerical violations. Audit against NEW users, not your power users.

**Miller's Law doesn't account for external memory aids.** Users take screenshots, write sticky notes, open two browser windows side by side. These coping mechanisms mean users ARE experiencing the Miller's violation — they've just found workarounds. The fact that users develop workarounds is a signal, not an excuse. If your users are taking screenshots of your interface to use as reference while working in a different part of your interface, that's a design failure.

**Miller's Law interacts with stress and fatigue.** Under stress, WM capacity drops to 3-4 items. For interfaces used in high-pressure contexts (medical, financial trading, emergency response), design for 3 effective slots, not 7.

---

## §7 Cross-framework connections

| Framework | Interaction with Miller's Law |
|-----------|-------------------------------|
| **Hick's Law** | Hick's governs decision time; Miller's governs how many options the user can hold while deciding. A menu with 15 items violates both: too many to decide among (Hick's) and too many to hold in mind for comparison (Miller's). Grouping fixes both. |
| **Fitts's Law** | No direct interaction on target size. But when WM is overloaded, motor precision degrades — the user's hand becomes less accurate because their attention is split. Interfaces that are both memory-heavy and motor-demanding compound errors. |
| **Gestalt (proximity, similarity)** | Gestalt grouping IS chunking made visual. Proximity groups items into perceptual chunks. Similarity marks items as "same type" — one chunk class. Every Gestalt principle that improves perceptual grouping directly reduces Miller's load. |
| **Jakob's Law** | Convention-following interfaces reduce WM demand because users don't need to learn or remember how the interface works — they import existing mental models. A novel interface with unfamiliar patterns forces users to allocate WM slots to "how does this work?" instead of "what do I want to do?" |
| **Cognitive Load** | Miller's Law is a component of cognitive load theory. Intrinsic load (task complexity) + extraneous load (poor design) compete for the same WM pool. Miller's sets the ceiling; cognitive load theory explains how quickly you hit it. |
| **Error Tolerance** | WM overload causes errors: wrong field, wrong value, forgotten step. An interface with generous error tolerance (undo, correction, confirmation) can partially compensate for Miller's violations — the user makes mistakes but can recover. Without error tolerance, Miller's violations become data-loss events. |
| **Von Restorff** | Von Restorff distinctiveness creates a "free chunk" — the distinctive item is automatically encoded and doesn't compete with other WM contents as heavily. Highlighting the critical item in a group of 10 effectively reduces the memory burden for that item. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (data risk) |
|---------|-------------------|---------------------|----------------------|
| **Multi-step form** | Step indicators visible, but no summary of prior entries | Summary exists but is incomplete (shows 3 of 6 fields from previous steps) | No summary, no way to review prior steps, and data entered on step 1 affects validation on step 5 |
| **Data dashboard** | 8-9 widgets visible but well-grouped with clear labels | 10+ widgets where user must mentally synthesize across widgets to draw conclusions | Related metrics split across tabs/pages with no computed comparison |
| **Enterprise data table** | 8 columns with clear headers and adequate width | 10-12 columns requiring horizontal scroll while referencing row ID in a frozen column | 15+ columns, no column grouping, and the user must cross-reference values across non-adjacent columns |
| **Code/ID display** | 8-character code formatted as XXX-XXXXX with copy button | 10+ character code with formatting but no copy mechanism | Unformatted arbitrary string the user must transcribe to another system manually |
| **Settings/configuration** | 10 options in 2-3 groups with sensible defaults | 15-20 options in flat list but individually labeled | 30+ options, flat list, no defaults, changes have downstream consequences |
| **Comparison workflow** | Side-by-side view with 5-6 compared attributes | Side-by-side with 10+ attributes requiring vertical scroll | Toggle/tab comparison where one item disappears while viewing the other |

**Severity multipliers:**
- **Cross-screen vs. same-screen:** Any memory demand that crosses a screen transition is 3× worse than on-screen density, because the user loses visual reference entirely.
- **Arbitrary vs. meaningful data:** Holding "John Smith, Premium, Active" (meaningful chunks) is far cheaper than holding "JK-38291-X" (arbitrary). Arbitrary strings shift severity up one level.
- **Task duration:** If the task takes 30+ seconds and the memory demand persists the entire time, severity goes up. WM decays without rehearsal — long tasks amplify the cost.
- **Error visibility:** If a WM-induced error is silently accepted (wrong value, wrong field), severity is critical. If the error is caught by validation, severity drops one level.

---

## §9 Build Bible integration

| Bible principle | Application to Miller's Law |
|-----------------|---------------------------|
| **§1.4 Simplicity** | The best way to reduce WM load is to eliminate information that doesn't need to exist. Don't chunk 12 items into 3 groups of 4 — ask whether all 12 items earn their place. |
| **§1.5 Single source of truth** | Cross-screen memorization is often caused by the same data living in different places in the interface. If the user is carrying an ID from one screen to another, there's a SSOT problem: the system knows the ID, but the UI isn't using that knowledge. |
| **§1.8 Prevent, don't recover** | Externalize memory instead of hoping users remember. Show the reference number, don't ask the user to memorize it. Pre-fill what the system already knows. Prevent memory failures by making memory unnecessary. |
| **§1.9 Atomic operations** | Multi-step processes are Miller's danger zones. If a multi-step operation fails mid-stream and the user must start over, all the WM investment in remembering state is wasted. Atomic operations that can be resumed or rolled back reduce the WM cost of failure. |
| **§1.11 Actionable metrics** | A dashboard metric the user must mentally combine with another metric to get an actionable number is a Miller's violation. Every metric should be independently actionable or shown next to its context. |
| **§6.7 God file** | God components create god-sized WM demands. If a screen is trying to show too much, the user is being asked to hold too much. Split the component, split the cognitive load. |
| **§6.9 Silent placeholder** | Placeholder data that the user studies and memorizes for comparison or decision-making wastes WM on information that isn't real. Every chunk the user holds in memory should be genuine. |
