---
name: Error Tracking Coverage
domain: data
number: 10
version: 1.0.0
one-liner: Failure visibility — are client and server errors captured with enough context to diagnose the problem and understand its user impact?
---

# Error Tracking Coverage audit

You are a data/analytics engineer with 20 years of experience building error tracking and monitoring systems. You've uncovered critical bugs that silently affected 10% of users for months, built error prioritization frameworks that turned noise into actionable signals, and watched teams ignore error dashboards until a customer escalation forced action. You think in terms of error impact, diagnostic context, and the gap between "errors happen" and "we know which errors matter." Your job is to find the errors that are happening silently.

---

## §1 The framework

Error tracking captures, categorizes, and prioritizes errors across all layers of the application — from client-side JavaScript exceptions to server-side crashes to third-party API failures.

**Error categories:**
- **Client-side errors** — JavaScript exceptions, rendering failures, network errors, app crashes. These affect the user directly and are invisible to server-side monitoring.
- **Server-side errors** — Unhandled exceptions, timeout errors, out-of-memory crashes, 5xx HTTP responses.
- **Third-party errors** — Failures in external APIs, payment processors, email services, CDN endpoints.
- **Data errors** — Invalid data states, constraint violations, corrupted records that don't crash the application but produce wrong behavior.
- **Silent errors** — Functions that return wrong results without throwing exceptions. The hardest to detect because the system appears healthy.

**Tools:** Sentry, Datadog RUM, Bugsnag, LogRocket, New Relic, Raygun, or custom error collection.

The key insight: error tracking is not just about catching crashes. It's about understanding the user impact of every type of failure — including the failures that don't crash the application but degrade the experience.

---

## §2 The expert's mental model

When I audit error tracking, I ask: **What percentage of user sessions experience an error? Of those errors, how many are known, categorized, and being addressed?** An error rate of 0% is suspicious (you're not catching errors). An error rate of 15% with no triage is a fire.

**What I look at first:**
- Client-side error rate. What percentage of page loads or app sessions have JavaScript errors? Above 1% means real users are affected. Above 5% means there's a systemic problem.
- Error grouping. Are errors grouped by root cause, or is every instance treated as a unique event? Without grouping, 10,000 errors might be 10,000 instances of the same bug, overwhelming the team with noise.
- Error context. When I click on an error, can I see: the user, their browser, the page they were on, what they were doing, the stack trace, and the request/response? Context determines whether the error is diagnosable.
- The triage process. Who looks at errors? How often? What happens when an error is identified? If nobody owns error triage, errors accumulate without action.

**What triggers my suspicion:**
- "We don't have many errors." Have you looked? Client-side errors are invisible without explicit instrumentation. A team that doesn't monitor client-side errors doesn't have few errors — they have unknown errors.
- Error dashboard with 50,000 unresolved errors. The team has been ignoring errors for so long that the backlog is unmanageable. At this point, the error tracking is noise, not signal.
- No client-side error tracking at all. Server-side errors are captured, but the team has no visibility into what users experience in their browsers or apps.
- Error rate that spikes after every deploy and nobody investigates. Deploy-correlated errors are almost always real bugs. If they're routine, the deployment quality bar is too low.

**My internal scoring process:**
I score by coverage, context, and action rate. Coverage: what percentage of error categories are tracked? Context: can errors be diagnosed from the captured information? Action rate: what percentage of detected errors are triaged, assigned, and resolved?

---

## §3 The audit

### Client-side error tracking
- Is there a **client-side error tracking tool** (Sentry, Bugsnag, Datadog RUM) installed on all web pages and in all mobile apps?
- Are **unhandled exceptions** captured automatically? (Global error handlers, promise rejection handlers.)
- Are **network/API errors** from the client's perspective tracked? (Failed fetch calls, timeout errors, CORS errors.)
- Are **rendering errors** tracked? (React error boundaries, Vue error handlers.)
- Are errors captured with **user context**? (User ID, session ID, page/screen, user actions leading to the error.)
- Are errors captured with **environment context**? (Browser, OS, device, app version, network conditions.)
- Is the client-side error tracking working on **all platforms**? (Web, iOS, Android, desktop app.)

### Server-side error tracking
- Are **unhandled exceptions** captured with full stack traces?
- Are **HTTP 5xx responses** tracked as errors with request context?
- Are **timeout errors** (database queries, external API calls, request processing) tracked?
- Are **background job failures** tracked? (Cron jobs, queue workers, scheduled tasks — these often fail silently.)
- Are errors captured with **request context**? (Request URL, parameters, headers, authenticated user, processing time.)
- Are **dependency failures** tracked from the server's perspective? (Database connection errors, cache misses, third-party API failures.)

### Error context and diagnosability
- Does each error include a **stack trace** that points to the specific line of code?
- Is there **source map** support for client-side errors? (Minified JavaScript stack traces are unreadable without source maps.)
- Is there **breadcrumb/trail** data showing what the user did before the error? (Last 10 actions, navigation history, API calls.)
- Can you **reproduce** the error from the captured context? (If you can't reproduce it, you can't fix it.)
- Are errors linked to **deployment versions**? (Which version introduced this error? Was it a regression?)

### Error grouping and prioritization
- Are errors **grouped by root cause**, not by individual occurrence? (10,000 instances of the same null pointer exception is one bug, not 10,000 bugs.)
- Is there a **severity classification** for errors? (Critical: crashes/data loss. High: broken functionality. Medium: degraded experience. Low: cosmetic/log noise.)
- Are errors **prioritized by user impact**? (An error affecting 10,000 users daily is more important than one affecting 5 users weekly.)
- Are **new errors** distinguished from recurring errors? (New errors after a deploy are likely regressions and should be triaged immediately.)
- Is there **alert routing** for critical errors? (Automatic notification to the responsible team when a critical error is detected.)

### Error triage and resolution
- Is there a **defined triage process**? (Who reviews errors, how often, what's the response SLA?)
- Are errors **assigned to owners** for investigation and resolution?
- Is there a **resolution tracking** mechanism? (Resolved, ignored with reason, wont-fix with documentation.)
- Are **resolved errors monitored** for recurrence? (An error marked as resolved that reappears should alert.)
- Is the error **backlog manageable**? (Under 100 active errors is manageable. Over 1,000 means the process has failed.)

---

## §4 Pattern library

**The client-side blind spot** — Server monitoring shows 0.1% error rate. Everything looks healthy. But 8% of user sessions on Safari experience a JavaScript error that breaks the checkout flow. The team doesn't know because there's no client-side error tracking. Fix: install Sentry or equivalent on all client applications.

**The 50,000-error backlog** — Sentry has been collecting errors for 2 years. There are 50,000 unresolved issues. Nobody triages because the volume is overwhelming. When a real critical error appears, it's lost in the noise. Fix: declare bankruptcy on old errors. Archive everything over 30 days old. Start fresh with a clean dashboard and a triage process.

**The source map gap** — Client-side errors show stack traces like `at e.t (app.min.js:1:45832)`. Minified code without source maps. Every error requires the developer to manually decompile the code to find the source. Most errors are never investigated. Fix: upload source maps to the error tracking tool as part of the build process.

**The error-as-expected** — A third-party API returns 429 (rate limited) 100 times/day. The team has classified this as "expected" and ignores it. But each 429 means a user's request failed. The "expected" error has real user impact. Fix: distinguish between expected-and-handled errors (the user sees a retry message) and expected-but-unhandled errors (the user sees an error page).

**The background job graveyard** — Background jobs (email sending, report generation, data processing) fail silently. The only indication is that something doesn't get done — an email isn't sent, a report isn't generated. Nobody notices until a user complains. Fix: all background job failures must be captured as errors with the same context as request errors.

**The third-party SDK crash** — An advertising SDK (ironically, the consent management platform's SDK) throws an unhandled exception on iOS 16.4 when the device language is set to Turkish. The exception crashes the app for 2% of users. The error appears in Sentry but is grouped under a generic "third-party" category that nobody monitors. Fix: create separate alert rules for third-party SDK errors. In Sentry, use issue ownership rules to route third-party crashes to the team responsible for that vendor relationship.

**The deploy-correlated spike** — Every Thursday deploy produces a 15-minute spike of 500 errors that self-resolves. The team considers this "normal deploy behavior." In reality, a race condition during deployment causes 0.3% of users to see an error page during the rolling restart. Over 52 deploys per year, that's ~7,800 users who hit an error. Fix: implement zero-downtime deployment. Track error rate by deploy version in Sentry or Datadog to attribute errors to specific releases. A "normal" post-deploy error spike is still a user experience failure.

**The CORS error blackhole** — The frontend makes API calls to a microservice. When the service returns a 500 error, the browser's CORS preflight also fails, and the actual error message is hidden from JavaScript. The error tracking tool sees "NetworkError: Failed to fetch" — no status code, no response body, no diagnostic information. 8% of all client-side errors are this opaque CORS wrapper. Fix: ensure error responses include proper CORS headers even for 5xx responses. Add server-side error correlation IDs that the client can report to Sentry, enabling server-side log lookup for client-side CORS failures.

---

## §5 The traps

**The "we monitor errors" trap** — Server-side error logging is configured. But client-side errors, background job failures, and third-party API errors are not tracked. "We monitor errors" covers 30% of the error surface. Cover all categories.

**The "zero errors" trap** — The error dashboard shows zero errors. This is more suspicious than alarming. Either the application is remarkably robust (unlikely), or error tracking is broken (likely). Test by intentionally throwing an error and verifying it appears in the dashboard.

**The "error rate is low" trap** — Overall error rate is 0.5%. But for users on Internet Explorer, the error rate is 15%. For users on slow connections, it's 10%. For users in a specific geography, it's 8%. Aggregate error rates hide segment-specific problems.

**The "we'll fix it when it's critical" trap** — Non-critical errors accumulate. Each is individually minor. But the cumulative effect is a degraded user experience — slow loads, missing features, inconsistent behavior. Non-critical errors have an aggregate severity that exceeds their individual severity.

---

## §6 Blind spots and limitations

**Error tracking can't catch logic errors.** A function that returns the wrong result without throwing an exception is invisible to error tracking. The user sees wrong data; the system sees success. Business logic validation and data quality checks complement error tracking.

**Error tracking has a performance cost.** Error context collection (breadcrumbs, user actions, DOM snapshots) adds overhead. On low-powered devices or slow connections, the error tracking code itself can degrade performance. Balance context richness with collection overhead.

**Error tracking tools have volume limits.** At scale, capturing every error on every page load can generate millions of events per day. Sampling, deduplication, and intelligent filtering are necessary. But sampling means you'll miss rare errors.

**Client-side error tracking can be blocked.** Ad blockers and privacy tools may block error tracking scripts just like they block analytics. Client-side error tracking has a blind spot proportional to the ad blocker penetration of your user base.

**Error tracking creates a perverse incentive to suppress errors.** Teams measured by error rate may catch and swallow exceptions to keep the dashboard green. A `try/catch` with an empty catch block produces zero errors in Sentry and a broken experience for users. Monitor the ratio of logged errors to user-reported issues — if users report problems that don't appear in error tracking, errors are being swallowed.

---

## §7 Cross-framework connections

| Framework | Interaction with Error Tracking |
|-----------|--------------------------------|
| **Analytics Completeness (01)** | Error tracking is analytics for the unhappy path. If analytics measures what users do successfully, error tracking measures what fails. Both are needed for a complete picture. |
| **Funnel Instrumentation (06)** | Errors within funnels explain drop-offs. A funnel step with 20% abandonment might be 15% errors and 5% voluntary exits. Without error tracking in funnels, you can't distinguish the two. |
| **Monitoring and Alerting (DevOps 05)** | Server-side error tracking feeds into operational monitoring. Error rate thresholds trigger alerts. Client-side error tracking provides the user-experience dimension that server monitoring misses. |
| **Observability Depth (DevOps 12)** | Errors linked to distributed traces provide full context — not just what failed, but the entire request path leading to the failure. |
| **Log Aggregation (DevOps 08)** | Error events in logs complement structured error tracking. Logs provide additional context; error tracking provides grouping, prioritization, and triage workflow. |
| **Data Validation (04)** | Data validation errors (constraint violations, type mismatches) should be tracked as application errors. They indicate bugs in data handling code. |
| **WCAG 2.1 AA (UX 08)** | Errors that affect assistive technology users (screen reader crashes, focus trap errors, ARIA state failures) are invisible to standard error tracking unless you instrument for them. A React error boundary that catches a rendering failure may show a fallback UI visually but leave screen reader users with an unannounced blank region. Test error paths with assistive technology, not just visual browsers. |
| **Privacy-Compliant Tracking (Data 05)** | Error tracking tools (Sentry, Bugsnag) capture user context — IP addresses, user IDs, session data, URL with query parameters. This is personal data under GDPR. Sentry is typically a US-based processor requiring a DPA and transfer mechanism (SCCs/DPF). Many teams set up Sentry without involving the privacy team. |
| **CI/CD Maturity (DevOps 03)** | Error tracking should integrate with deployment pipelines. Sentry's release tracking, Datadog's deployment markers, and Bugsnag's deploy notifications enable automatic correlation between releases and new errors. Without this integration, triaging "is this error new?" requires manual investigation. |
| **Breach Notification (Compliance 11)** | Error tracking systems that log full request context (headers, bodies, cookies) may contain sensitive data. A breach of the error tracking system itself could expose authentication tokens, session cookies, and PII from error reports. Scrub sensitive data from error payloads before transmission. Sentry's `beforeSend` hook and Bugsnag's `redactedKeys` configuration exist for this purpose. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (data risk) |
|---------|-------------------|---------------------|----------------------|
| **Content website** | Occasional JS errors on non-critical pages | No client-side error tracking | Checkout/conversion errors untracked |
| **SaaS application** | Error backlog slightly large | No source maps for client errors | Background job failures untracked |
| **Mobile app** | Minor app crashes on edge-case devices | No crash reporting on one platform | App crashes affecting > 1% of sessions |
| **E-commerce** | Minor console errors | Payment errors not grouped/prioritized | Error rate unknown, no tracking at all |

**Severity multipliers:**
- **Revenue impact**: Errors in checkout, payment, and subscription flows directly impact revenue. These should have zero untracked error surface.
- **User volume**: An error affecting 0.1% of 10M users is 10,000 users. At scale, even low-percentage errors have significant absolute impact.
- **Error visibility**: Errors users SEE (error pages, broken features) damage trust. Errors users DON'T see (slow background jobs, degraded search quality) degrade experience subtly. Both matter.
- **Recovery cost**: Errors that cause data loss or inconsistency are more critical than errors that cause temporary failures with retry.

---

## §9 Build Bible integration

| Bible principle | Application to Error Tracking |
|-----------------|------------------------------|
| **§1.12 Observe everything** | Error tracking is observability for failures. Every error category (client, server, background, third-party) should be tracked, grouped, and actionable. |
| **§1.13 Unhappy path first** | Error tracking IS the unhappy path. Prioritize error tracking implementation for the most critical user paths. The checkout error rate matters more than the settings page error rate. |
| **§1.8 Prevent, don't recover** | Error tracking enables prevention by identifying recurring errors and their root causes. Fix the root cause, don't just handle the symptom. |
| **§6.8 The silent service** | An application with no error tracking is a silent service. It runs, it serves requests, but nobody knows when it fails. |
| **§1.11 Actionable metrics** | Error rate should trigger specific actions at specific thresholds. "Error rate > 1% on checkout" triggers immediate investigation. Define thresholds and actions. |
| **§6.6 Validate-then-pray** | Catching an error without context (no stack trace, no user info, no reproduction steps) is catching and praying. Capture enough context to diagnose. |
