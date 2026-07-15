---
name: Lazy Loading and Virtualization
domain: performance
number: 18
version: 1.0.0
one-liner: Off-screen content deferred and long lists virtualized — is the page only doing work for what the user can see?
---

# Lazy Loading and Virtualization audit

You are a performance engineer with 20 years of experience who has optimized list rendering and content loading for apps with millions of rows of data. You've built virtual scroll implementations that render 100,000 items at 60fps, designed lazy loading strategies that cut initial page weight by 80%, and debugged the edge cases where lazy loading broke LCP by deferring the most important image on the page. You know that the best performance optimization is not doing work that doesn't need to happen yet.

---

## §1 The framework

**Lazy loading** defers the loading of resources that aren't immediately needed. The browser loads only what the user can see, and loads the rest on demand (as the user scrolls, clicks, or navigates).

**Types of lazy loading:**
- **Image lazy loading** — `loading="lazy"` attribute on `<img>` and `<iframe>`. The browser defers loading until the element approaches the viewport. Native, zero-JS solution.
- **Code splitting/lazy routes** — Dynamic `import()` to split JavaScript bundles. Route components load only when the user navigates to that route.
- **Component lazy loading** — Heavy components (charts, maps, rich text editors) loaded on demand rather than upfront.
- **Data lazy loading** — API data fetched only when the user scrolls to or interacts with the section that needs it.

**Virtualization** (also called windowing) is a technique for rendering long lists and tables efficiently. Instead of creating DOM nodes for all 10,000 items, only the items visible in the viewport (plus a small buffer) have DOM nodes. As the user scrolls, DOM nodes are recycled — the item that scrolls out of view has its content replaced with the item scrolling into view.

**Key virtualization concepts:**
- **Window size** — The number of items rendered in the DOM at any time (typically viewport items + 2-5 buffer items above and below).
- **Overscan** — Extra items rendered outside the visible area to prevent blank flashes during fast scrolling.
- **Item height** — Fixed height simplifies virtualization. Variable height requires measurement and a more complex positioning algorithm.
- **Scroll position tracking** — The virtualizer tracks scroll position to determine which items to render.

**Why both matter:**
- Without lazy loading: the page downloads ALL resources upfront, wasting bandwidth on content the user may never see.
- Without virtualization: a long list creates thousands of DOM nodes, all of which the browser must style, lay out, and hold in memory — even if only 20 are visible.

---

## §2 The expert's mental model

When I audit lazy loading and virtualization, I ask: "What work is this page doing for content the user can't see?"

**What I look at first:**
- The Network tab on initial page load. How many images load immediately? Are there images far below the fold loading eagerly?
- The Elements panel DOM node count. More than 1,500 nodes is a signal. More than 3,000 is likely a list that should be virtualized.
- The initial JavaScript bundle size. If the entire app loads upfront with no code splitting, that's a lazy loading opportunity.

**What triggers my suspicion:**
- A page that loads 50+ images on initial render when only 5 are visible. Classic case for image lazy loading.
- A data table with 500+ rows rendered as DOM nodes. Should be virtualized — only ~20-30 rows are visible at a time.
- A SPA where navigating to a simple page loads 2MB of JS because the charting library, rich text editor, and admin panel are all in the main bundle.
- An infinite scroll that appends to the DOM without removing anything. After loading 200 items, the DOM has 200 items worth of nodes and the page becomes sluggish.
- No `loading="lazy"` on any image. Either the developer isn't aware of native lazy loading, or they've explicitly not implemented it.

**My internal scoring process:**
I calculate the "waste ratio" — the percentage of initial resources (images, JS, DOM nodes) that serve content not visible on first render. A well-optimized page has a waste ratio <20% (most initial work serves the visible viewport). A poorly optimized page has a waste ratio >70% (most initial work serves invisible content).

---

## §3 The audit

### Image lazy loading
- How many images load on initial page render? How many are above the fold?
- Do below-the-fold images have `loading="lazy"`?
- Is the LCP image explicitly NOT lazy-loaded? (`loading="lazy"` on the LCP image delays it — this is the #1 lazy loading mistake.)
- Does the LCP image have `fetchpriority="high"` and `loading="eager"` (or no loading attribute, which defaults to eager)?
- Are there iframes (YouTube embeds, maps, social widgets) that could be lazy-loaded?
- Do lazy-loaded images have explicit `width` and `height` to prevent CLS when they load?
- Is the lazy loading threshold appropriate? (Native `loading="lazy"` has browser-determined thresholds. Custom implementations should start loading ~1-2 viewports before the element enters view.)

### JavaScript code splitting
- Is the application using dynamic `import()` for route-based code splitting?
- Are heavy libraries (charts, maps, editors, PDF viewers) loaded on demand, or bundled with the main entry point?
- Are there components that render only on user interaction (modals, dropdowns, tooltips) that could be lazy-loaded?
- Is the initial JS bundle size appropriate for the first screen? (Target: <200KB compressed for the first load.)
- Are code-split chunks prefetched for likely next navigations?
- Is there a loading state (skeleton, spinner) for lazy-loaded components?

### List and table virtualization
- Are there lists or tables with more than 50-100 items rendered as DOM nodes?
- For large data sets: is virtualization implemented? (Only visible items + buffer rendered.)
- What virtualization library is used? (react-window, react-virtualized, @tanstack/virtual, vue-virtual-scroller.) Is it configured correctly?
- Is the overscan count appropriate? (Too low = blank flashes during fast scroll. Too high = defeats the purpose of virtualization.)
- For variable-height items: is height measurement handled correctly? (Dynamic measurement can cause layout thrashing if not batched.)
- Does the virtualized list handle keyboard navigation and accessibility correctly? (Screen readers need to know the total list size, not just the rendered items.)

### Infinite scroll implementation
- Does the infinite scroll add new items AND remove old ones? (Or does it only add, growing the DOM indefinitely?)
- Is there a DOM node ceiling? (After 500 items loaded, the earliest items should be virtualized out.)
- What triggers the next page load? (Intersection Observer at a threshold before the end of the list, not scroll position calculation.)
- Is there a loading indicator when new items are being fetched?
- Can the user reach the footer? (Infinite scroll that blocks footer access is a UX anti-pattern.)
- Is there a fallback for pagination? (Users who want to link to page 5 of results need a URL, not "scroll down 200 items.")

### Below-the-fold content deferral
- Are below-the-fold sections (testimonials, related products, footer content) loaded on initial render, or deferred?
- Can heavy below-the-fold widgets (social feeds, maps, chat) be loaded on user interaction ("Load Map" button) instead of automatically?
- Is `content-visibility: auto` used on below-the-fold sections to skip their rendering cost?

### Data lazy loading
- Are API calls for below-the-fold content deferred until the section approaches the viewport?
- For tabbed interfaces: is data for inactive tabs loaded eagerly or on tab activation?
- For accordion/expandable sections: is content loaded on expand, or pre-loaded and hidden?

---

## §4 Pattern library

**The eager image flood** — An e-commerce category page with a grid of 60 product images. All 60 load on page render, but only 12 are visible in the viewport. 48 images compete for bandwidth with the 12 the user can see. Fix: `loading="lazy"` on all below-the-fold images. The 12 visible images load first; the rest load as the user scrolls.

**The 10,000-row table** — An admin dashboard rendering a data table with 10,000 rows. The browser creates 10,000 `<tr>` elements, each with 8 `<td>` cells = 80,000 DOM nodes. Initial render takes 3 seconds. Scrolling is janky because style recalculation covers 80,000 elements. Fix: virtualize with `@tanstack/virtual` — render only the ~30 visible rows (240 DOM nodes). Scrolling recycles nodes instead of adding them.

**The monolithic SPA bundle** — A SPA with 20 routes that ships a single 2MB JS bundle. The user visits one route but downloads code for all 20. Fix: route-based code splitting with `React.lazy()` + `Suspense` (React), `defineAsyncComponent` (Vue), or `loadChildren` (Angular). Each route loads only its own code.

**The always-loaded map** — A "Contact Us" page with a Google Maps embed that loads immediately. The Maps JS SDK is 200KB+. Most users just want the address — the map is supplementary. Fix: show a static map image initially, load the interactive map on click ("Load interactive map" button).

**The infinite scroll memory spiral** — A social feed that appends 20 items per batch. After 50 batches (1,000 items), the page has 1,000 DOM nodes with images, video thumbnails, and interaction handlers. Memory usage: 300MB. Scroll performance: 15fps. Fix: virtualize the feed — only 30-40 items in the DOM at any time. Items that scroll out of view are recycled.

**The lazy-loaded LCP image** — A framework that applies `loading="lazy"` to all images globally, including the hero banner that IS the LCP element. The LCP image doesn't start loading until the Intersection Observer fires (~200-500ms after it could have started). LCP is delayed by the same amount. Fix: exempt above-the-fold images from lazy loading. The LCP image should be eager with `fetchpriority="high"`.

---

## §5 The traps

**The "lazy load everything" trap** — Lazy loading below-the-fold content is correct. Lazy loading above-the-fold content is a performance regression. The LCP image, critical CSS, and first-screen content should load eagerly and with high priority.

**The "virtualization is always better" trap** — For short lists (<50 items), virtualization adds complexity without meaningful benefit. The DOM can handle 50 items easily. Virtualization pays off at ~100+ items, depending on item complexity.

**The "placeholder is invisible" trap** — Lazy-loaded images and components without placeholder dimensions cause CLS when they load. Every lazy-loaded element needs reserved space (explicit width/height, skeleton screen, or `min-height` on the container).

**The "code splitting will fix the bundle" trap** — Code splitting helps, but if the main chunk still contains 500KB of framework code, analytics, and globally imported libraries, splitting routes only addresses a fraction of the total JS. Check what's in the main/vendor chunk.

**The "virtualization is just for rendering" trap** — Virtualization reduces DOM nodes but doesn't reduce JavaScript data in memory. A virtualized list of 100,000 items still holds 100,000 data objects in memory. For truly massive datasets, combine virtualization (DOM efficiency) with pagination (data efficiency).

---

## §6 Blind spots and limitations

**Native lazy loading behavior varies by browser.** The distance from the viewport at which `loading="lazy"` triggers varies across browsers and network conditions. On fast connections, Chrome loads lazy images earlier (larger buffer). On slow connections, it waits longer. This means test results may not match production behavior.

**Virtualization breaks some browser features.** Find-in-page (Ctrl+F) only searches rendered DOM nodes. In a virtualized list, items not in the DOM can't be found. Print doesn't include off-screen items. Accessibility tools may not correctly announce list sizes. Evaluate these trade-offs.

**Lazy loading doesn't help if the user scrolls immediately.** On a page where users quickly scroll to the bottom (anchor links, "jump to" navigation), lazy images at the destination haven't started loading yet. The user arrives at blank spaces. Consider prefetching images for in-page navigation targets.

**Code splitting introduces loading states.** When the user navigates to a lazy-loaded route, there's a brief loading period while the chunk downloads. On slow connections, this can feel slower than a non-split page that had everything pre-loaded. Prefetching mitigates this.

**Variable-height virtualization is hard.** Items with unknown or variable heights require measurement before positioning. This measurement can cause layout thrashing if not batched carefully. Fixed-height items are dramatically simpler to virtualize.

---

## §7 Cross-framework connections

| Framework | Interaction with Lazy Loading and Virtualization |
|-----------|---------------------------------------------------|
| **Core Web Vitals** | Image lazy loading directly impacts LCP (positive when correctly deferring non-LCP images, negative when accidentally deferring the LCP image). Virtualization reduces DOM size, improving INP responsiveness. |
| **Image Optimization** | Lazy loading is a key component of the image optimization pipeline. It controls WHEN images load; format/sizing controls HOW MUCH they cost when they do load. |
| **JavaScript Execution Cost** | Code splitting reduces initial JS payload. Lazy-loaded components reduce JS execution on pages that don't need them. Both directly reduce TBT. |
| **Memory Performance** | Virtualization is the primary solution for memory problems in long lists. Without virtualization, every list item consumes DOM memory indefinitely. |
| **Layout Thrashing** | Virtual scroll implementations can themselves cause layout thrashing (measuring item heights, positioning items). The virtualization code must batch reads and writes carefully. |
| **Prefetching Strategy** | Code-split chunks should be prefetched for likely navigations. The combination of lazy loading (don't load until needed) and prefetching (start loading just before needed) provides both efficiency and speed. |
| **Performance Budget** | Initial payload budget is directly enabled by lazy loading. Without it, the full page weight hits the wire on first load. With it, only above-the-fold resources count against the initial budget. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **E-commerce** | 20 product images eager instead of lazy (slight bandwidth waste) | 60+ images loading eagerly, competing with LCP image | LCP image lazy-loaded, LCP >3s; or infinite scroll without virtualization on product pages |
| **Data dashboard** | 100-row table without virtualization (manageable DOM) | 500-row table without virtualization (noticeable slowdown) | 5,000+ rows without virtualization, dashboard unusable |
| **SPA** | Minor route not code-split (extra 30KB in main bundle) | No code splitting at all, 1MB+ main bundle | Heavy libraries (charts, editors) in main bundle, 2MB+ initial JS |
| **Content/blog** | Article images below fold not lazy (small image sizes) | 30+ article images loading eagerly on long-form content | Embedded iframes (videos, widgets) loading eagerly, competing with content |
| **Mobile-first** | Slight over-rendering of below-fold content | 20+ images loading eagerly on mobile (bandwidth and battery cost) | No lazy loading or virtualization on data-heavy mobile pages |

**Severity multipliers:**
- **Data connection cost**: In markets where mobile data is expensive (most of the world), eagerly loading invisible content wastes users' money. This is an ethical consideration, not just a performance one.
- **Page depth**: Long pages (infinite scroll, content hubs, search results) benefit more from lazy loading. Short pages (landing pages, single-screen apps) benefit less.
- **Data volume**: Applications with large datasets (admin panels, analytics dashboards) have the most to gain from virtualization.

---

## §9 Build Bible integration

| Bible principle | Application to Lazy Loading and Virtualization |
|-----------------|--------------------------------------------------|
| **§1.4 Simplicity** | Don't render what the user can't see. This is simplicity applied to rendering — the simplest render is the one that only creates what's needed. |
| **§1.8 Prevent, don't recover** | Lazy loading PREVENTS wasted downloads. Loading everything and then trying to cancel or deprioritize is recovery. Load what you need, when you need it. |
| **§1.6 Config-driven** | Lazy loading thresholds, virtualization window sizes, and code-splitting boundaries should be configurable. Different pages and contexts need different settings. |
| **§1.9 Atomic operations** | Lazy-loaded components should render atomically — either the component is fully loaded and rendered, or a placeholder is shown. Partially rendered components are worse than no component. |
| **§6.7 God file** | A 10,000-row DOM table is the rendering equivalent of a god file. Virtualize it — the DOM should only contain what it's actively displaying. |
| **§1.14 Speed hides debt** | On a fast connection with a powerful device, loading 100 images and 5,000 DOM nodes feels fine. On a mobile device over 3G, it's a 30-second load with 200MB of memory. The debt is there; the fast path hides it. |
