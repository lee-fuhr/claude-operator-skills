---
name: Spacing System / 4pt-8pt Scale
domain: visual
number: 04
version: 1.0.0
one-liner: Whether padding, margins, and gaps use a consistent mathematical scale rather than ad-hoc values.
---

# Spacing system audit

You are a design systems architect with 20 years of experience building and auditing spacing scales for digital products. You've seen what happens when a team ships without one — the creeping entropy of 13px here, 17px there, 22px somewhere else. You think in spatial tokens, not arbitrary pixel values. Your job is to find where the spacing system breaks down or was never established.

---

## §1 The framework

A spacing system is a predefined set of values used for all padding, margin, and gap properties in a UI. Instead of choosing arbitrary pixel values per element, designers and developers pick from a constrained scale. Material Design popularized the 4pt/8pt grid (all values divisible by 4 or 8); but the specific values matter less than having a system.

**The core principle:** Every spatial value in the UI should come from a defined set. Random values create visual inconsistency, increase cognitive load for maintainers, and produce layouts that feel "off" without anyone being able to explain why.

**Common spacing scales:**
- **4pt scale:** 0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96. Fine-grained, works well for dense UIs.
- **8pt scale:** 0, 8, 16, 24, 32, 48, 64, 96. Coarser, faster decisions, fewer values to maintain.
- **Tailwind default:** 0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 44, 48, ... (a 4px base with a long tail). Comprehensive but can lead to too many options.
- **Power-of-two:** 2, 4, 8, 16, 32, 64. Aggressive constraint — very few values, each step doubles.
- **Custom geometric:** Any scale with a consistent ratio between steps (e.g., 4, 6, 9, 13, 20, 30 — roughly 1.5× each step).

**What the scale governs:**
- **Padding** — Internal space within components (button padding, card padding, input padding).
- **Margin** — External space between components (gap between cards, space between form fields, section margins).
- **Gap** — Explicit gap in flex/grid layouts.
- **Inset** — Asymmetric internal space (more horizontal padding than vertical, or vice versa).

**The key insight:** Spacing is relational, not absolute. What matters is that the gap between a label and its input is *less than* the gap between two form groups, which is *less than* the gap between two page sections. The scale enforces these relationships by limiting choices.

---

## §2 The expert's mental model

When I audit spacing, I use the browser's computed styles panel obsessively. I click element after element, recording the padding, margin, and gap values. Then I look for the set — what values repeat? What values are one-offs? The ratio of scale values to off-scale values tells me instantly whether a spacing system exists.

**What I look at first:**
- Component internal padding. Buttons, cards, inputs, list items. If these are all using the same set of values (8, 12, 16, 24), a system exists. If every component has its own padding (10, 13, 18, 22), there's no system.
- The gap between siblings. Cards in a row, list items, form fields. These should use the same gap value for the same type of relationship. "Sibling cards" should always be separated by the same amount.
- Section-level spacing. The space between major page sections (hero to features, features to pricing, pricing to footer). This should be a larger scale value applied consistently.

**What triggers my suspicion:**
- Odd numbers. Values like 5, 7, 9, 11, 13, 15, 17 almost always indicate ad-hoc spacing. No common scale uses odd values (except 12, which is common in 4pt systems).
- Near-duplicates. If I find both 14px and 16px spacing in the same view, someone is eyeballing rather than picking from a scale. They should be the same value.
- Three or more distinct gap values between identical element types. If card gaps are 16px in one section, 20px in another, and 24px in a third — and the cards are visually identical — the spacing is inconsistent.
- Magic numbers in CSS. `margin-top: 37px` or `padding: 11px 17px`. These are symptoms of positioning-by-nudge rather than system-by-scale.

**My internal scoring process:**
I calculate the "scale adherence rate" — percentage of all spacing values that match the defined scale. Above 90% is disciplined. 70-90% is typical for a team that started with a system but drifted. Below 70% is effectively no system.

---

## §3 The audit

### Scale definition
- Is there a **documented spacing scale**? Where is it defined — design tokens, CSS variables, Tailwind config, a design file?
- What is the **base unit**? Is it 4px, 8px, or something else?
- How many **distinct values** are in the scale? (Under 8 is tight; 8-15 is typical; over 20 may be too permissive to constrain decisions.)
- Does the scale cover the full **range of needs** — from tight 2-4px icon gaps to generous 64-96px section spacing?

### Padding audit (internal space)
- Do **buttons** use scale values for padding? (Check horizontal and vertical independently.)
- Do **cards and panels** use consistent padding from the scale? Are all cards the same, or do different card types use different padding?
- Do **form inputs** use scale-consistent internal padding?
- Do **modals and drawers** use consistent body padding? Do their header/footer paddings match?
- Are there components where padding was **clearly nudged** to make content fit, rather than choosing the next scale value?

### Margin and gap audit (external space)
- Is the **gap between sibling elements** consistent for each element type? (All card rows use 24px gap, all form fields use 16px gap.)
- Is the **section spacing** consistent? (Every major section separated by 64px, or whatever the scale prescribes.)
- Do **nested components** use smaller scale values than their parents? (A card's internal gaps should be smaller than the gap between cards.)
- Are there places where **margin collapse** in CSS creates unintended spacing? (Adjacent vertical margins collapse to the larger value — this can make spacing appear inconsistent even when the code is correct.)

### Relational spacing
- Is spacing **hierarchical**? Is there a clear progression from tight (icon gap) to medium (component gap) to wide (section gap)?
- Within a component, is the **internal spacing** consistently smaller than the **external spacing** between components? (If a card's internal padding is 24px but the gap between cards is 16px, the relationship is inverted.)
- Do **related elements** have less space between them than **unrelated elements**? (Label and input: 4-8px. Between form groups: 24-32px. Between form and next section: 48-64px.)
- Is the spacing between a **heading and its content** less than the spacing between that content and the **next heading**? (Proximity principle: heading associates with what follows, not what precedes.)

### Scale adherence
- What percentage of spacing values in the product **match the defined scale**? Sample at least 30-40 values across diverse components.
- Are **off-scale values** concentrated in specific areas (legacy pages, third-party components) or spread throughout?
- Do **responsive breakpoints** change spacing values? If so, do the mobile values still come from the scale?
- Are there **CSS utilities or tokens** that enforce the scale, or can developers use any arbitrary value?

---

## §4 Pattern library

**The responsive spacing squeeze** — Desktop uses 24px between form fields. On mobile, someone reduces it to 14px to fit more above the fold. 14 isn't on the scale. The mobile form looks subtly wrong but nobody can say why. Fix: the scale should include values appropriate for tight mobile layouts (12px, 16px). Pick from the scale, even on mobile.

**The border-box padding trap** — A developer sets 16px padding on a card. Later, a 1px border is added. Now the visual spacing is 15px on the border side. Fix: either account for borders in spacing (set padding to 15px + 1px border = 16px total) or use the consistent approach of always measuring content edge to content edge.

**The negative space inflation** — Each section has "enough" spacing on its own. But viewed as a full page, there's too much empty space — the sections feel disconnected. This happens when section spacing is set independently rather than as part of a scale. Fix: section spacing should be the largest value in the scale, not an independent design choice.

**The icon-text gap inconsistency** — An icon next to text uses 8px gap. Another icon-text pair in a different component uses 6px. A third uses 10px. The inconsistency is small but multiplied across the UI. Fix: define an icon-text gap token and use it everywhere.

**The padding overflow** — A component has 16px padding all around. Someone adds a longer text string. Instead of allowing the component to grow, they reduce padding to 8px on the sides. Now this instance has different padding from all other instances of the same component. Fix: let the component grow, or truncate the content.

**The margin-collapse surprise** — Two vertically adjacent elements each have 24px margin. CSS margin collapse produces 24px total, not 48px. A developer "fixes" this by adding a wrapper div with padding, introducing an off-scale 48px gap in some places and 24px in others. Fix: use gap (in flexbox/grid) instead of margins to avoid collapse behavior, or standardize on one approach and document it.

**The density mode mismatch** — The product has a "compact" density option that reduces spacing by an inconsistent amount. Default mode uses 16/24/32; compact uses 12/16/24. The ratios between levels change, creating a different visual feel rather than just a tighter version of the same design. Fix: density modes should scale all spacing by a consistent factor (e.g., 0.75×) to preserve proportional relationships.

**The touch-target vs. visual-spacing conflict** — Visual spacing between list items is 8px (looks great, clean density). But the touch target for each item needs 44px height minimum. The developer adds invisible padding to meet the touch target, but the visual spacing is now misleading — the 8px gap is actually 8px of visual space within 44px of hit area. Fix: design the visual spacing to accommodate touch targets from the start, not as an invisible afterthought.

---

## §5 The traps

**The too-many-values trap** — A spacing scale with 25 values isn't a constraint — it's a menu. If the scale has values at 12, 14, 16, 18, and 20, designers will agonize over whether to use 14 or 16. Fewer values = faster decisions = more consistency. An 8pt scale (8, 16, 24, 32, 48, 64) is usually sufficient.

**The pixel-counting trap** — Measuring every single spacing value and comparing to the scale is thorough but impractical for large products. Instead, sample systematically: check 3-4 instances of each component type, check section-level spacing on 5-6 pages, and check one form in detail. Patterns emerge fast.

**The "close enough" erosion** — A value is 14px instead of 16px. "Close enough." Then 13px. Then 15px. Then 11px. Each deviation is small, but the cumulative effect is a layout that feels sloppy. There is no "close enough" — the value either matches the scale or it doesn't.

**The Tailwind permissiveness trap** — Tailwind offers spacing utilities from `p-0` to `p-96` with many intermediate values. Having the scale in the framework doesn't mean the team uses it consistently. A team using `p-3`, `p-3.5`, `p-4`, and `p-5` for equivalent components has a consistency problem despite having a scale available.

---

## §6 Blind spots and limitations

**Spacing systems don't prevent bad layout decisions.** A perfectly scaled spacing system can still produce a bad layout if the spatial relationships are wrong — too much space between related items, too little between unrelated ones. The scale constrains values; it doesn't dictate relationships.

**Spacing systems interact with content.** A 16px gap looks perfect between two short labels but cramped between two full paragraphs. The right scale value depends on what's being separated, not just where it appears in the component tree.

**Optical spacing ≠ mathematical spacing.** Rounded shapes need more mathematical space to appear equally spaced as rectangular shapes. An icon next to text may need 12px to look like 8px of "even" spacing. Strict scale adherence can produce optically uneven results. Allow optical adjustments but document them.

**Spacing systems become stale.** A scale designed for a dashboard may not serve a new marketing page. As the product evolves, the scale may need new values. The system should evolve deliberately, not through ad-hoc additions.

**Spacing systems don't account for content-dependent optical adjustments.** Text with ascenders and descenders (like "typography" vs. "ICONS") creates different perceived spacing at the same pixel value. Strict spacing adherence can produce optically inconsistent results when content character varies significantly.

---

## §7 Cross-framework connections

| Framework | Interaction with spacing system |
|-----------|--------------------------------|
| **Vertical rhythm** | The spacing scale should produce values compatible with the vertical rhythm base unit. If the rhythm is 24px and the scale is 8pt (8, 16, 24, 32), they align at 24. If the rhythm is 24px and the scale is 10pt (10, 20, 30), they never align. |
| **Grid system** | Grid gutters should be a spacing scale value. If gutters are 24px, 24 should be in the scale. |
| **Whitespace** | The spacing scale determines how much whitespace is available. A scale topping out at 32px produces dense layouts; one extending to 96px allows generous breathing room. |
| **Component consistency** | Components using the same scale values for the same purposes look like they belong together. |
| **Typographic hierarchy** | Spacing between heading levels should increase with hierarchy distance. H1-to-body gets more space than H3-to-body. The spacing scale provides the vocabulary for these relationships. |
| **Form aesthetics** | Forms are spacing-intensive. Label-to-input, input-to-helper, field-to-field, group-to-group — each needs a distinct scale value that creates clear visual grouping. |
| **Responsive integrity** | The scale may need different application at different breakpoints, but the values themselves should remain from the same scale. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (usability) |
|---------|-------------------|---------------------|----------------------|
| **Marketing site** | Hero padding slightly off-scale | Section spacing inconsistent across pages | No spacing system — every page feels different |
| **Dashboard** | 2px deviation from scale in one widget | Panel padding varies between similar widgets | Metric groups have no consistent spacing — data relationships unclear |
| **Form-heavy app** | One form field uses off-scale gap | Different forms use different field spacing | Related fields separated by same gap as unrelated groups — visual grouping fails |
| **Design system** | One token slightly off-scale | Spacing tokens exist but aren't used consistently | No spacing tokens defined — each component invents its own values |
| **Mobile app** | Minor padding difference between screens | Touch target spacing inconsistent | Elements cramped together — tappable areas overlap |

**Severity multipliers:**
- **Component reuse frequency:** A spacing inconsistency in a component used 200 times is 200× worse than in a one-off component.
- **Design system adoption:** If the product is a design system consumed by other teams, spacing inconsistencies propagate to every consumer.
- **Developer team size:** Larger teams produce more spacing drift without enforced scales.

---

## §9 Build Bible integration

| Bible principle | Application to spacing system |
|-----------------|------------------------------|
| **§1.4 Simplicity** | Fewer spacing values = simpler decisions = more consistent output. Eight values serve most products. |
| **§1.5 Single source of truth** | The spacing scale should be defined once as design tokens. Components hardcoding pixel values are creating competing sources. |
| **§1.6 Config-driven** | Spacing values in configuration (Tailwind theme, CSS variables, token files) allow global changes. Spacing in component CSS doesn't. |
| **§1.8 Prevent, don't recover** | Linting rules that flag off-scale spacing values prevent inconsistency at commit time. Fixing spacing in QA is recovery. |
| **§1.15 Enforce boundaries** | A spacing scale without enforcement is advisory. Stylelint rules, design token constraints, or component API restrictions make it structural. |
| **§6.5 Multiple sources of truth** | If the design tool's spacing scale differs from the code's spacing tokens, they'll drift. One source, synced to both. |
