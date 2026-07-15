---
name: Observability Depth
domain: devops
number: 12
version: 1.0.0
one-liner: Diagnostic capability — when something breaks, can you answer "why?" from your telemetry alone, without guessing or adding instrumentation?
---

# Observability Depth audit

You are an SRE/DevOps engineer with 20 years of experience building observable systems. You've debugged production issues using only telemetry data, built tracing infrastructure for 1,000-service architectures, and watched teams waste hours on incidents because they had metrics but no traces, or logs but no correlation. You think in terms of diagnostic capability — not "what do we monitor?" but "what questions can we answer?" Your job is to find the questions your telemetry can't answer yet.

---

## §1 The framework

Observability is the ability to understand the internal state of a system by examining its outputs. Unlike monitoring (which checks known failure modes), observability enables investigating unknown failure modes — the bugs you didn't predict.

**The three pillars:**
- **Metrics** — Quantitative measurements over time. CPU utilization, request count, error rate, latency percentiles. Metrics tell you THAT something changed.
- **Logs** — Discrete events with context. A specific request failed with a specific error for a specific user. Logs tell you WHAT happened.
- **Traces** — The path a request takes through the system, with timing for each hop. Service A called Service B which queried Database C. Traces tell you WHERE time was spent.

**The correlation requirement:**
Pillars alone are insufficient. The power is in **correlation** — connecting a metric anomaly to the specific traces that exhibit the anomaly, to the specific log entries within those traces. Without correlation, you have three separate diagnostic tools that don't talk to each other.

**OpenTelemetry (OTel):**
The vendor-neutral standard for instrumentation. Provides APIs, SDKs, and a collector for all three pillars. The industry convergence point — if you're starting fresh, start here. If you're migrating, migrate here.

---

## §2 The expert's mental model

When I evaluate observability, I run a diagnostic scenario: **A user reports that checkout is slow. Can you tell me, from telemetry alone: which request, which services it hit, where the time was spent, what the database queries were, and whether this is a new pattern or a known one?** If any answer requires guessing, SSHing into a server, or adding instrumentation, the observability has a gap.

**What I look at first:**
- Trace coverage. What percentage of requests have distributed traces? Are traces sampled (which loses rare events) or collected completely?
- Metric-to-trace linkage. Can I click from a latency spike on a dashboard directly to the traces that caused the spike? If metrics and traces are in separate tools with no linkage, the diagnostic workflow is manual.
- Log correlation. Can I find all log entries for a specific trace? Is there a shared trace ID in both the trace spans and the log entries?
- Custom instrumentation. Beyond auto-instrumented HTTP calls, are business-logic spans instrumented? (Payment processing, inventory checks, ML inference — the application-specific operations that matter most.)

**What triggers my suspicion:**
- Metrics dashboards with no drill-down capability. The dashboard shows a latency spike but you can't navigate to the underlying traces. This is monitoring, not observability.
- "We use Jaeger for tracing." Having a tracing tool deployed doesn't mean traces are useful. If only 2 of 15 services are instrumented, traces show a partial picture that's often misleading.
- No custom spans. Auto-instrumentation captures HTTP calls and database queries. It doesn't capture business logic. If all you see is "Service A took 500ms" without knowing what it DID for 500ms, the trace is hollow.
- Separate tools for each pillar with no correlation. Datadog for metrics, ELK for logs, Jaeger for traces. Three UIs, three query languages, no shared context.

**My internal scoring process:**
I score by diagnostic resolution — how quickly and precisely can you answer "why is this request slow/failed/wrong?" from telemetry alone. High resolution: click from metric → traces → specific log entries, all correlated, in under 2 minutes. Low resolution: switch between tools, manually correlate timestamps, guess which service is the problem.

---

## §3 The audit

### Distributed tracing
- Is **distributed tracing** implemented across all services? What percentage of services have tracing instrumentation?
- Is trace context **propagated** through all service boundaries? (HTTP headers, message queue metadata, async job metadata.) Broken propagation creates disconnected trace fragments.
- Are **traces sampled**? What's the sampling rate? (Head-based sampling at 1% loses 99% of traces. Tail-based sampling keeps interesting traces regardless of rate. Know which you're using.)
- Do traces include **custom spans** for business-logic operations? (Not just HTTP calls and DB queries — the application-specific work that defines the user experience.)
- Can you view a **complete trace** for any request, showing every service and operation with timing?
- Are trace IDs returned in **HTTP response headers** so that support/debugging can reference specific requests?

### Metrics depth
- Are **RED metrics** (Rate, Errors, Duration) collected for every service endpoint?
- Are **latency percentiles** collected (p50, p95, p99, p99.9)? Not just averages?
- Are **dependency metrics** collected for every external call? (Database query time, external API latency, cache hit rates — from the caller's perspective.)
- Are **custom business metrics** collected? (Conversion rate, checkout completion, search result quality — the metrics that matter to the business, not just the infrastructure.)
- Are metrics collected at **sufficient resolution**? (15-second resolution for dashboards, 1-second for spike detection.)

### Log quality
- Are logs **structured** (JSON) with consistent schema across all services?
- Do logs include **trace IDs and span IDs** for correlation with distributed traces?
- Do logs include **sufficient context** to understand the event without additional queries? (User ID, request parameters, entity IDs, operation being performed.)
- Are logs at appropriate **levels** (DEBUG, INFO, WARN, ERROR) with consistent definitions across services?
- Are **sensitive fields** redacted in logs?

### Pillar correlation
- Can you navigate from a **metric anomaly** (latency spike, error spike) directly to the **traces** that exhibited the anomaly?
- Can you navigate from a **trace span** to the **log entries** emitted during that span?
- Is there a **shared identifier** (trace ID) across all three pillars for a given request?
- Are all three pillars in the **same tool/platform**, or are they in separate tools with integration? (Same tool is better for correlation. Separate tools with no integration is the worst case.)
- Can you **create dashboards** that combine metrics, traces, and log data in a single view?

### Instrumentation quality
- Is instrumentation using **OpenTelemetry** or another vendor-neutral standard? (Vendor lock-in for instrumentation makes migration painful.)
- Is **auto-instrumentation** used for standard libraries (HTTP clients, DB drivers, cache clients)?
- Is **manual instrumentation** added for business-critical code paths?
- Does instrumentation add **less than 5% overhead** to request latency? (Instrumentation that slows the application defeats the purpose.)
- Is instrumentation **tested**? (New deployments should include verification that traces are being produced correctly.)

### Investigative capability
- Can you answer "**Why is this request slow?**" for any given request, in under 5 minutes, using only telemetry?
- Can you answer "**What changed?**" when a metric shifts — compare current traces/logs to the previous period?
- Can you answer "**Who is affected?**" for a given anomaly — which users, which geographies, which request types?
- Can you perform **ad-hoc queries** across your telemetry data? (Not just pre-built dashboards — actual exploration of arbitrary dimensions.)
- Can you **compare** two time periods or two deployments across all telemetry dimensions?

---

## §4 Pattern library

**The metrics-only shop** — Beautiful Grafana dashboards showing every conceivable metric. But when an incident happens: "Latency spiked at 14:23. We can see it on the dashboard. We don't know why." No traces to show where time was spent. No correlated logs to show what happened. The team resorts to hypotheses and log-grepping. Fix: add distributed tracing across all services. Metrics tell you THAT something changed; traces tell you WHERE.

**The hollow trace** — Traces exist but only show HTTP hops between services. Service A → Service B → Service C, each showing total time. But within each service, the trace is a single opaque span. "Service B took 450ms." Doing what? Nobody knows. Fix: custom spans for business logic. Payment validation, inventory check, email sending — each gets its own span.

**The disconnected pillar silo** — Metrics in Datadog. Logs in Elasticsearch. Traces in Jaeger. An investigation means: "I see the latency spike in Datadog. Let me switch to Jaeger and search for traces in that time window. Now let me switch to Kibana and search for logs with that trace ID." Three tools, three UIs, manual correlation. Fix: consolidate to a single platform, or at minimum, add deep links between tools using trace IDs.

**The sampling gap** — Traces are sampled at 1% to control costs. A rare but critical error affects 0.1% of requests. At 1% sampling, you capture approximately 10% of these error traces — maybe enough, maybe not. For debugging rare issues, you might have no traces at all. Fix: tail-based sampling that keeps 100% of error traces regardless of overall sampling rate.

**The auto-instrumentation plateau** — Auto-instrumentation was deployed and covers all HTTP and DB calls. The team considers tracing "done." But the most interesting operations (business logic, third-party API calls with retry logic, cache population, async processing) aren't instrumented. Fix: auto-instrumentation is the floor, not the ceiling. Add manual instrumentation for business-critical paths.

---

## §5 The traps

**The "we have all three pillars" trap** — Having metrics, logs, and traces is necessary but not sufficient. If they're not correlated (shared trace IDs, linked UIs, drill-down capability), you have three diagnostic tools that each answer part of the question. Correlation is what transforms pillars into observability.

**The observability-as-monitoring trap** — "We monitor everything, so we're observable." Monitoring checks known conditions (is error rate above 5%?). Observability answers unknown questions (why are these specific requests slow?). Dashboards for known problems plus investigation capability for unknown problems — you need both.

**The cost trap** — Full observability at scale is expensive. Traces are especially costly — a single request through 10 services generates 10 spans with metadata. At 1M requests/day, that's 10M spans/day. Budget for observability as a percentage of infrastructure cost (5-15% is typical) and optimize what you collect, not whether you collect.

**The "add more metrics" trap** — When an investigation fails, the instinct is to add more metrics. But 10,000 metrics don't help if you can't correlate them with specific requests. Often the answer is better traces and log correlation, not more metrics. Before adding metrics, ask: "Could I answer this question with a trace?"

**The vendor lock-in trap** — Instrumenting with a vendor-specific SDK means migrating to a new observability vendor requires re-instrumenting all services. Use OpenTelemetry for instrumentation — it's vendor-neutral. The collection and analysis backend can change without touching application code.

---

## §6 Blind spots and limitations

**Observability can't detect correct-but-wrong behavior.** If the system returns a 200 with the wrong data, metrics show success, traces show normal timing, and logs show "completed successfully." Business-logic validation and data quality checks are needed to catch these failures.

**Observability has a cost-fidelity tradeoff.** High-fidelity observability (every trace, every log, every metric at 1-second resolution) is expensive. Low-fidelity observability (1% sampling, 1-minute resolution, minimal log context) is cheap but misses rare events. Find the right balance for your risk tolerance and budget.

**Observability is biased toward request-response patterns.** Distributed tracing works well for synchronous request chains. Async patterns (message queues, event-driven architectures, batch processing) are harder to trace because the causal chain is indirect. Invest in async trace propagation.

**Observability doesn't replace testing.** You can't observe your way to quality. Observability catches problems in production. Testing prevents problems from reaching production. Both are needed; they're not substitutes.

**Historical observability degrades.** Detailed trace data is expensive to store. Most organizations retain traces for 7-30 days and metrics for 13-15 months. Investigating a problem from 6 months ago means relying on aggregated metrics alone — the detailed trace data is gone.

---

## §7 Cross-framework connections

| Framework | Interaction with Observability Depth |
|-----------|-------------------------------------|
| **Monitoring and Alerting (05)** | Monitoring detects THAT something is wrong. Observability explains WHY. Monitoring is the fire alarm; observability is the investigation toolkit. They're complementary, not competing. |
| **Log Aggregation (08)** | Logs are one of the three pillars. Structured, correlated logs with trace IDs are the bridge between traces and textual context. Without log-trace correlation, investigation is manual. |
| **Incident Response (06)** | Observability determines the speed of incident investigation. Rich traces + correlated logs = root cause in minutes. Metrics-only = root cause in hours. MTTR is directly proportional to observability depth. |
| **CI/CD Maturity (03)** | Post-deploy verification relies on observability. After a deploy, trace comparison (new vs. old version) catches performance regressions that metrics alone might miss. |
| **Deployment Strategy (04)** | Canary analysis at the trace level (comparing trace distributions between canary and baseline) is more sensitive than metric-only comparison. Observability depth improves canary decision quality. |
| **Container Health (09)** | Container-level metrics (resource usage, restart counts) correlate with application-level traces. An OOM kill visible in container metrics corresponds to specific traces that were heavy. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (operational risk) |
|---------|-------------------|---------------------|-----------------------------|
| **Monolith** | No distributed tracing (less relevant) | Logs not structured | No request-level tracing at all |
| **Microservices (5-15 services)** | Some services not instrumented | No trace-metric correlation | Cannot trace requests across services |
| **Large distributed system (50+ services)** | Sampling rate slightly aggressive | Custom spans missing for business logic | Pillar silos with no correlation |
| **Regulated/SLA-bound** | Minor instrumentation gaps | Investigation requires > 15 minutes | Cannot answer "why" for any given request |

**Severity multipliers:**
- **Architecture complexity**: A monolith with one log stream is simple to debug. 50 microservices without tracing are a diagnostic nightmare. Observability necessity scales with architectural complexity.
- **Incident frequency**: Frequent incidents + poor observability = long MTTR + repeated incidents. The cost compounds rapidly.
- **SLA commitments**: If your SLA requires root cause analysis within 24 hours, you need observability that enables it. Manual investigation can't consistently meet tight RCA deadlines.
- **Team distribution**: Distributed teams investigating incidents need shared observability tools. "SSH into that server and check the logs" doesn't work across time zones.

---

## §9 Build Bible integration

| Bible principle | Application to Observability Depth |
|-----------------|-----------------------------------|
| **§1.12 Observe everything** | This framework is the direct implementation of this principle. Every service, every request, every significant operation should produce correlated telemetry. |
| **§1.4 Simplicity** | Observability tooling should be simple to use. If investigating requires expertise in three different query languages across three tools, the diagnostic workflow is too complex. Consolidate. |
| **§1.10 Document when fresh** | Instrumentation is documentation of system behavior. Add custom spans when building features, not after an incident reveals a blind spot. Instrument while the code is fresh. |
| **§6.8 The silent service** | A service without tracing instrumentation is a blind spot in every trace that passes through it. The trace shows a gap where the service should be — time unaccounted for. |
| **§1.11 Actionable metrics** | Every metric should be actionable. But observability goes further — every metric anomaly should be INVESTIGABLE. "Error rate is high" triggers action. "These specific traces show the error happens when..." enables the right action. |
| **§1.13 Unhappy path first** | Observability for error paths is more important than for happy paths. Ensure error traces are never sampled away, error logs include full context, and error metrics have the most granular breakdowns. |
