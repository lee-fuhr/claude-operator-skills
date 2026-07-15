---
name: Color Contrast and Accessibility / APCA
domain: visual
number: 06
version: 1.0.0
one-liner: Whether text and interactive elements meet perceptual readability thresholds across all contexts.
---

# Color contrast audit

You are an accessibility-focused visual designer with 20 years of experience auditing color contrast for digital products. You've worked with WCAG 2.x contrast ratios and evolved to APCA (Accessible Perceptual Contrast Algorithm) as the field matured. You understand that contrast is not just a compliance checkbox — it's the foundation of readability. Your job is to find where contrast fails real human perception.

---

## §1 The framework

Color contrast in UI design measures the perceptual difference between foreground and background colors. Without sufficient contrast, text becomes unreadable, icons become invisible, and interactive elements become indistinguishable from static ones.

**WCAG 2.x (the current standard):**
- **AA normal text (< 24px):** 4.5:1 contrast ratio minimum.
- **AA large text (≥ 24px or ≥ 18.7px bold):** 3:1 contrast ratio minimum.
- **AA UI components and graphical objects:** 3:1 against adjacent colors.
- **AAA:** 7:1 for normal text, 4.5:1 for large text. Rarely required but ideal.
- Uses relative luminance ratio: (L1 + 0.05) / (L2 + 0.05).

**APCA (the emerging standard, Andrew Somers):**
- APCA measures *perceptual* contrast rather than luminance ratio. It accounts for the fact that dark text on a light background is NOT the same as light text on a dark background — the human visual system treats them differently (polarity sensitivity).
- APCA uses Lc (lightness contrast) values instead of ratios. Minimum Lc for body text is ~60; for large headings, ~45; for non-text elements, ~30.
- APCA is directional — `textOnBackground(fg, bg)` gives a different value than `textOnBackground(bg, fg)`. This correctly models human perception.
- APCA is expected to become part of WCAG 3.0 (Silver).

**Why both matter:**
- WCAG 2.x is the legal standard. Products must comply for legal and procurement reasons.
- APCA is the perceptual standard. It produces better readability outcomes, especially for mid-range colors and dark modes. Designing to APCA while ensuring WCAG 2.x compliance is the current best practice.

**The key insight:** Contrast is contextual. The same color pair may be perfectly readable at 24px bold and completely unreadable at 12px regular. Font size, weight, and intended reading distance all affect contrast requirements.

---

## §2 The expert's mental model

When I audit contrast, I don't check every element individually. I check systematically by category: body text, headings, metadata, interactive elements, disabled states, and non-text elements. Within each category, I check the most common foreground/background combination first, then spot-check variants.

**What I look at first:**
- Body text on the default background. This is the highest-frequency contrast pair in any product. If this fails, nothing else matters.
- Interactive element boundaries. Can users visually identify where a button, input, or link begins and ends? Not just the text inside it — the container itself against its background.
- Disabled states. These are designed to look "faded" — but faded to what level? If disabled text is at 2:1 contrast, it's invisible to many users while still technically present in the DOM.

**What triggers my suspicion:**
- Light gray text on white backgrounds. The aesthetic trend of using #999 or lighter for "secondary" text on white produces contrast ratios well below 4.5:1.
- Colored text on colored backgrounds. Blue text on a dark blue background, green text on a light green background — these are the most common contrast failures because designers match hues without checking values.
- Placeholder text in form inputs. Nearly every product uses light gray placeholder text that fails contrast. The argument "it's a placeholder, not real text" doesn't hold — if it conveys information, it needs to be readable.
- Focus indicators. Many products style focus rings to be subtle. Subtle focus rings fail contrast and fail keyboard users.

**My internal scoring process:**
I categorize findings by impact: text contrast failures are more severe than non-text failures; body text failures are more severe than metadata failures; failures in critical paths (forms, errors, navigation) are more severe than decorative failures.

---

## §3 The audit

### Text contrast
- Does **body text** meet WCAG AA (4.5:1) against its default background? Check both light and dark themes.
- Does **heading text** meet appropriate thresholds? (Large text ≥ 24px or ≥ 18.7px bold: 3:1 minimum.)
- Does **metadata text** (timestamps, captions, helper text) meet 4.5:1? (This is the most common failure — designers use light gray for "secondary" content.)
- Does **link text** have sufficient contrast both against the background AND distinguishable from surrounding non-link text?
- Does **placeholder text** in form inputs meet at least 3:1? (WCAG doesn't explicitly require placeholder contrast, but APCA recommends Lc ≥ 45 for guide text.)
- Does text contrast hold when the text overlays **images or gradients**? (Hero text, card overlays, banner text — check worst-case image behind the text.)

### Interactive element contrast
- Do **buttons** have at least 3:1 contrast between their boundary and the surrounding background?
- Do **form inputs** have at least 3:1 contrast for their border/boundary against the background? (Ghost inputs with very light borders are a common failure.)
- Do **focus indicators** have at least 3:1 contrast against the element AND the background?
- Do **toggle/switch controls** show sufficient contrast between on/off states? (Both states must be independently readable, not just distinguishable from each other.)
- Do **active/selected states** maintain text readability? (A button that changes to a dark background needs light text — check both resting and active states.)

### Disabled and secondary states
- Does **disabled text** have enough contrast to be identifiable as text? (It should be faded but not invisible. Target: 3:1 minimum, even for disabled states.)
- Are **disabled interactive elements** distinguishable from enabled elements AND from decorative elements? (A disabled button that looks like a label is a contrast failure.)
- Do **visited link colors** maintain adequate contrast? (Visited link purple on white can fall below 4.5:1 with certain shades.)

### Non-text contrast
- Do **icons** have at least 3:1 contrast against their background?
- Do **chart elements** (bars, lines, slices) have at least 3:1 contrast against each other AND against the chart background?
- Do **status indicators** (dots, badges, progress bars) have 3:1 contrast? (A tiny green dot on a white background at 3.2:1 is technically passing but practically invisible at small sizes.)
- Do **borders and dividers** have sufficient contrast to be visible? (A 1px border at 1.5:1 contrast is functionally invisible.)

### Polarity and APCA-specific checks
- In **dark mode**, is the text light enough? (Dark mode often has insufficient contrast because designers darken the text "for aesthetics." APCA penalizes dark-on-light less than light-on-dark, so dark mode needs higher luminance text.)
- Are **colored backgrounds** with text checked in both directions? (White text on blue AND blue text on white have different perceptual contrast per APCA.)
- For **small text** (under 16px), is contrast increased beyond the minimum? (APCA recommends Lc ≥ 75 for text under 16px.)
- For **thin fonts** (weight 300 or below), is contrast compensated? (Thin strokes need more contrast than bold strokes at the same size.)

---

## §4 Pattern library

**The gray text epidemic** — Body text is black (#000 or #111). "Secondary" text is #6B7280 (gray-500). On a white background, #6B7280 produces ~4.6:1 — barely passing AA. At 14px, it's readable but strained. On #F9FAFB (gray-50), it drops to ~4.2:1 and fails. Fix: secondary text at #4B5563 (gray-600) or darker. Passing by a thin margin is not passing in practice.

**The dark mode contrast inversion** — Light mode: #111 text on #FFF (21:1 contrast). Dark mode: #E5E7EB text on #1F2937 (11.7:1). Looks fine. But a second text level uses #9CA3AF on #1F2937 — that's 4.4:1, below the psychological threshold where text starts feeling effortful. Fix: in dark mode, be more aggressive with light text values.

**The focus ring disappearing act** — Focus indicator is a 2px outline in the brand blue. Brand blue on white is 3.8:1 — passes the 3:1 non-text minimum. But the focus ring is on a light blue button, where brand blue on light blue is 1.8:1. Fix: focus rings need to be checked against every surface they appear on, not just the page background.

**The chart accessibility gap** — A line chart uses 5 colors. Three of them are distinguishable. Two (light blue and light teal) are nearly identical at low contrast. For colorblind users, four of the five collapse to two groups. Fix: ensure chart colors differ in both hue and value. Add pattern fills or labels as backup.

**The glass morphism failure** — Frosted glass / backdrop blur effect with semi-transparent backgrounds. Text contrast is variable — it passes when the background image is dark, fails when it's light. Fix: add a solid fallback layer behind text, or use enough opacity that worst-case background still provides contrast.

**The placeholder text vanishing act** — Form input placeholder text at #9CA3AF on a white background: 2.6:1 contrast. Fails AA. The team argues "it's just a placeholder, users won't need to read it." But they will — placeholders often serve as the only instruction for what to enter. Fix: placeholders need at least 4.5:1 contrast, or replace with persistent labels that meet contrast.

**The badge text crunch** — Small colored badges (status pills, tags, counts) with white text on medium-saturated backgrounds. "In Progress" in 12px white text on a medium blue badge: the combination of small text, thin weight, and marginal contrast produces unreadable labels. Fix: badges with text need at least 4.5:1 for text under 18px. Use darker background variants or dark text on light badge backgrounds.

**The gradient text gamble** — Text overlaying a gradient background. At one end, the contrast is 7:1. At the other end, it's 2.8:1. The average might pass, but readers at the failing end can't read the text. Fix: check contrast at the worst point of the gradient, not the best point. If any position fails, the gradient fails.

---

## §5 The traps

**The ratio-passing trap** — "We're at 4.52:1, that passes AA." Technically yes. Perceptually, 4.52:1 at 14px is strained reading. WCAG minimums are floors, not targets. Design to APCA Lc 75+ for body text and you'll never have this conversation.

**The automated-test false positive** — Automated contrast checkers test the CSS colors. But if text overlays an image, gradient, or pattern, the CSS background-color is irrelevant — the actual pixels behind the text determine contrast. Automated tools miss every overlay case. Manual checking required.

**The "it's just a label" dismissal** — "That text is just a label, users don't need to read it carefully." If it's on the screen and it's text, someone needs to read it. Labels, captions, footnotes, breadcrumbs — all need readable contrast. If nobody needs to read it, delete it.

**The dark mode pass-through** — "We checked contrast in light mode." Dark mode has different contrast characteristics. The same lightness difference produces different perceptual contrast depending on polarity. Check both themes independently.

---

## §6 Blind spots and limitations

**WCAG 2.x contrast ratio has known flaws.** It overvalues contrast for dark colors and undervalues it for light colors. It treats dark-on-light the same as light-on-dark, which doesn't match human perception. This is why APCA exists. Until WCAG 3.0 adopts APCA formally, products must meet the flawed standard while designing to the better one.

**Contrast doesn't account for font rendering.** The same color pair at the same size renders differently across operating systems (macOS subpixel smoothing vs. Windows ClearType vs. Linux FreeType). Contrast that's comfortable on macOS may be strained on Windows. Test on multiple platforms.

**Contrast doesn't account for ambient lighting.** A screen in a sunlit room has effectively lower contrast than the same screen in a dark room. Products used outdoors or in variable lighting (retail, healthcare, field work) need higher contrast margins.

**High contrast can be harmful.** Pure black (#000) text on pure white (#FFF) at maximum contrast (21:1) causes eye strain for users with certain visual conditions (astigmatism, photosensitivity). Using #111 or #1A1A1A on #FAFAFA provides excellent contrast without the harshness.

**Contrast tools disagree with each other.** WCAG 2.x relative luminance and APCA produce different results for the same color pair, especially for mid-range values and dark mode. A color pair can pass one standard and fail the other. Until WCAG 3.0 is finalized, auditors must decide which standard to apply and document the choice.

---

## §7 Cross-framework connections

| Framework | Interaction with color contrast |
|-----------|--------------------------------|
| **Color theory** | Theory defines the palette; contrast checks whether it's readable. A beautiful palette that fails contrast is unusable. |
| **Typographic hierarchy** | Hierarchy uses value contrast (light vs. dark text) as a tool. If contrast minimums aren't met, the hierarchy tool is broken. |
| **Dark mode** | Dark mode fundamentally changes contrast dynamics. Every contrast decision must be validated per theme. |
| **Visual weight** | Contrast contributes to visual weight. Low-contrast elements recede; high-contrast elements advance. Both need to be intentional. |
| **Form aesthetics** | Form labels, inputs, helper text, and error messages all need independent contrast validation. Forms pack many text levels into small spaces. |
| **Brand expression** | Brand colors must serve contrast requirements. If the brand blue is too light for text, it needs a darker text variant. Brand identity doesn't override readability. |
| **Pixel polish** | At the "last 5%" level, subtle contrast refinements (placeholder text, dividers, disabled states) separate polished products from adequate ones. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (usability/legal) |
|---------|-------------------|---------------------|---------------------------|
| **Marketing site** | Decorative text slightly below 4.5:1 | CTA text below 4.5:1 on colored background | Body text fails contrast — legal compliance risk |
| **Dashboard** | Chart gridlines low contrast | Data labels below 4.5:1 | Critical metric values fail contrast — users misread data |
| **Form-heavy app** | Placeholder text below 3:1 | Error messages below 4.5:1 | Required field indicators invisible against background |
| **E-commerce** | Category labels slightly low | Price text on colored badges fails | Add-to-cart button invisible for low-vision users |
| **Medical/financial** | ANY text below 4.5:1 | ANY interactive element below 3:1 | ANY critical data below 7:1 |

**Severity multipliers:**
- **Legal/compliance context:** Products subject to ADA, Section 508, EAA, or EN 301 549 must treat ALL contrast failures as at minimum moderate severity.
- **User population:** Products for elderly users, healthcare, or government need AAA (7:1) as the effective minimum.
- **Low-vision users:** 4.5:1 is the minimum for 20/20 vision. Low-vision users need 7:1 or higher. If your user base has above-average low-vision rates, shift all thresholds up.

---

## §9 Build Bible integration

| Bible principle | Application to color contrast |
|-----------------|------------------------------|
| **§1.8 Prevent, don't recover** | Build contrast checking into the design token pipeline. Flag failures at token creation, not in QA. |
| **§1.13 Unhappy path first** | Test contrast with worst-case conditions: smallest text, lightest color on lightest background, dark mode, image overlays. |
| **§1.15 Enforce boundaries** | Linting rules (e.g., axe-core, Pa11y, eslint-plugin-jsx-a11y) that block CI on contrast failures make this structural, not advisory. |
| **§6.9 Silent placeholder** | Placeholder text that fails contrast is a silent failure — it exists in the DOM, it conveys information, but users can't read it. |
| **§6.10 Unenforceable punchlist** | "We'll fix contrast later" is a punchlist item that never gets fixed. Enforce at build time or accept the debt. |
| **§6.11 Advisory illusion** | "Our style guide says 4.5:1 minimum" but nothing enforces it. Without automated checking, the rule is an illusion. |
