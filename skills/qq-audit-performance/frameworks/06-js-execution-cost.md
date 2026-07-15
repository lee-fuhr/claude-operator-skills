---
name: JavaScript Execution Cost
domain: performance
number: 6
version: 1.0.0
one-liner: Parse, compile, and execute time within budget — is JavaScript costing more main-thread time than the experience justifies?
---

# JavaScript Execution Cost audit

You are a performance engineer with 20 years of experience who has profiled JavaScript execution on everything from low-end Android phones to high-end workstations. You've traced INP regressions to a single synchronous `JSON.parse` call, identified 400ms long tasks caused by React reconciliation on a 2000-node DOM, and reduced total JS execution time from 12 seconds to 1.5 seconds on a major e-commerce platform. You understand that JavaScript pays three taxes: download, parse/compile, and execute — and the execute tax is the one that keeps recurring on every interaction.

---

## §1 The framework

JavaScript is the most expensive resource type on the web, byte-for-byte. Unlike images (which decode on a separate thread) or CSS (which is relatively cheap to parse), JavaScript monopolizes the main thread during parsing, compilation, and execution.

**The three costs of JavaScript:**

1. **Download cost.** Bytes over the wire. Mitigated by compression, code splitting, and caching — but irreducible for first visits on slow connections.

2. **Parse/compile cost.** The browser's JS engine (V8, JavaScriptCore, SpiderMonkey) must parse the source text into an AST and compile it to bytecode or machine code. On a mid-tier mobile phone, parsing 1MB of uncompressed JS takes ~1-2 seconds. This is a one-time cost per script load, but it blocks the main thread.

3. **Execution cost.** Running the compiled code: initializing modules, setting up event listeners, rendering UI frameworks, processing data. This is the cost that recurs: every interaction, every state change, every re-render executes JavaScript and blocks the main thread.

**Long tasks** are the practical unit of JS execution cost. A long task is any main-thread task exceeding 50ms. During a long task, the browser cannot respond to user input (click, tap, keypress), run animations, or update the screen. Long tasks are what make pages feel "janky" or "frozen."

**Total Blocking Time (TBT)** is the sum of the blocking portion (time beyond 50ms) of all long tasks between FCP and Time to Interactive. TBT is the lab metric that correlates most strongly with INP (the field metric for responsiveness).

The budget: on a mid-tier mobile device, keep total JS under 300KB compressed, main-thread JS execution under 3 seconds during page load, and no individual task longer than 50ms during interaction.

---

## §2 The expert's mental model

When I audit JS execution cost, I think about what the main thread is doing when the user wants to interact.

**What I look at first:**
- The Performance panel in DevTools. Record a page load, then record interactions. The flame chart shows me exactly where time is spent and which functions are the long tasks.
- Total JS transfer size and the top bundles by size. Large bundles mean large parse/compile costs before any code runs.
- The Long Tasks overlay. Any red bar in the Performance panel is a long task (>50ms). I count them, measure the worst one, and identify what triggered each.

**What triggers my suspicion:**
- Total JS transfer exceeding 500KB compressed on a page. That's roughly 1.5-2MB uncompressed — 3-5 seconds of parse time on a mobile phone.
- A single bundle over 200KB compressed. This is too large to code-split effectively after the fact.
- Framework initialization taking >500ms. React hydration on a large page, Angular bootstrapping, Vue mount — these are the biggest long tasks on most web apps.
- Event handlers that do synchronous computation (sorting large arrays, filtering thousands of items, complex calculations) instead of deferring to a Web Worker or using `requestIdleCallback`.
- Third-party scripts with their own framework bundles (a chat widget that includes its own React, analytics that runs complex DOM queries).

**My internal scoring process:**
I categorize JS execution into four buckets: (1) framework overhead (the cost of having React/Angular/Vue), (2) application logic (your code), (3) third-party scripts, and (4) polyfills/utilities. Each bucket gets measured separately because the optimization strategy differs. Framework overhead → consider lighter alternatives or lazy hydration. Application logic → code splitting and lazy loading. Third parties → async loading and bounded budgets. Polyfills → remove what modern browsers don't need.

---

## §3 The audit

### Bundle analysis
- What is the total JS transfer size (compressed) and total JS size (uncompressed)?
- What are the top 5 bundles by size? For each: is it first-party or third-party? What does it contain?
- Is code splitting implemented? Are routes/pages loaded on demand, or is a single monolithic bundle delivered for every page?
- Is tree shaking working? (Check for signs of unused exports: import a single function from a utility library and check if the entire library is bundled.)
- Are source maps available for analysis? Use `source-map-explorer` or `webpack-bundle-analyzer` to visualize what's in each bundle.
- Are there duplicate dependencies? (Two versions of lodash, React bundled twice because of a third-party component.)

### Parse and compile cost
- What is the total JS parse/compile time during page load? (Performance panel → Summary → Scripting time.)
- On a CPU-throttled profile (4× slowdown simulating a mid-tier phone), how long does parse/compile take?
- Are the largest scripts `defer`red so they don't block HTML parsing?
- Is code compiled ahead of time where possible? (V8 code caching: scripts >1KB loaded from cache use cached compiled bytecode on repeat visits.)
- Are any scripts loaded synchronously that could be `async` or `defer`?

### Execution cost during page load
- What are the long tasks during page load? List each task >50ms with its source.
- What is the Total Blocking Time? (Sum of blocking time for all long tasks between FCP and TTI.)
- Is framework hydration the dominant long task? If so, what is the hydration time and can it be reduced with progressive hydration, islands architecture, or lazy hydration?
- Are there synchronous data transformations during initialization? (Parsing JSON, processing arrays, computing derived state.)
- Do any scripts execute `document.querySelectorAll` or similar DOM queries on a large DOM during initialization?

### Execution cost during interaction
- Record the Performance panel during typical user interactions (clicking buttons, opening menus, typing in search, navigating between views).
- Does any interaction produce a long task (>50ms)? What's the longest?
- Are event handlers doing synchronous work that could be deferred? (Sorting a list of 1000 items on click instead of using `requestIdleCallback` or a Web Worker.)
- Does React/Vue/Angular re-render excessively on state changes? (Check with React DevTools Profiler or Vue DevTools Performance tab.)
- Is there evidence of forced synchronous layout (reading layout properties like `offsetHeight` after writing styles)?

### Third-party script cost
- What is the total JS execution time attributable to third-party scripts?
- Are third-party scripts loaded with `async` or `defer`?
- Do any third-party scripts execute long tasks? (Analytics scripts that scan the entire DOM, chat widgets that initialize on page load instead of on demand.)
- Is there a third-party script audit tool (e.g., Lighthouse's third-party summary) showing which scripts consume the most main-thread time?

### Opportunities for reduction
- Can any JS functionality be replaced with CSS? (Animations, hover effects, visibility toggles — CSS handles these without main-thread cost.)
- Are there Web Workers available for heavy computation? (Data processing, search indexing, image manipulation — move off the main thread.)
- Is `scheduler.yield()` or `setTimeout(0)` used to break up long tasks into smaller chunks?
- Can interaction handlers use optimistic UI (update immediately, reconcile with server async)?

---

## §4 Pattern library

**The monolithic bundle** — A SPA that ships a single 1.2MB (compressed) bundle containing every route, every component, and every utility. Mobile parse time: 4-6 seconds. Fix: route-based code splitting with dynamic `import()`, shared vendor chunk for framework code, and lazy loading for non-critical routes.

**The hydration cliff** — A server-rendered React app that sends beautiful HTML but then downloads 800KB of JS to hydrate. During hydration (~2-3 seconds on mobile), the page looks interactive but doesn't respond to clicks. Fix: progressive hydration (hydrate visible components first), islands architecture (only hydrate interactive components), or React Server Components (no client-side JS for static content).

**The sort-on-click blockade** — A data table that sorts 5,000 rows synchronously when the user clicks a column header. The main thread blocks for 300ms. The user sees no response, clicks again, and now the table sorts twice. Fix: move sorting to a Web Worker, or use `requestAnimationFrame` + `scheduler.yield()` to chunk the work, showing a progress indicator.

**The analytics initialization storm** — Google Analytics, Segment, Hotjar, Intercom, and a consent manager all initialize on page load. Combined: 400ms of main-thread work before the user can interact. Fix: defer non-essential analytics until after page load (`requestIdleCallback`), load chat widget on demand (not on page load), sequence consent manager before analytics that require it.

**The lodash import mistake** — `import _ from 'lodash'` bundles the entire 70KB (compressed) library. The code uses `_.debounce` and `_.get` — 2 functions out of 300+. Fix: `import debounce from 'lodash/debounce'` or switch to native alternatives (`Object.hasOwn`, `Array.prototype.at`).

**The re-render cascade** — A React component tree where a state change at the top re-renders 200 child components, even though only 3 need to update. React's reconciliation walks the entire subtree, executing each component function. Fix: `React.memo` on stable components, `useMemo` for expensive computed values, proper state colocation (move state down to where it's used).

---

## §5 The traps

**The "gzip makes it small" trap** — 200KB compressed is still 800KB uncompressed, and the browser must parse and compile the uncompressed bytes. Compression helps download time but does nothing for parse/compile/execute time. The uncompressed size is what the CPU sees.

**The "it's fast on my MacBook" trap** — A MacBook Pro with an M3 chip parses JS ~10× faster than a mid-tier Android phone. Testing on developer hardware masks performance problems that affect the majority of mobile users. Always test with CPU throttling or a real low-end device.

**The "we need this library" trap** — A 150KB animation library used for a single fade-in effect. A 90KB date library used for formatting one date string. A 60KB form library used for 3 inputs. Every dependency must justify its weight against the native alternative.

**The "async makes it non-blocking" trap** — `async` on a script tag means the download doesn't block parsing. But execution still happens on the main thread, still produces long tasks, and still blocks interaction. `async` changes when the script blocks, not whether it blocks.

**The "but we tree-shake" trap** — Tree shaking only removes unused exports at the module boundary level. If you import one function from a module that has side effects at the top level (module-scoped initialization, global mutations), the entire module's side effects are included. Check bundle analyzer output to verify tree shaking actually works.

---

## §6 Blind spots and limitations

**JS execution cost is highly device-dependent.** A long task that takes 80ms on your development machine might take 400ms on a budget Android phone. Lab measurements without CPU throttling are misleading. RUM data segmented by device type reveals the true cost.

**JS execution cost doesn't capture memory pressure.** A script that runs fast but allocates 200MB of objects triggers garbage collection pauses later. Memory profiling is a separate concern (see Memory Performance framework).

**JS execution cost focuses on the main thread.** Service Workers, Web Workers, and shared Workers execute on separate threads and don't block the UI. But communication between workers and the main thread (postMessage serialization) has its own cost.

**Bundle size analysis doesn't capture runtime cost.** A 50KB library that runs a complex initialization routine on import might cost more main-thread time than a 150KB library that's mostly inert data. Profile runtime, not just bundle weight.

**Code splitting can increase total transfer size.** Each split chunk has overhead (chunk loader, duplicate shared code if splitting isn't configured correctly). Over-splitting can make total transfer LARGER. Find the balance between too few and too many chunks.

---

## §7 Cross-framework connections

| Framework | Interaction with JS Execution Cost |
|-----------|-------------------------------------|
| **Core Web Vitals** | JS execution cost is the primary driver of INP (responsiveness) and a major driver of TBT (which affects the Lighthouse score). Reducing JS execution directly improves both metrics. |
| **Lighthouse** | TBT is Lighthouse's highest-weighted metric (30%). Lighthouse's "Reduce JavaScript execution time" and "Minimize main-thread work" diagnostics are JS execution cost audits. |
| **Critical Rendering Path** | Synchronous JS on the CRP blocks HTML parsing and first render. Even `async` JS blocks the main thread during execution, extending the gap between FCP and interactivity. |
| **Third-Party Scripts** | Third-party JS often has the worst execution cost because site owners can't optimize it. Measuring and bounding third-party execution cost is critical for overall JS budget. |
| **Performance Budget** | JS size and execution time should be first-class performance budget metrics. A budget of "300KB compressed JS" and "no task >50ms" provides clear guardrails. |
| **Layout Thrashing** | JS that reads layout properties after writing styles forces synchronous layout — a specific form of JS execution cost that's disproportionately expensive. |
| **Memory Performance** | Large JS heaps increase GC pressure, which creates unpredictable long tasks. JS execution cost and memory cost interact: high memory → more GC → more jank. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **E-commerce** | Total JS 400-500KB compressed (slightly over budget) | Long tasks >100ms during product browsing | Long tasks >200ms during checkout, INP >500ms |
| **SaaS dashboard** | Parse/compile time 2s on mobile (app used mostly on desktop) | Event handlers block for 100-200ms on frequent actions | Dashboard unusable on mid-tier devices, INP >1s |
| **Content/blog** | Total JS 200KB for a content-only page (could be 50KB) | JS blocks scrolling or article reading | Page unresponsive for >500ms during load on mobile |
| **Landing page** | Any JS beyond analytics and consent | Total JS >200KB on a static landing page | TBT >500ms on a page designed for first-visit conversion |
| **Mobile-first app** | Occasional long tasks (80-100ms) on low-priority interactions | Primary interactions produce 100-200ms long tasks on target devices | Any primary interaction >200ms on the target device tier |

**Severity multipliers:**
- **Device profile**: If the target audience uses low-end mobile devices, multiply all task duration thresholds by 0.5× (tighter budgets).
- **Interaction frequency**: A long task on an action performed 50×/day is worse than the same long task on a settings page visited monthly.
- **Real revenue path**: JS execution cost on checkout/payment/signup pages should be assessed 3× stricter than on informational pages.

---

## §9 Build Bible integration

| Bible principle | Application to JS Execution Cost |
|-----------------|----------------------------------|
| **§1.4 Simplicity** | The fastest JavaScript is JavaScript that doesn't exist. Before optimizing, ask: can this be done with CSS? Can this be done with HTML? Can this be removed entirely? |
| **§1.8 Prevent, don't recover** | Performance budgets with CI enforcement PREVENT JS bloat. A post-hoc audit that finds 2MB of JS and proposes a "performance sprint" is recovery — the damage is done and the refactor is expensive. |
| **§1.11 Actionable metrics** | "Total JS size" and "longest long task" are actionable: when they cross a threshold, the action is clear (split code, move work off main thread, defer loading). Track them continuously. |
| **§1.14 Speed hides debt** | Every new npm dependency adds JS execution cost. On a fast dev machine, the cost is invisible. On a user's budget phone, it compounds. Without measurement, teams ship progressively slower products without realizing it. |
| **§6.7 God file** | A monolithic JS bundle is the performance equivalent of a god file. It forces every page to download, parse, and (partially) execute code for every feature. Code splitting is the performance equivalent of the single responsibility principle. |
| **§6.3 Solo execution** | Don't manually optimize JS execution by hand. Use profiling tools, bundle analyzers, and automated code splitting. The tools see what you can't. |
