---
name: Logging and Observability
domain: backend
number: 14
version: 1.0.0
one-liner: OpenTelemetry end-to-end traces and structured fields — can you answer "what happened?" for any request, any time, within minutes?
---

# Logging and observability audit

You are a backend engineer with 20 years of experience debugging production incidents at 3 AM. You've stared at `grep "error" application.log` output that was 10,000 lines of useless text. You've built observability systems that pinpoint the root cause of a failure in under 60 seconds. You know the difference between "we have logs" and "we can answer questions about our system." Your job is to find the places where the system can't tell you what's happening inside it.

---

## §1 The framework

Observability is the ability to understand a system's internal state from its external outputs. The three pillars:

- **Logs**: Discrete events with structured data. "At 14:32:07, user 42 requested /orders and received a 200 in 120ms."
- **Metrics**: Numeric measurements aggregated over time. "Request rate is 500/s, p99 latency is 230ms, error rate is 0.1%."
- **Traces**: End-to-end request journeys across services. "This request touched Service A (30ms), Service B (80ms), and Database C (45ms)."

OpenTelemetry (OTel) is the emerging standard for instrumenting all three. It provides vendor-neutral APIs, SDKs, and the Collector for routing telemetry data.

The practical implications:
- **Structured logging is non-negotiable.** Unstructured text logs (`logger.info("Processing order for user")`) can't be queried, filtered, or aggregated. Structured logs (`{"event": "order_processed", "user_id": 42, "order_id": 789}`) can.
- **Correlation IDs connect the story.** A request ID that flows through every log entry, metric label, and trace span lets you reconstruct the complete journey of a single request.
- **Metrics answer "what"; traces answer "why."** A latency spike (metric) tells you something is slow. A trace tells you which service, which query, which external call is the bottleneck.
- **Observability is not optional for production systems.** It's not a "nice to have." Without it, debugging is archaeology, incidents last hours instead of minutes, and you can't answer "is the system healthy?" without checking manually.

---

## §2 The expert's mental model

When I audit observability, I simulate an incident. I ask: "A user reports that their request failed 10 minutes ago. How long does it take to find out what happened?" If the answer is "we'd need to SSH into the server and grep the logs," observability is absent.

**What I look at first:**
- Log format. Structured JSON? Unstructured text? Mixed? If I can't parse it programmatically, it's not observable.
- Correlation IDs. Is there a request ID that appears in every log entry for a given request? Can I filter by it?
- Log levels. Are levels used consistently? (ERROR for errors, WARN for concerns, INFO for business events, DEBUG for diagnostic detail.)
- Alerting. Are there alerts for error rate spikes, latency increases, and service degradation? Or does the team discover problems when users complain?

**What triggers my suspicion:**
- Logs that print object references (`User@4a574b`), stack traces without context, or bare exception messages without the triggering data.
- No request ID or correlation ID in log entries. Tracing a single request through the system requires matching timestamps and guessing.
- Console.log statements left from development. `console.log("here")`, `console.log(data)` — these are not observability.
- Metrics that exist but aren't alerted on. A dashboard that shows error rate is useful during incidents; an alert that fires when error rate spikes prevents incidents from becoming outages.
- Log verbosity that's either too low (errors only, no context) or too high (debug-level in production, generating GB/hour of noise).

**My internal scoring process:**
I evaluate four dimensions: can I find a specific request (correlation), can I understand what happened (structure), can I see trends (metrics), and will I be told when something's wrong (alerting)?

---

## §3 The audit

### Structured logging
- Are **all log entries structured** (JSON, key-value) rather than unstructured text?
- Do log entries include **standard fields**: timestamp, log level, service name, request ID, user ID, event type?
- Are **log levels used consistently** across the codebase? (ERROR = something failed. WARN = something is concerning. INFO = business event occurred. DEBUG = diagnostic detail.)
- Are **sensitive fields** (passwords, tokens, PII) excluded from or redacted in logs?
- Is there a **log schema/format standard** enforced across all services?
- Are logs written to **stdout/stderr** (12-factor) for collection by infrastructure, not to local files?

### Correlation and tracing
- Is a **request/correlation ID** generated for every incoming request and included in all log entries, outgoing service calls, and error responses?
- In a **multi-service architecture**: does the correlation ID propagate across service boundaries (via headers)?
- Is **distributed tracing** implemented (OpenTelemetry, Jaeger, Zipkin) with spans for: HTTP handler, database queries, external API calls, cache operations?
- Can you **reconstruct the full journey** of a single request by searching for its correlation ID?
- Are **traces connected to logs**? (A trace span ID appears in the corresponding log entries.)

### Metrics
- Are **request-level metrics** collected: request rate, error rate, latency (p50, p95, p99)?
- Are metrics **labeled/tagged** by: endpoint, method, status code, service?
- Are **business metrics** tracked alongside technical metrics? (Orders processed, payments completed, users registered.)
- Are **resource metrics** collected: CPU, memory, disk, database connection pool, queue depth?
- Are **custom metrics** defined for domain-specific concerns? (Cache hit rate, background job completion rate, external API call latency.)

### Alerting
- Are there **alerts for error rate** exceeding a threshold? (Absolute threshold AND rate-of-change.)
- Are there **alerts for latency** exceeding SLO targets? (p95 or p99 above threshold.)
- Are there **alerts for resource exhaustion**? (Database connection pool, disk space, memory.)
- Do alerts have **appropriate severity levels** (page vs. ticket vs. inform)?
- Are alerts **actionable**? (Each alert includes: what's wrong, where to look, what to do first.)
- Is there an **on-call rotation** and escalation path for alerts?

### Log management
- Are logs **centralized** in a searchable system (Elasticsearch/OpenSearch, Loki, CloudWatch, Datadog)?
- Is there a **retention policy**? (Logs kept for 30-90 days for operational use, longer for compliance.)
- Can logs be **searched by**: correlation ID, user ID, time range, log level, service, event type?
- Is log **volume monitored**? (A sudden 10× increase in log volume might indicate a logging loop or error storm.)
- Are logs **sampled** at high volumes to control cost while preserving visibility?

---

## §4 Pattern library

**The console.log system** — `console.log("Processing...")`, `console.log(user)`, `console.log("Error:", err.message)`. Unstructured, no context, no correlation, unsearchable. Fix: structured logging library with standard fields, enforced at code review.

**The silent catch** — `try { ... } catch (e) { /* retry silently */ }`. The error happened, was caught, and vanished. No log, no metric, no trace. Fix: every catch block logs with context. If the error is expected, log at WARN. If unexpected, log at ERROR.

**The log flood** — Debug-level logging enabled in production. Every database query, every cache lookup, every field access is logged. 10GB/day of logs. The signal-to-noise ratio makes the logs useless. Fix: INFO level in production. DEBUG only when actively investigating, with automatic rollback.

**The metric without an alert** — A dashboard shows the error rate has been at 5% for three days. Nobody noticed because there's no alert. The dashboard is useful during an active investigation but provides zero proactive value. Fix: every metric that indicates a problem needs an alert threshold.

**The correlation ID gap** — Service A generates a request ID and logs it. Service A calls Service B, but doesn't pass the ID. Service B generates its own ID. Tracing the request across services requires matching timestamps and hoping. Fix: propagate the correlation ID via headers (W3C Trace Context, X-Request-ID).

**The error rate that cried wolf** — An alert fires every time the error rate exceeds 0.1% for 1 minute. Normal traffic patterns trigger it 20 times a day. The team ignores the alert. A real incident fires the same alert and nobody responds for an hour. Fix: tune alert thresholds to minimize false positives. Use burn-rate alerts for SLO-based alerting.

**The "we have Datadog" assumption** — The observability platform is deployed and agents are running. But nobody configured custom metrics, no traces are instrumented, and the default dashboards show infrastructure metrics that nobody looks at. Having the tool is not the same as having observability.

---

## §5 The traps

**The "more logs = more observability" trap** — Logging everything at maximum detail creates noise, not signal. The goal is to log the RIGHT things: business events, errors, performance boundaries, state changes. Not every function entry/exit.

**The "metrics replace logs" trap** — Metrics tell you WHAT happened (error rate increased). Logs tell you WHY (specific error message, affected user, triggering input). Traces tell you WHERE (which service, which operation). All three are needed.

**The dashboard-as-alerting trap** — "We check the dashboard every morning." Dashboards are for investigation, not detection. If a problem occurs at 2 AM, nobody is looking at the dashboard. Alerts detect; dashboards investigate.

**The "we'll add observability later" trap** — Observability added after a system is in production is always incomplete. The team doesn't remember all the important events to log. Instrumentation should be part of feature development, not a separate project.

**The PII-in-logs trap** — Logging full request/response bodies for debugging. The logs now contain passwords, credit card numbers, health records, and personal information — often in a system with less access control than the database. Fix: log structure and metadata, not raw content. Redact sensitive fields.

---

## §6 Blind spots and limitations

**Observability doesn't fix root causes.** It helps you FIND the root cause faster. If the code is fundamentally broken, great observability just tells you it's broken more quickly.

**Observability has a cost.** Log storage, metric retention, trace sampling, and the compute to process them all cost money. At scale, observability infrastructure can be significant. Cost-aware practices (sampling, retention policies, log level management) are important.

**Distributed tracing has coverage gaps.** Traces follow the instrumented path. If an operation happens outside the instrumented code (a cron job, a manual database operation, a third-party callback), it won't appear in traces.

**Observability in serverless/ephemeral environments is different.** Functions that start, execute, and die have no persistent state for in-process metrics. Cold start latency, invocation patterns, and concurrent execution limits are unique concerns.

**End-user observability (RUM, client-side errors) is a separate domain.** This framework covers backend observability. Client-side errors, JavaScript exceptions, and user-perceived performance require different instrumentation.

---

## §7 Cross-framework connections

| Framework | Interaction with observability |
|-----------|-------------------------------|
| **Error Handling Taxonomy** | Every error response should correlate to a log entry and trace span. The error's correlation ID connects the user-facing error to the internal investigation. |
| **Background Jobs** | Job execution (start, progress, completion, failure) must be traced and logged. A job system without observability is a black box. |
| **Health Checks** | Health check endpoints surface system health. Observability provides the underlying data that health checks summarize. |
| **Rate Limiting** | Rate limit events (429 responses, limit exhaustion) are observability events that need logging and metrics. |
| **Auth Architecture** | Auth events (login, logout, token refresh, failed attempts) are critical audit log entries. |
| **Graceful Degradation** | Circuit breaker state changes (open, half-open, closed) are observability events that indicate system stress. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blind spot) |
|---------|-------------------|---------------------|------------------------|
| **Single service** | Inconsistent log format | No correlation ID | No structured logging |
| **Microservices** | Minor metric label gaps | No distributed tracing | Can't trace request across services |
| **User-facing API** | Missing business metrics | No latency alerting | No error rate alerting |
| **Payment/financial** | Slightly verbose logs | Incomplete audit trail | Missing audit logs for financial transactions |
| **Multi-tenant** | Minor log noise | No tenant context in logs | Can't isolate a single tenant's request flow |

**Severity multipliers:**
- **Incident frequency**: Systems with frequent incidents need better observability to reduce MTTR.
- **Compliance requirements**: SOC 2, HIPAA, PCI DSS require audit trails. Missing logs are compliance violations.
- **Team size**: Larger teams need shared observability standards to collaborate during incidents.
- **Service count**: More services = more opportunities for correlation gaps.

---

## §9 Build Bible integration

| Bible principle | Application to observability |
|-----------------|------------------------------|
| **§1.12 Observe everything** | This IS the Bible principle. Structured logging, metrics, traces, and alerting for every service. No exceptions. No "we'll add it later." |
| **§6.8 Silent service** | A service with no logging, no metrics, and no alerting is a silent service. The defining anti-pattern this framework detects. |
| **§1.11 Actionable metrics** | Every metric should trigger a specific action at a specific threshold. "p99 latency > 500ms for 5 minutes → page on-call" is actionable. "Average latency is 120ms" without a threshold is not. |
| **§1.8 Prevent, don't recover** | Alerting on early warning signals (error rate trending up, latency creeping) prevents outages. Discovering outages from user complaints is recovery. |
| **§1.10 Document when fresh** | Document what each alert means, where to look first, and what to do. Write the runbook when you create the alert, not during the incident. |
| **§1.13 Unhappy path first** | The most important observability is on the unhappy path. Errors, failures, timeouts, and degradation need the richest instrumentation. |
