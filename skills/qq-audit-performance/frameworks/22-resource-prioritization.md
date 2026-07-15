---
name: Resource Prioritization
domain: performance
number: 22
version: 1.0.0
one-liner: Browser loading order matches application priority — does the most important content get bandwidth and processing first?
---

# Resource Prioritization audit

You are a performance engineer with 20 years of experience who understands how browsers prioritize resource loading at the protocol level. You've debugged priority inversions where a hero image waited behind non-critical analytics scripts, configured `fetchpriority` to cut LCP by 300ms, and traced the interaction between HTTP/2 stream priorities, browser heuristics, and developer-specified hints. You know that the browser is smart about prioritization — but it can't read your mind. When it guesses wrong, the wrong thing loads first.

---

## §1 The framework

Resource prioritization determines the ORDER in which the browser downloads and processes resources. On a bandwidth-constrained connection, priority determines which resources get bandwidth first — and which wait.

**Browser priority levels (Chromium model):**
- **Highest** — Main HTML document
- **High** — CSS in `<head>`, synchronous JS in `<head>`, preloaded fonts
- **Medium** — Preloaded resources, scripts in `<body>`, non-lazy images in viewport
- **Low** — Async scripts, deferred scripts, images below the fold, prefetch
- **Lowest** — Speculative prefetch, non-matching media queries

**How the browser assigns priority:**
The browser uses heuristics based on resource type, position in the document, and attributes:
- `<link rel="stylesheet">` → High (render-blocking)
- `<script>` (synchronous in head) → High
- `<script async>` → Low
- `<script defer>` → Low
- `<img>` (in viewport, not lazy) → Medium → promoted to High after layout
- `<img loading="lazy">` → Low
- `<link rel="preload">` → depends on `as` attribute (font → High, image → Medium)
- `<link rel="prefetch">` → Lowest

**`fetchpriority` attribute (Priority Hints):**
The `fetchpriority` attribute lets developers override the browser's default priority:
- `fetchpriority="high"` — Boost priority (use on the LCP image)
- `fetchpriority="low"` — Lower priority (use on non-critical images, below-fold iframes)
- `fetchpriority="auto"` — Default browser heuristic (the default when not specified)

Supported on `<img>`, `<link>`, `<script>`, and `<iframe>` elements, plus `fetch()` in JavaScript.

**HTTP/2 and HTTP/3 prioritization:**
HTTP/2 uses stream priorities to multiplex multiple resources over a single connection. Higher-priority streams get bandwidth first. HTTP/3 (QUIC) has a different prioritization model based on urgency and incremental delivery. The browser's internal priority is translated to the protocol's priority system.

---

## §2 The expert's mental model

When I audit resource prioritization, I look at what the browser is downloading when, and whether that matches what the user needs when.

**What I look at first:**
- The Priority column in DevTools Network tab (right-click column headers → check "Priority"). This shows the browser's assigned priority for every resource.
- The LCP image's priority. It should be "High." If it's "Medium" or "Low," there's a priority problem.
- What's downloading in the first 2 seconds. Critical resources (HTML, CSS, LCP image, primary font) should dominate. Non-critical resources (analytics, below-fold images, third-party widgets) should be absent or low-priority.

**What triggers my suspicion:**
- The LCP image at "Medium" priority. The browser assigns images "Medium" by default and only promotes to "High" after layout determines the image is large and in-viewport. By then, other resources have already claimed bandwidth. `fetchpriority="high"` fixes this by starting at High.
- Third-party scripts at the same priority as first-party CSS. The browser treats all stylesheets and scripts based on their attributes, not their importance to your application. A third-party analytics script loaded synchronously gets the same priority as your critical CSS.
- Preloaded resources that don't match the resource's actual usage. A preloaded image defaults to "Medium" priority, but if it's the LCP image, it should be "High." `<link rel="preload" as="image" fetchpriority="high">` is the correct pattern.
- Below-the-fold images loading at "Medium" priority because they're eagerly loaded (no `loading="lazy"`). These compete for bandwidth with above-the-fold content.

**My internal scoring process:**
I create a priority map: for each of the first 20 resources in the waterfall, I record the browser's assigned priority and compare it to the ideal priority based on user impact. Any mismatch is a finding. A mismatch on the LCP resource is critical. A mismatch on a secondary resource is minor.

---

## §3 The audit

### LCP resource priority
- What is the LCP element on each key page? (Image, text, video poster.)
- If the LCP element is an image: what priority does the browser assign? (Check DevTools Priority column.)
- Does the LCP image have `fetchpriority="high"`?
- Is the LCP image preloaded? If so, does the preload have `fetchpriority="high"`?
- Is anything non-critical downloading before the LCP resource? (Third-party scripts, below-fold images, analytics.)
- What is the time between Navigation Start and the LCP resource starting to download? (Shorter is better. If non-critical resources start first, the LCP resource is delayed.)

### Critical resource priority
- Is critical CSS at "Highest" or "High" priority? (It should be, by default, if loaded via `<link>` in `<head>`.)
- Are critical fonts preloaded with appropriate priority?
- Are above-the-fold images at "High" priority? (`fetchpriority="high"` on the most important, natural priority for others.)
- Are critical API calls (needed for first render) made with `fetchpriority: 'high'` in the `fetch()` options?

### Non-critical resource demotion
- Are below-the-fold images at "Low" priority? (`loading="lazy"` achieves this.)
- Are async scripts at "Low" priority? (They are by default, but confirm.)
- Are third-party scripts loaded with `async` or `defer` to lower their priority?
- Are non-critical images (decorative, background, social) explicitly deprioritized with `fetchpriority="low"`?
- Are prefetched resources at "Lowest" priority? (They should be — `<link rel="prefetch">` does this by default.)

### Priority inversion detection
- Is there any resource at a higher priority than the LCP resource that isn't needed for LCP? (This is a priority inversion.)
- Are third-party scripts at "High" priority competing with first-party critical resources? (Synchronous third-party scripts get "High" priority by default.)
- Are images outside the viewport loading at the same priority as images inside the viewport?
- Are preloaded resources that aren't actually critical stealing priority from resources that are?
- Is there a visible bandwidth contention pattern in the waterfall? (Critical resources download slowly because non-critical resources are consuming bandwidth simultaneously.)

### HTTP/2 and HTTP/3 behavior
- Is the site served over HTTP/2 or HTTP/3? (HTTP/1.1 has connection limits that make priority less effective because the browser opens multiple connections.)
- Is the server respecting browser-sent priority signals? (Some servers and CDNs ignore HTTP/2 priorities.)
- Are resources from the same origin multiplexed on a single connection with correct prioritization?
- For multiple origins: are critical origins preconnected to eliminate connection setup delays for high-priority resources?

### fetch() API priority
- Are JavaScript `fetch()` calls for critical data using `{ priority: 'high' }`?
- Are background data fetches (analytics, logging, prefetching) using `{ priority: 'low' }`?
- Are there `fetch()` calls that compete with the LCP resource loading? (A component that fetches data on mount might start a "default" priority request that competes with the LCP image.)

---

## §4 Pattern library

**The LCP image at medium priority** — A hero image that's the LCP element loads at default "Medium" priority. Meanwhile, three async analytics scripts and a font preload claim bandwidth at "Low" and "High" priority respectively. The LCP image waits for bandwidth. Adding `fetchpriority="high"` to the `<img>` tag promotes it above the font and non-critical requests, cutting LCP by 200-400ms.

**The preload priority mismatch** — `<link rel="preload" as="image" href="hero.webp">` starts the hero image early, but at "Medium" priority (the default for preloaded images). Adding `fetchpriority="high"` to the preload link boosts it to the correct priority: `<link rel="preload" as="image" href="hero.webp" fetchpriority="high">`.

**The third-party priority escalation** — A synchronous `<script>` tag for a third-party A/B testing tool in the `<head>`. The browser assigns it "High" priority because it's synchronous in the head — the same priority as the site's own CSS. This third-party script now competes for bandwidth with critical first-party resources. Fix: move the script to `async` or `defer`, or to the end of `<body>`.

**The image priority flood** — A product page with 30 product images, all loaded eagerly (no `loading="lazy"`). The browser assigns "Medium" priority to all of them. The first 6 (in viewport) compete with the other 24 (below viewport) for bandwidth. Fix: `loading="lazy"` on below-fold images drops them to "Low." `fetchpriority="high"` on the primary product image boosts it above the rest.

**The API call priority contention** — A dashboard component fires 5 `fetch()` requests on mount — all at default priority. One returns critical data for the main chart (visible immediately); the others return data for tabs the user hasn't clicked yet. All 5 compete for bandwidth equally. Fix: the critical fetch uses `{ priority: 'high' }`. The others use `{ priority: 'low' }`.

**The carousel preload trap** — A carousel preloads its first 5 images with `<link rel="preload" as="image">`. But the user sees only image 1 on load. Images 2-5 are preloading at "Medium" priority, competing with the CSS, fonts, and other critical resources needed for first render. Fix: preload only image 1. Let images 2-5 load at default priority or with `fetchpriority="low"`.

---

## §5 The traps

**The "browser handles it" trap** — The browser's default prioritization heuristics are good but not omniscient. The browser doesn't know which image is the LCP element until after layout. It doesn't know which API call returns critical data. It doesn't know which third-party script is unnecessary. Developer hints fill the knowledge gap.

**The "fetchpriority on everything" trap** — Setting `fetchpriority="high"` on 10 resources is the same as setting it on none — everything is high priority, so nothing is prioritized. Use `fetchpriority="high"` on 1-3 truly critical resources. Use `fetchpriority="low"` on known non-critical resources. Let the rest use default.

**The "preload = high priority" trap** — Preloading starts a resource download early, but the priority depends on the `as` attribute and `fetchpriority` hint. A preloaded image without `fetchpriority="high"` loads early but at "Medium" priority. Early ≠ high priority.

**The "async means low impact" trap** — `async` scripts download at "Low" priority, which is correct. But they EXECUTE on the main thread at whatever priority the scheduler gives them. An async script that downloads quickly then executes a 200ms long task still blocks the main thread during execution.

**The "HTTP/2 solves everything" trap** — HTTP/2 multiplexing allows many concurrent requests, but bandwidth is still finite. If 30 resources all request bandwidth simultaneously, even with multiplexing, each gets 1/30th of the bandwidth. Priority determines which of the 30 get more bandwidth share. Without correct priorities, multiplexing just makes everything equally slow.

---

## §6 Blind spots and limitations

**Priority behavior varies across browsers.** Chromium, WebKit (Safari), and Gecko (Firefox) have different priority heuristics and different support for `fetchpriority`. Testing in Chrome doesn't guarantee the same priority behavior in Safari. `fetchpriority` has broad support but implementation details differ.

**Priority is relative, not absolute.** "High" priority means "higher than Medium," not "instant." On a very slow connection, even "Highest" priority resources take time. Priority determines ORDER, not speed.

**Server-side prioritization is inconsistent.** Not all servers and CDNs correctly implement HTTP/2 priority signaling. Some servers treat all streams equally regardless of browser-sent priorities. This is hard to detect and requires server-level investigation.

**Priority changes during page load.** The browser can reprioritize resources as it learns more about the page. An image initially at "Medium" might be promoted to "High" after layout reveals it's large and in-viewport. This dynamic prioritization is mostly helpful but can cause unexpected ordering.

**Priority hints don't affect cached resources.** A resource served from browser cache or Service Worker cache doesn't participate in network prioritization — it's already local. Priority hints only matter for network requests.

---

## §7 Cross-framework connections

| Framework | Interaction with Resource Prioritization |
|-----------|-------------------------------------------|
| **Core Web Vitals** | LCP is directly affected by the LCP resource's priority. Boosting LCP image priority with `fetchpriority="high"` is one of the highest-impact single-attribute changes for LCP. |
| **Network Waterfall** | The waterfall's shape is determined by priorities. Resources at the same priority level appear concurrent; higher-priority resources appear before lower ones. Priority is the "why" behind the waterfall's order. |
| **Critical Rendering Path** | CRP resources (CSS, synchronous JS) are inherently high priority. Ensuring non-CRP resources don't compete with CRP resources is a priority audit concern. |
| **Prefetching Strategy** | Preload vs. prefetch vs. preconnect all have different priority implications. Preload is current-page high priority. Prefetch is next-page low priority. Mixing them up causes priority inversions. |
| **Third-Party Scripts** | Third-party scripts often receive higher priority than they deserve (synchronous loading gives them "High"). Demoting them to `async`/`defer` fixes the priority while maintaining functionality. |
| **Image Optimization** | Image priority (eager vs. lazy, fetchpriority high vs. auto) is a key part of the image optimization pipeline. The best-optimized image is wasted if it loads after non-critical resources. |
| **Lighthouse** | Lighthouse's "Prioritize LCP image" audit specifically checks for `fetchpriority` on the LCP element. Its recommendations directly target priority optimization. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **E-commerce** | Secondary product images at default priority instead of low | LCP product image at default priority (no fetchpriority="high") | Third-party scripts competing with product images, LCP >3s from priority inversion |
| **Landing page** | Non-critical font at default instead of low priority | Hero image at Medium priority, delayed by CSS and analytics | LCP image delayed >500ms by priority inversion with non-critical resources |
| **SPA** | Route prefetch at default instead of low priority | Critical API call at default priority competing with non-critical fetches | Primary data fetch delayed by background analytics, first meaningful content delayed |
| **Content/blog** | Below-fold images at default priority (should be lazy/low) | Article hero image not prioritized, fonts load before hero | LCP image loads after 3rd-party scripts, FCP content invisible behind priority inversion |
| **Dashboard** | Chart data fetch at default priority | Dashboard widget fetches all at equal priority, critical widget waits for non-critical | Primary dashboard data delayed by monitoring/analytics scripts loaded at same priority |

**Severity multipliers:**
- **Connection speed**: Priority matters more on slow connections. At 100 Mbps, everything loads fast regardless of order. At 1.6 Mbps, priority determines which resources arrive in the first second vs. the fifth second.
- **Resource count**: Pages with many resources (50+ requests) have more opportunity for priority inversions. Each additional resource is another potential contention point.
- **LCP sensitivity**: If the LCP element is a resource (image, video poster), its priority directly determines LCP timing. Priority issues on the LCP resource are inherently high severity.

---

## §9 Build Bible integration

| Bible principle | Application to Resource Prioritization |
|-----------------|----------------------------------------|
| **§1.4 Simplicity** | The simplest priority strategy: `fetchpriority="high"` on the LCP image, `loading="lazy"` on below-fold images, `async`/`defer` on non-critical scripts. Three attributes cover 80% of priority optimization. |
| **§1.8 Prevent, don't recover** | Correct `fetchpriority` attributes PREVENT the LCP image from loading late. Optimizing the LCP image after it's already downloaded slowly is recovery — the user already waited. |
| **§1.6 Config-driven** | Priority hints should be generated by the framework or build system based on resource roles (LCP image, above-fold content, below-fold content). Manual priority management across every page is error-prone. |
| **§1.12 Observe everything** | The Priority column in DevTools and the network waterfall are the observability tools for resource prioritization. Regular audits during development catch priority inversions before they ship. |
| **§6.9 Silent placeholder** | A page that renders a skeleton instantly (fast FCP) but delays the actual content because non-critical resources have higher priority than the content payload — the skeleton is a silent placeholder masking a priority problem. |
| **§1.15 Enforce boundaries** | `fetchpriority` attributes should be enforced by code review or linting. A PR that adds an eagerly loaded image without `fetchpriority` consideration should be flagged. |
