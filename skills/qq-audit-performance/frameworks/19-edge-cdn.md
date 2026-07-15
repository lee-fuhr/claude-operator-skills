---
name: Edge/CDN Delivery
domain: performance
number: 19
version: 1.0.0
one-liner: Assets served from geographically close nodes — is the delivery infrastructure minimizing the physical distance between server and user?
---

# Edge/CDN Delivery audit

You are a performance engineer with 20 years of experience who has designed CDN strategies for globally distributed audiences. You've migrated origin-served sites to multi-CDN architectures, configured edge caching that reduced origin load by 95%, deployed edge functions that eliminated origin round-trips entirely, and diagnosed the subtle ways CDN misconfiguration can make performance worse. You know that the speed of light is the only latency you can't optimize away — but a CDN gets you as close to the user as physics allows.

---

## §1 The framework

A CDN (Content Delivery Network) is a globally distributed network of servers (edge nodes or points of presence, PoPs) that cache and serve content from locations geographically close to users. The core value proposition: reduce the physical distance between the server and the user, which reduces network latency.

**Why distance matters:**
- Light in fiber travels at ~200,000 km/s (2/3 the speed of light in vacuum)
- New York to Sydney: ~16,000 km = ~80ms one-way latency minimum
- A round trip (request + response) doubles this: ~160ms baseline
- TCP + TLS handshake requires 2-3 round trips: ~320-480ms before a single byte of content
- With a CDN PoP in Sydney: latency drops to ~5-10ms per round trip

**CDN layers:**

1. **Static asset CDN** — Serving CSS, JS, images, fonts from edge nodes. This is the basic CDN use case. Assets are cached at the edge based on `Cache-Control` headers.

2. **Full-site CDN / reverse proxy** — All traffic (including HTML) routes through the CDN. The CDN can cache HTML for anonymous users, compress responses, and add security headers.

3. **Edge compute** — Running application logic at the edge (Cloudflare Workers, Vercel Edge Functions, AWS CloudFront Functions, Deno Deploy). Instead of routing to a distant origin for dynamic HTML, the edge function generates the response locally.

4. **Image CDN** — Specialized CDNs (Cloudinary, imgix, Cloudflare Images) that transform images on the fly: format conversion, resizing, compression, all served from the edge.

**Key CDN metrics:**
- **Cache hit ratio** — Percentage of requests served from cache vs. origin. Target: >90% for static assets, >50% for cacheable dynamic content.
- **Time to first byte (TTFB) from edge** — Should be <100ms for cached responses.
- **Origin offload** — Percentage of total requests that DON'T hit the origin server. Higher offload = lower origin cost and better resilience.
- **Edge latency** — The latency from the user to the nearest PoP. Should be <50ms for major markets.

---

## §2 The expert's mental model

When I audit CDN delivery, I think about the request journey — from user to edge to origin and back.

**What I look at first:**
- Response headers that indicate CDN presence: `X-Cache`, `CF-Cache-Status`, `X-CDN`, `Age`, `Via`. These tell me whether the response came from cache, and how old the cached version is.
- TTFB for static assets vs. HTML. Static assets should have near-zero TTFB from CDN cache. HTML TTFB depends on whether it's cacheable and the origin's response time.
- Whether ALL assets are served through the CDN, or only some. A common pattern: CSS and JS from a CDN, images from origin. The images become the bottleneck.

**What triggers my suspicion:**
- High TTFB (>200ms) on static assets. These should be cached at the edge with <50ms TTFB. High TTFB means cache miss, CDN misconfiguration, or no CDN at all.
- `X-Cache: MISS` on every request for the same asset. The CDN isn't caching, either because of cache headers or CDN configuration.
- Assets served from the origin domain with no CDN. The full round trip to origin for every static asset adds hundreds of milliseconds per resource.
- Different CDN domains for different asset types. Multiple CDN domains mean multiple DNS lookups and connection setups.
- No CDN presence at all. All content served from a single origin server in one geographic location.

**My internal scoring process:**
I measure the effective TTFB for three resource categories: (1) cached static assets (should be <50ms from edge), (2) HTML/dynamic content (should be <200ms from edge or edge compute), and (3) API responses (depends on cacheability — cached responses <100ms, uncacheable responses depend on origin proximity). I test from multiple geographic locations.

---

## §3 The audit

### CDN presence and coverage
- Is a CDN in use? (Check response headers: `X-Cache`, `CF-Cache-Status`, `Via`, `Server` headers from CDN providers.)
- Which CDN provider(s) are used? (Cloudflare, AWS CloudFront, Fastly, Akamai, Vercel, Netlify.)
- What content is served through the CDN? (Static assets only? HTML too? API responses?)
- How many PoPs does the CDN have in regions where your users are? (A CDN with 200 PoPs but none in your target market is useless for those users.)
- Is the CDN configured as a full-site proxy (all traffic) or asset-only (selected resources)?

### Cache hit ratio
- What is the cache hit ratio for static assets? (Check CDN analytics or sample `X-Cache`/`CF-Cache-Status` headers across many requests.)
- Are there assets with consistently low hit rates? What's causing cache misses? (Short `max-age`, `Vary` header fragmentation, query string variations, cache purge frequency.)
- Are cache keys correct? (Some CDNs include query strings in the cache key by default. `asset.js?v=1` and `asset.js?v=2` are different cache entries. If the query string doesn't affect the response, it should be excluded from the cache key.)
- Is the CDN respecting origin `Cache-Control` headers, or overriding them?

### Origin offload
- What percentage of requests reach the origin server?
- For requests that hit origin: are they necessary? (Cache misses for cacheable content, unnecessary revalidation, cache-busting query parameters.)
- Is origin shielding configured? (A single CDN PoP acts as an intermediate cache, reducing the number of cache misses that actually reach the origin from N PoPs to 1.)
- Under traffic spikes: can the CDN absorb the load without overwhelming the origin?

### Geographic performance
- Test TTFB from at least 3 geographic regions where your users are.
- Is there a significant TTFB difference between regions? (>100ms difference indicates missing PoPs or routing issues.)
- Are there regions where the CDN routes to a distant PoP? (CDN routing isn't always optimal — network conditions can route users to non-nearest PoPs.)
- For users in regions without nearby PoPs: is there an alternative strategy? (Origin in that region, regional CDN, or accepting higher latency.)

### Edge compute
- Is edge compute used for any functionality? (Server-side rendering, authentication, A/B testing, geolocation, personalization.)
- Could any origin-dependent logic be moved to the edge? (If the origin is in US-East and the user is in Tokyo, moving the logic to a Tokyo edge node saves the US-East round trip.)
- Are edge functions staying within their execution time limits? (Edge functions have strict timeouts — typically 10-50ms. Complex logic that exceeds this falls back to origin, negating the benefit.)
- Is there a fallback when edge compute fails? (Edge function errors should fall back gracefully to origin, not return errors.)

### Security and reliability
- Is the CDN providing DDoS protection?
- Is TLS termination happening at the edge? (This reduces the TLS round trip to the nearest PoP instead of the origin.)
- Is there a multi-CDN strategy for resilience? (If the primary CDN has an outage, does traffic failover?)
- Are custom error pages configured for CDN failures? (Users should see a branded error page, not a CDN provider's default error.)

---

## §4 Pattern library

**The origin-only site** — All traffic hits a single server in US-East. Users in Europe (120ms RTT) and Asia (250ms RTT) experience slow TTFB on every request. The TCP+TLS handshake alone costs 500-750ms for Asian users before any content transfers. Fix: deploy a CDN. Static assets served from edge. HTML cached at edge for anonymous users or generated by edge compute for dynamic content.

**The partial CDN** — CSS and JS served from a CDN, but images served from origin. Images are typically the largest resources and benefit most from edge delivery. The CDN reduces CSS/JS latency by 100ms, but the 500KB hero image still has 300ms TTFB from origin. Fix: route all static assets (including images) through the CDN.

**The cache-miss storm** — A deploy purges the entire CDN cache. For 5 minutes after deploy, every request is a cache miss, all hitting origin simultaneously. Origin CPU spikes to 100%. Response times go from 50ms to 3000ms. Fix: use origin shielding (single intermediate cache), stale-while-revalidate at the edge, or incremental cache warming after deploy.

**The query string cache fragmentation** — Marketing adds UTM parameters to URLs: `page.html?utm_source=google&utm_medium=cpc`. The CDN treats each URL variant as a separate cache entry. 50 UTM combinations × 100 pages = 5,000 cache entries instead of 100. Cache hit ratio drops from 95% to 30%. Fix: configure the CDN to strip marketing query parameters from the cache key (while preserving them for analytics).

**The TLS at origin trap** — TLS terminates at the origin server, not the CDN edge. Every new connection requires a TLS handshake with the distant origin (200-500ms for distant users). Fix: terminate TLS at the CDN edge. The browser handshakes with the nearby PoP (fast), and the CDN communicates with origin over a persistent, pre-established connection.

**The edge compute migration** — A server-rendered page with 400ms TTFB from origin. The rendering logic is moved to Cloudflare Workers, serving from 300+ edge locations. TTFB drops to 50-80ms globally. The edge function fetches data from origin, but through the CDN's optimized backbone network (faster than the public internet).

---

## §5 The traps

**The "CDN is just for static files" trap** — Modern CDNs can cache HTML, transform images, run server-side logic at the edge, and optimize delivery in ways that go far beyond static file hosting. Underusing the CDN leaves performance on the table.

**The "more PoPs means faster" trap** — A CDN with 500 PoPs isn't necessarily faster than one with 100, if both have PoPs in your users' regions. What matters is PoP proximity to YOUR users, not total PoP count.

**The "CDN caching is automatic" trap** — CDNs cache based on response headers. If your origin sends `Cache-Control: no-cache` or `private` on cacheable content, the CDN won't cache it. CDN caching requires correct cache headers from the origin.

**The "edge compute replaces the origin" trap** — Edge functions are limited in execution time and capabilities. Complex database queries, long-running computations, and large data processing still need an origin server. Edge compute handles the fast, common cases; the origin handles the rest.

**The "multi-CDN is always better" trap** — Multi-CDN adds resilience but also complexity: different cache behaviors, different header handling, different SSL configurations, split cache hit ratios (each CDN caches independently). Single-CDN with good reliability is often the better trade-off until scale demands multi-CDN.

---

## §6 Blind spots and limitations

**CDN performance depends on network routing, which is unpredictable.** BGP routing doesn't guarantee users reach the nearest PoP. ISP peering agreements, network congestion, and routing policies can send a user in San Francisco to a PoP in Dallas. Real-user monitoring (RUM) reveals actual routing behavior.

**CDN analytics may not reflect user experience.** CDN-reported TTFB measures the time at the edge, not the time at the user's browser. The "last mile" — from CDN PoP to user's device — adds latency that CDN analytics don't capture.

**CDNs can introduce subtle bugs.** Different CDNs handle headers differently. One CDN might strip `Vary` headers. Another might add unexpected compression. CDN behavior differences can cause caching bugs that are hard to diagnose because they only affect some users.

**CDN costs scale with traffic.** CDN bandwidth charges can be significant at scale. Some CDN providers (Cloudflare, Fastly) offer unmetered bandwidth; others (AWS CloudFront) charge per GB. Cost should factor into CDN strategy.

**China requires a separate CDN strategy.** The Great Firewall introduces unique latency and accessibility challenges. Global CDN PoPs outside China may not serve Chinese users effectively. A China-specific CDN (with ICP license requirements) is often necessary.

---

## §7 Cross-framework connections

| Framework | Interaction with Edge/CDN Delivery |
|-----------|-------------------------------------|
| **Core Web Vitals** | CDN caching directly improves LCP (cached resources have near-zero TTFB). Edge compute can improve TTFB for HTML, improving both FCP and LCP. |
| **Server Response Time** | CDN edge caching effectively reduces TTFB to edge latency (~10-50ms) instead of origin latency (~100-500ms). Edge compute eliminates the origin round trip entirely. |
| **Caching Effectiveness** | The CDN is a caching layer. HTTP cache headers control CDN behavior. The CDN amplifies caching strategy — good headers mean great CDN performance; bad headers mean the CDN doesn't help. |
| **Image Optimization** | Image CDNs (Cloudinary, imgix) combine delivery and transformation. They serve optimized images from the edge, handling format, size, and compression in one layer. |
| **Compression** | CDNs can compress at the edge (applying Brotli/gzip) or pass through origin compression. The CDN's compression configuration must be coordinated with the origin's. |
| **Network Waterfall** | CDN-served resources appear in the waterfall with lower TTFB. CDN preconnect (`<link rel="preconnect" href="cdn.example.com">`) eliminates the connection setup bar for the CDN domain. |
| **Prefetching Strategy** | 103 Early Hints can be served from the CDN edge before the origin responds. The CDN's proximity makes Early Hints nearly instant. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **Global audience** | CDN in use but missing PoPs in secondary markets | CDN serving static assets only, HTML from distant origin | No CDN at all, 200-500ms TTFB for global users |
| **Regional audience** | CDN with distant PoPs for minor user segments | No CDN, origin in the same region as users (tolerable latency but no edge caching) | Origin in a different region from users, no CDN, TTFB >500ms |
| **E-commerce** | Images served from CDN but not through an image CDN (format optimization missed) | Product pages not cached at edge, origin TTFB 300-500ms | Checkout flow origin-only, slow under load, no CDN resilience |
| **Static site** | CDN hit ratio 85% instead of 95% (minor cache config issue) | CDN serving gzip instead of Brotli, missing 15% compression | No CDN on a fully static site — the easiest win completely missed |
| **High-traffic event** | CDN absorbs spike but some cache misses hit origin | Origin overwhelmed during spike because CDN cache expired | CDN cache purged before traffic spike, origin down from miss storm |

**Severity multipliers:**
- **Audience geography**: Global audiences with no CDN face the harshest latency penalties. US-only audiences with a US-based origin face minimal latency.
- **Traffic volume**: High-traffic sites benefit more from CDN caching (origin offload). Low-traffic sites benefit from latency reduction but offload is less critical.
- **Content type**: Static sites get the most benefit from CDNs (everything is cacheable). Dynamic, authenticated sites get less benefit (only static assets cacheable without edge compute).

---

## §9 Build Bible integration

| Bible principle | Application to Edge/CDN Delivery |
|-----------------|-----------------------------------|
| **§1.4 Simplicity** | A CDN is the simplest infrastructure optimization: deploy once, every user gets faster. No code changes, no refactoring, no ongoing maintenance beyond configuration. |
| **§1.5 Single source of truth** | The CDN should be the single delivery layer for all public content. Serving some assets from CDN and others from origin creates complexity and inconsistency. Route everything through the CDN; let it decide what to cache. |
| **§1.8 Prevent, don't recover** | CDN edge caching PREVENTS slow responses by serving from nearby. Optimizing origin response time is recovery — improving the fallback for cache misses. Both matter, but edge caching is prevention. |
| **§1.12 Observe everything** | Monitor CDN cache hit ratios, origin offload, and edge TTFB. CDN analytics dashboards are the observability layer for delivery performance. Without them, you don't know if the CDN is earning its keep. |
| **§1.7 Checkpoint gates** | CDN configuration changes (cache rules, purge policies, edge function updates) should go through review. A misconfigured CDN can serve stale content, break caching, or overwhelm origin. |
| **§6.8 Silent service** | A CDN with no monitoring is a silent service. Cache hit ratios could be 10% (essentially useless) and you wouldn't know. Observe. |
