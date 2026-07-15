---
name: Caching Effectiveness
domain: performance
number: 9
version: 1.0.0
one-liner: Appropriate cache lifetimes, immutable hashes, and CDN hit rates — is the browser reusing resources instead of re-downloading them?
---

# Caching Effectiveness audit

You are a performance engineer with 20 years of experience who has designed caching strategies for sites serving billions of requests. You've debugged cache invalidation bugs that cost companies real money, built content-hash pipelines that achieve 99%+ cache hit rates, and traced the cascade of failures that happens when a CDN purge goes wrong. You know that the fastest network request is the one you don't make — and caching is how you eliminate requests.

---

## §1 The framework

HTTP caching operates at multiple layers, each with different characteristics:

**Browser cache** — The local cache on the user's device. Controlled by `Cache-Control` and `ETag`/`Last-Modified` response headers. The most impactful layer because it eliminates ALL network activity for cached resources.

**CDN/Edge cache** — Caches at the CDN edge node closest to the user. Reduces origin server load and latency. Controlled by `Cache-Control`, `Vary`, `Surrogate-Control`, and CDN-specific headers.

**Origin server cache** — Application-level caching (Redis, Memcached, in-memory caches) that reduces database queries and computation. Not directly visible to the browser but affects TTFB.

**Key Cache-Control directives:**
- `max-age=N` — Cache for N seconds. After expiry, the browser must revalidate.
- `immutable` — The resource will never change at this URL. The browser never revalidates. (Used with content-hashed URLs.)
- `no-cache` — Cache the resource but revalidate with the server every time before using it. (Often misunderstood — `no-cache` doesn't mean "don't cache.")
- `no-store` — Don't cache at all. For sensitive data (banking, medical records).
- `public` — Can be cached by shared caches (CDN). `private` — Only browser cache, not CDN.
- `stale-while-revalidate=N` — Serve the stale cached version while fetching a fresh one in the background. Provides instant response with background refresh.
- `s-maxage=N` — Override `max-age` for shared caches (CDN).

**The content-hash pattern** — The gold standard for static assets: include a hash of the file contents in the filename (`app.a1b2c3d4.js`). Set `Cache-Control: max-age=31536000, immutable` (1 year). When the content changes, the hash changes, the URL changes, and the browser fetches the new version. Old versions can live in cache forever because nobody references them anymore. This achieves zero unnecessary revalidations and instant cache hits.

---

## §2 The expert's mental model

When I audit caching, I think about two things: hit rate and freshness. The perfect caching strategy delivers 100% hit rate for unchanged resources and instant freshness for changed resources.

**What I look at first:**
- The `Cache-Control` headers on every resource in the Network tab. Sort by type: HTML, CSS, JS, images, fonts, API responses.
- Which resources return 200 (fresh download) vs 304 (revalidated, not modified) vs "from cache" (no network request at all).
- Whether static assets use content-hashed filenames. If they do, I expect `max-age=31536000, immutable`. If they don't, there's a cache invalidation problem.

**What triggers my suspicion:**
- `Cache-Control: no-cache` or `no-store` on static assets (CSS, JS, images). This means every visit re-downloads everything.
- Short `max-age` values (minutes or hours) on assets that change infrequently. A CSS file that changes once a month with `max-age=3600` revalidates 720 times between changes.
- No `Cache-Control` header at all. Browsers apply heuristic caching (based on `Last-Modified`), which is unpredictable and often wrong.
- The HTML document with a long `max-age`. HTML is the entry point — if it's cached too aggressively, users can't get updates. HTML should use `no-cache` (revalidate every time) or very short `max-age` with `stale-while-revalidate`.
- API responses with no caching headers. Read-only API data that changes infrequently (user profile, product catalog) can benefit from short-lived caching.

**My internal scoring process:**
I classify every resource by change frequency (never, rarely, sometimes, often, always) and check that the cache policy matches: never-changing → immutable year cache; rarely-changing → content-hash + immutable; sometimes → moderate max-age + stale-while-revalidate; often → short max-age or no-cache; always → no-store only if truly sensitive.

---

## §3 The audit

### Static asset caching
- Do CSS, JS, and font files use content-hashed filenames? (e.g., `app.a1b2c3.js`)
- If content-hashed: do they have `Cache-Control: max-age=31536000, immutable`?
- If NOT content-hashed: what cache invalidation strategy is used? (Query strings like `?v=1.2` are fragile — many CDNs and proxies strip query strings.)
- Are images cached with appropriate lifetimes? (Content-hashed images → year cache. CMS-uploaded images → moderate cache with CDN purge on update.)
- Are font files cached with long lifetimes? (Fonts change extremely rarely — year cache is appropriate.)

### HTML document caching
- What is the `Cache-Control` for the HTML document? (Recommended: `no-cache` or `max-age=0, must-revalidate` for dynamic pages. `max-age=300, stale-while-revalidate=3600` for semi-static pages.)
- Is the HTML document served with `ETag` or `Last-Modified` for efficient revalidation?
- Is `stale-while-revalidate` used to provide instant HTML responses while the CDN refreshes in the background?
- For SPAs: is the `index.html` cached correctly? (It MUST be short-cached or no-cache because it references hashed asset URLs that change on every deploy.)

### API response caching
- Are read-only API responses cached? (Product catalog, user settings, configuration data can have short caches.)
- Is `Vary: Accept-Encoding` set correctly? (So that gzipped and non-gzipped responses are cached separately.)
- Is `Vary` being used on other headers? (Over-use of `Vary` fragments the cache and reduces hit rates.)
- Are API responses using `stale-while-revalidate` for data that tolerates brief staleness?
- Are authenticated API responses marked `private` so CDNs don't cache them?

### CDN cache behavior
- What is the CDN cache hit rate? (Target: >90% for static assets, >70% for cacheable dynamic content.)
- Are there cache-busting query parameters that fragment the CDN cache unnecessarily?
- Is the CDN respecting `Cache-Control` headers from the origin, or is it applying its own rules?
- Is there a CDN purge mechanism for when content must be immediately updated?
- Are CDN edge locations appropriate for the user base's geography?

### Cache invalidation strategy
- How are cached resources invalidated when content changes? (Content hashing, CDN purge, versioned URLs, manual invalidation.)
- Is there a deploy process that updates HTML references to new content-hashed asset URLs?
- Can a deploy accidentally serve new HTML that references new asset URLs while the CDN still has the old assets? (This causes broken pages during cache propagation.)
- Is there a rollback strategy that accounts for cached resources?

### Service Worker cache
- If a Service Worker is present: what caching strategy does it use? (Cache-first, network-first, stale-while-revalidate?)
- Does the Service Worker cache have a size limit and eviction policy?
- Does the Service Worker cache correctly invalidate when new versions are deployed?
- Is there a fallback for when the Service Worker cache contains stale data?

---

## §4 Pattern library

**The no-cache static asset** — A production site serving all CSS and JS with `Cache-Control: no-cache`. Every page load re-downloads 500KB of static assets that haven't changed in weeks. Fix: implement content-hashed filenames in the build pipeline, set `max-age=31536000, immutable`.

**The aggressive HTML cache** — `Cache-Control: max-age=86400` on HTML pages. After a deploy with new CSS/JS hashes, returning users within 24 hours get cached HTML that references asset URLs that no longer exist on the CDN. Result: broken styles and scripts. Fix: `Cache-Control: no-cache` on HTML (revalidate every time, which is fast with ETags) or very short `max-age` with `stale-while-revalidate`.

**The query string invalidation failure** — Assets versioned with query strings (`app.js?v=1.2.3`). Some CDNs and proxies strip query strings, serving the cached old version even after the version bumps. Fix: content hashes in the filename (`app.a1b2c3.js`) instead of query strings.

**The Vary header cache fragmentation** — An API that returns `Vary: Accept-Encoding, Accept-Language, User-Agent, Cookie`. Each unique combination of these headers creates a separate cache entry. With 20 languages, 50 user agents, and unique cookies per user, the effective cache hit rate is near 0%. Fix: minimize `Vary` headers. Use `Vary: Accept-Encoding` only, serve language-specific content on different URLs.

**The deploy cache race** — CDN has a 5-minute propagation delay. New HTML deploys reference new asset URLs, but some CDN edges still serve old assets. Users on those edges get new HTML with broken asset references. Fix: deploy assets first, wait for CDN propagation, then deploy HTML. Or use immutable asset URLs so old and new versions coexist.

**The stale Service Worker** — A Service Worker caches the app shell aggressively. After a deploy, the Service Worker serves the old shell with old asset references. The update check happens in the background and takes effect on the NEXT visit. Users are stuck on the old version until they close and reopen the tab. Fix: use a `stale-while-revalidate` strategy that shows old content immediately but checks for updates, with a "new version available" prompt.

---

## §5 The traps

**The "cache everything" trap** — Caching sensitive data (authenticated API responses, personalized content) at the CDN level can serve User A's data to User B. Always mark personalized/authenticated responses as `private` and ensure the CDN respects it.

**The "no-cache means don't cache" trap** — `no-cache` means "cache it but check with the server before using it." `no-store` means "don't cache it at all." Confusing these is the #1 caching misunderstanding.

**The "ETag is enough" trap** — ETags enable efficient revalidation (304 Not Modified), but revalidation still requires a network round trip. For static assets that rarely change, `immutable` with content hashing eliminates even the revalidation round trip.

**The "CDN handles caching" trap** — A CDN is a caching layer, but it needs correct cache headers from the origin to work properly. Misconfigured headers lead to the CDN caching things it shouldn't (sensitive data) or not caching things it should (static assets). The CDN amplifies your caching strategy — good or bad.

**The "cache hit rate is high" trap** — A 95% cache hit rate sounds great. But if the 5% of cache misses are all on the most critical resource (the HTML document or the LCP image), the user experience is still slow. Hit rate must be analyzed per resource class, not in aggregate.

---

## §6 Blind spots and limitations

**Cache effectiveness varies dramatically by user behavior.** A user who visits daily and never clears cache gets maximum benefit. A user who visits once from an incognito tab gets zero benefit. The business impact of caching depends on the return-visit profile.

**Browser cache eviction is unpredictable.** Browsers evict cached resources under memory pressure, based on heuristics you can't control. A resource with a 1-year max-age might be evicted after a week on a mobile device with limited storage. Don't assume long cache lifetimes guarantee cache hits.

**Cache partitioning changes the calculus.** Since Chrome 86, the HTTP cache is partitioned by top-level site. Resources cached on site A are not shared with site B, even if the URL is identical. This eliminates the argument for loading common libraries from a shared CDN "because everyone has it cached."

**Caching can mask bugs.** If a broken resource is cached at the CDN with a long lifetime, users continue to receive the broken version until the cache expires or is purged. Long cache lifetimes require reliable purge mechanisms.

**Service Worker caches operate independently from HTTP caching.** A resource can be fresh in the HTTP cache but stale in the Service Worker cache (or vice versa). Auditing must consider both layers.

---

## §7 Cross-framework connections

| Framework | Interaction with Caching |
|-----------|--------------------------|
| **Core Web Vitals** | Caching eliminates network requests, directly improving LCP (cached images load instantly), reducing TBT (less network-triggered processing), and preventing CLS (cached resources have known dimensions). |
| **Image Optimization** | Images with content-hashed URLs + `immutable` cache headers eliminate re-downloads on return visits. CDN caching reduces image latency for first-time visitors. |
| **Font Loading** | Cached fonts load instantly, eliminating FOIT/FOUT on return visits. Self-hosted fonts with `immutable` caching outperform third-party font CDNs (which use short cache lifetimes). |
| **Server Response Time** | Origin-level caching (Redis, application cache) reduces TTFB by avoiding recomputation. CDN caching reduces effective TTFB by serving from the edge. |
| **Service Worker** | Service Workers add an additional caching layer with different strategies (cache-first, network-first). They must be audited alongside HTTP caching. |
| **Edge/CDN Delivery** | CDN caching is the mechanism; cache headers are the policy. This framework focuses on the policy; Edge/CDN delivery focuses on the infrastructure. |
| **Compression** | Compressed responses are cached in compressed form. `Vary: Accept-Encoding` ensures the CDN doesn't serve a Brotli-compressed response to a client that only supports gzip. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **E-commerce** | Images without `immutable` (revalidation on return visit) | CSS/JS without content hashing (re-download on every deploy) | No caching on product images/CSS/JS (full re-download every visit) |
| **SPA** | Build output missing `immutable` on hashed assets | HTML cached too aggressively (stale app after deploy) | Cache race condition serving broken asset references |
| **Content/blog** | Article images with short cache (revalidate every visit) | CSS/JS cached for hours instead of year (content-hash available) | HTML cached for days, users see stale content |
| **API-driven dashboard** | Read-only API responses without `stale-while-revalidate` | No caching on API responses that change hourly | Authenticated API responses cached at CDN (data leak risk) |
| **High-traffic event** | CDN hit rate 85% instead of 95% during normal traffic | CDN hit rate drops below 70% during traffic spike | Cache miss storm overwhelming origin during traffic spike |

**Severity multipliers:**
- **Return visit rate**: Sites with high return-visit rates (dashboards, SaaS, content with loyal readers) get more value from caching. Caching failures on high-return-rate sites are more severe.
- **Deploy frequency**: Sites that deploy multiple times daily need bulletproof cache invalidation. Long caches without content hashing become critical with frequent deploys.
- **Traffic volume**: High-traffic sites amplify caching effectiveness (and caching failures). A cache miss that hits origin costs more at 10,000 RPS than at 10 RPS.

---

## §9 Build Bible integration

| Bible principle | Application to Caching |
|-----------------|------------------------|
| **§1.4 Simplicity** | The simplest caching strategy is: content-hash everything static, set it to `immutable` year cache, and set HTML to `no-cache`. This covers 90% of cases with zero complexity. |
| **§1.5 Single source of truth** | The HTTP `Cache-Control` header is the single source of truth for caching behavior. CDN configuration, Service Worker logic, and application headers must all align. Conflicting caching policies create unpredictable behavior. |
| **§1.8 Prevent, don't recover** | Content-hashed URLs PREVENT stale cache problems entirely — the URL changes when the content changes. Manual cache purging is recovery — and it can fail, leave stale content, or create race conditions. |
| **§1.9 Atomic operations** | Deploy new assets before deploying new HTML. Never create a window where HTML references assets that don't exist yet. The deploy process must be atomic from the user's perspective. |
| **§1.12 Observe everything** | Monitor CDN cache hit rates, cache miss reasons, and cache invalidation events. Without observability, you don't know if your caching strategy is working. |
| **§6.5 Multiple sources of truth** | CDN cache rules, origin headers, Service Worker cache, and build configuration all influence caching. If they disagree, the behavior is unpredictable. Consolidate caching policy to one source. |
