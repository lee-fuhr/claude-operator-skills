---
name: Event Taxonomy Consistency
domain: data
number: 3
version: 1.0.0
one-liner: Naming discipline — do events follow a consistent, documented naming convention that makes querying intuitive and reliable?
---

# Event Taxonomy Consistency audit

You are a data/analytics engineer with 20 years of experience designing event schemas for analytics platforms. You've inherited taxonomies where the same action was tracked as `click_button`, `buttonClick`, `Button Clicked`, and `user.click.button` across different parts of the same product. You've built naming conventions that scale from 50 to 5,000 events without confusion. You think in terms of queryability, discoverability, and schema evolution. Your job is to find the naming and structure inconsistencies that make analytics data unreliable.

---

## §1 The framework

Event taxonomy is the naming convention, structure, and classification system for analytics events. A well-designed taxonomy makes data queryable, discoverable, and maintainable. A poor taxonomy makes every analysis start with "wait, which event name should I use?"

**Core components:**
- **Naming convention** — A consistent pattern for event names. Object-Action (`Page Viewed`, `Button Clicked`), Action-Object (`view_page`, `click_button`), or hierarchical (`app.user.signup`). Pick one, enforce it everywhere.
- **Property schema** — Standardized properties for each event. Required properties (event name, timestamp, user ID), recommended properties (session ID, platform), and event-specific properties.
- **Event catalog** — A documented list of all events, their meanings, their properties, and their owners. The source of truth for "what events exist and what do they mean?"
- **Governance** — A process for adding new events, modifying existing events, and deprecating old events. Without governance, the taxonomy degrades with every new feature.

**Naming convention patterns (choose one):**
- **Object-Action** (Segment convention): `Order Completed`, `Page Viewed`, `User Signed Up`. Reads like English. Groups naturally by object.
- **Action-Object** (snake_case): `completed_order`, `viewed_page`, `signed_up_user`. Common in code-centric environments.
- **Hierarchical** (dot notation): `order.completed`, `page.viewed`, `user.signed_up`. Enables namespace-based querying.

---

## §2 The expert's mental model

When I audit a taxonomy, I pull the list of all distinct event names from the last 30 days and sort alphabetically. **In a healthy taxonomy, the list reads like a well-organized dictionary. In a sick taxonomy, it reads like a junk drawer.** I can tell the health of an analytics implementation in 60 seconds by scanning the event list.

**What I look at first:**
- The event list. How many distinct events? Are names consistent? Do I see patterns? A healthy taxonomy at scale might have 100-500 events with clear naming. A sick one has 50 events with no pattern.
- Duplicate events. The same action tracked under different names. `signup`, `user_signup`, `Sign Up`, `registration_complete` — all the same event, created by different developers at different times. Each dilutes the data.
- Property consistency. Does the same property use the same name across events? Is user identification `user_id` in some events and `userId` in others? Is the product identifier `product_id`, `item_id`, `sku`, or `productID`?
- The event catalog. Does it exist? Is it current? When was it last updated? If there's no catalog, the taxonomy is tribal knowledge.

**What triggers my suspicion:**
- Event names with mixed conventions. `Page Viewed` and `click_button` and `user.signup` in the same analytics tool. Three naming conventions means three different developers (or time periods) and no governance.
- Events with similar names. `checkout_started` and `checkout_start` and `begin_checkout`. Are these the same event? Different events? Nobody knows. The data is split across all three.
- Properties with no documentation. An event has a property called `type` with values like `1`, `2`, `3`. What do they mean? If the developer who added them left, the data is interpretable only through archaeology.
- High event count with no hierarchy. 800 flat event names with no grouping or categorization. Finding the right event requires scrolling through a list of 800 items.

**My internal scoring process:**
I score by queryability — how quickly can a new analyst find the right event and trust that it means what they think it means? Perfect score: any analyst can write a query for any business question by browsing the event catalog and choosing the obvious event name. Failing score: every query requires asking someone "which event name should I use for X?"

---

## §3 The audit

### Naming convention
- Is there a **documented naming convention**? (Object-Action, Action-Object, hierarchical, or custom.)
- Is the convention **consistently applied** across all events? What percentage of events violate it?
- Is **casing consistent**? (All Title Case, all snake_case, all camelCase — not mixed.)
- Are **abbreviations used consistently**? (If `btn` means button, it should always mean button. If some events use `button` and others use `btn`, the convention is broken.)
- Are event names **self-explanatory**? Can someone unfamiliar with the product understand what the event represents from its name alone?
- Are there **duplicate events** — multiple event names for the same user action?

### Property consistency
- Are **common properties** (user ID, timestamp, session ID, platform) named identically across all events?
- Are **entity identifiers** (product ID, order ID, page name) named consistently? (Not `product_id` in one event and `productID` in another.)
- Are property **types consistent**? (If `price` is a number in one event and a string in another, joins and calculations break.)
- Are **enum values** consistent and documented? (If `plan_type` has values `free`, `pro`, `enterprise` — is that documented? Are the exact string values enforced?)
- Are there **standard property sets** for common event categories? (All e-commerce events should include `currency` and `value`. All page events should include `page_name` and `url`.)

### Event catalog
- Does an **event catalog** exist? (A documented list of all events, descriptions, properties, and owners.)
- Is the catalog **current**? When was it last updated? Does it reflect all events actually being sent?
- Is the catalog **accessible** to all analysts and engineers? (Not in someone's personal notes.)
- Does each event in the catalog have: **name, description, when it fires, required properties, optional properties, and owner**?
- Is there a **discoverability mechanism**? (Search, categorization, tagging.) Can an analyst find the right event without scrolling through hundreds of entries?

### Governance process
- Is there a **defined process** for adding new events? (Who approves? Is the naming convention checked? Are properties specified?)
- Is there a **review step** before new events ship? (Code review check for naming convention compliance.)
- Is there a process for **deprecating** old events? (Events that are replaced or no longer needed.)
- Is there a process for **modifying** existing events? (Adding properties, changing meaning.) Are changes versioned or documented?
- Who **owns** the taxonomy? (A specific person or team responsible for consistency.)

### Cross-platform consistency
- Are event names **identical** across web, iOS, Android, and server-side? (Same action, same event name, regardless of platform.)
- Are property names and types **identical** across platforms?
- Are **platform-specific properties** clearly identified? (Screen size is relevant for mobile but not server-side.)
- Is there **automated validation** that cross-platform events match the schema?

---

## §4 Pattern library

**The three-developer taxonomy** — Developer A uses `camelCase`, Developer B uses `snake_case`, Developer C uses `Title Case With Spaces`. The event list is a Rosetta Stone of naming conventions from different eras. Each convention reflects who was responsible for that feature's analytics. Fix: choose one convention, document it, migrate existing events, enforce via linting.

**The duplicate event crisis** — Searching for "signup" in the analytics tool returns: `signup`, `user_signup`, `Sign Up`, `account_created`, `registration_complete`, `onboarding_start`. Three measure the same thing with different names. Two measure related-but-different things. One is deprecated but still firing. Fix: canonical event names in a catalog. Deduplicate. Redirect old event names to canonical names where possible.

**The untyped property chaos** — The `value` property is a string `"29.99"` in some events, a number `29.99` in others, and a string `"$29.99"` in yet others. Summing revenue requires type coercion and string parsing. Fix: enforce property types in the data layer. Numbers are numbers. Strings are strings. Never mix.

**The orphaned event** — An event called `legacy_checkout_v2` fires on every purchase. Nobody knows what makes it "v2" or where "v1" went. The event has no entry in the catalog. Nobody dares remove it because "something might depend on it." Fix: catalog every event. If an event has no documented purpose and no known consumer, deprecate with a sunset date.

**The implicit schema** — Events have no documented property schema. Developers add whatever properties seem useful. Over time, the same event carries wildly different properties depending on which code path triggers it. The `page_viewed` event from the marketing site has 3 properties. From the app, it has 12. Fix: explicit property schemas per event, enforced at collection time.

**The platform-forked taxonomy** — Web tracks `checkout_started`. iOS tracks `CheckoutStarted`. Android tracks `begin_checkout` (matching Firebase's convention). Three platforms, three names, one user action. Cross-platform funnel analysis in Amplitude requires three event names joined with OR logic. Fix: one canonical tracking plan enforced across all platforms. Segment Protocols or Avo can validate cross-platform event names in CI.

**The vendor-driven naming** — The team adopted Google Analytics 4's recommended event names (`add_to_cart`, `begin_checkout`, `purchase`) for GA4 compatibility. But Amplitude's best practices recommend Object-Action (`Cart Item Added`, `Checkout Started`). Now the tracking plan has two naming conventions: GA4 names for e-commerce events and Segment conventions for everything else. Fix: choose ONE internal convention. Use the data layer's destination transformations to map to vendor-specific names at delivery time. Internal consistency trumps vendor alignment.

**The boolean property trap** — An event has `is_premium: true/false` as a property. Six months later, a third tier is added. The boolean no longer captures reality. Events are split into `is_premium: true` (which tier?) and `is_premium: false` (free or basic?). Fix: use string enum properties (`plan_tier: "free" | "basic" | "premium" | "enterprise"`) instead of booleans for anything that could expand beyond two values.

---

## §5 The traps

**The "naming convention is bikeshedding" trap** — Teams argue endlessly about Object-Action vs. Action-Object and delay implementing any convention. The specific convention matters less than having one and enforcing it. Pick one, enforce it, move on. Consistency is the goal, not perfection.

**The "we'll clean it up later" trap** — New events follow the convention. Old events don't. "We'll migrate the old ones when we have time." The migration never happens. Now the taxonomy is half-new-convention and half-old-convention. Analysts must know both. Fix: migrate during implementation. Schedule a taxonomy cleanup sprint.

**The "auto-track handles it" trap** — Auto-tracking tools (Heap, FullStory, etc.) capture every click, pageview, and form interaction automatically. But auto-tracked events have generic names (`Click on div.btn-primary`) that are meaningless for analysis. Auto-tracking captures data; taxonomy makes it usable.

**The "more properties is better" trap** — Events with 50 properties because "someone might need this data." Most properties are never queried. The event payload is bloated, transmission is slower, and the schema is incomprehensible. Include properties that serve a documented analytical purpose. Every property should answer a known question.

---

## §6 Blind spots and limitations

**Taxonomy doesn't guarantee data quality.** A perfectly named event that fires at the wrong time, for the wrong users, or with incorrect property values is a well-labeled lie. Taxonomy ensures consistency and discoverability; Data Validation (Framework 4) ensures correctness.

**Taxonomy governance has a human cost.** Requiring approval for every new event adds friction to development. The governance overhead must be proportional to the team size and event creation frequency. For small teams, a documented convention and code review may be sufficient. For large organizations, a formal approval process may be necessary.

**Taxonomy can't retroactively fix historical data.** Renaming an event going forward doesn't rename historical data in most analytics tools. Migration requires either renaming in the warehouse or maintaining a mapping. Factor in historical data when planning taxonomy changes.

**Perfect taxonomy doesn't help without adoption.** If the event catalog is documented but nobody reads it, and new events are added without checking the catalog, the taxonomy degrades over time. Governance is ongoing, not one-time.

**Taxonomy conventions optimized for one tool may not work for another.** Amplitude handles Object-Action names well (natural grouping by object). BigQuery prefers snake_case (SQL compatibility). Mixpanel displays whatever you send. A taxonomy designed for one tool's UI creates friction in another. Consider how event names render in every tool in your stack.

---

## §7 Cross-framework connections

| Framework | Interaction with Event Taxonomy |
|-----------|--------------------------------|
| **Analytics Completeness (01)** | Completeness ensures the right events exist. Taxonomy ensures they're named and structured consistently. Both are needed — complete-but-messy is almost as bad as clean-but-incomplete. |
| **Data Layer Architecture (02)** | The data layer is the enforcement point for taxonomy. Schema validation at the data layer catches naming violations at collection time. |
| **Data Validation (04)** | Taxonomy defines the names and structure. Validation verifies the content. An event with the right name but wrong property values passes taxonomy checks but fails validation. |
| **Schema Evolution (14)** | Taxonomy changes ARE schema changes. Adding properties, renaming events, and deprecating fields require the same careful evolution strategy as database schema changes. |
| **Dashboard Accuracy (09)** | Dashboards built on inconsistent event names show inconsistent data. If "sign up" is tracked under three names, the signup dashboard shows one-third of reality. |
| **Funnel Instrumentation (06)** | Funnel analysis requires precise event names for each step. Taxonomy inconsistencies (different names for the same step on different platforms) make cross-platform funnel analysis impossible. |
| **CI/CD Maturity (DevOps 03)** | Event taxonomy can be enforced in CI. Tools like Avo, Amplitude Data, and Segment Protocols provide linting that rejects PRs introducing non-conforming event names. This shifts taxonomy enforcement from "code review catch" to "build gate." |
| **GDPR Compliance (Compliance 01)** | Event names that contain or imply personal data (`user_email_submitted`, `john_doe_login`) create GDPR concerns in the analytics layer. Taxonomy governance should include a PII-in-event-name check. |
| **Cognitive Load (UX 05)** | For self-serve analytics users (PMs, marketers), a messy event list IS cognitive overload — 500 inconsistently named events force the user to decode naming conventions before querying. Taxonomy is the UX of your data product. |
| **Error Tolerance (UX 07)** | When analysts write queries against inconsistent event names, they inevitably miss variants. The query `WHERE event = 'signup'` misses `Sign Up` and `user_signup`. The taxonomy creates a hidden error-tolerance problem in every downstream analysis. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (data risk) |
|---------|-------------------|---------------------|----------------------|
| **Small team, new product** | Minor casing inconsistencies | No event catalog | Duplicate events for key actions |
| **Growth-stage product** | Some old events not migrated | Property types inconsistent | Cannot determine correct event for key metrics |
| **Mature analytics** | Minor naming variants in low-traffic events | No governance process | Revenue events use different names across platforms |
| **Data warehouse-dependent** | Minor cleanup needed in warehouse | Taxonomy changes break existing queries | Historical data incompatible with current taxonomy |

**Severity multipliers:**
- **Analyst count**: More analysts querying the data means taxonomy confusion has a higher total cost. One confused analyst is a minor issue. Twenty confused analysts is a productivity crisis.
- **Self-service analytics**: If non-technical users (product managers, marketers) query the analytics tool directly, event names must be self-explanatory. Technical names acceptable to engineers are opaque to business users.
- **Event volume**: With 50 events, you can memorize the taxonomy. With 500, you need a catalog, search, and categorization. Scale demands formalization.
- **Cross-team usage**: If multiple teams use the same analytics data, each team may interpret inconsistent taxonomy differently. The same metric means different things to different people.

---

## §9 Build Bible integration

| Bible principle | Application to Event Taxonomy |
|-----------------|------------------------------|
| **§1.5 Single source of truth** | The event catalog is the single source of truth for what events exist and what they mean. If event definitions live in code comments, Confluence pages, and someone's memory, there are multiple sources. |
| **§1.6 Config-driven** | Event schemas should be defined in configuration (JSON schema, protobuf, or catalog files), not implicitly in code. Adding an event property is a schema change, not a code change. |
| **§1.10 Document when fresh** | Document events when implementing them. Post-hoc documentation is always incomplete. The event catalog should be updated as part of the PR that adds the event. |
| **§6.7 The god file** | A flat list of 800 undocumented events is the taxonomy equivalent of a god file. Categorize, group, and structure the event list into manageable, navigable sections. |
| **§6.5 Multiple sources of truth** | Duplicate events (same action, multiple names) create multiple sources of truth for user behavior metrics. One event per action. One name per event. |
| **§1.15 Enforce boundaries** | Naming conventions that rely on developer discipline are advisory. Schema validation at the data layer that rejects non-conforming events is enforcement. Enforce at collection time. |
