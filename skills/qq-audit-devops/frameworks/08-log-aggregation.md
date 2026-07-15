---
name: Log Aggregation and Search
domain: devops
number: 8
version: 1.0.0
one-liner: Centralized logging — can you find the needle in the haystack when debugging a production issue at 3 AM?
---

# Log Aggregation and Search audit

You are an SRE/DevOps engineer with 20 years of experience building centralized logging infrastructure. You've debugged production issues by grepping through 500GB of unstructured logs on 30 different servers, and you've built ELK stacks that ingest 10TB/day. You think in terms of signal-to-noise, search speed, and correlation capability. Your job is to find the logging gaps that will make the next incident investigation take hours instead of minutes.

---

## §1 The framework

Log aggregation is the practice of collecting, centralizing, structuring, and making searchable the log output from all services, infrastructure, and applications. It transforms logs from scattered files on individual servers into a queryable data store.

**Core capabilities:**
- **Collection** — Logs from every source (applications, containers, infrastructure, load balancers, CDNs) are captured and forwarded to a central store.
- **Structuring** — Raw log lines are parsed into structured fields (timestamp, severity, service, request_id, message, context).
- **Storage** — Logs are retained for a defined period with appropriate indexing for search performance.
- **Search** — Any log entry can be found by any field within seconds. Full-text search, field-based filtering, time-range queries.
- **Correlation** — Logs from different services about the same request can be traced together using a shared identifier (trace/request/correlation ID).

**Common stacks:** ELK (Elasticsearch, Logstash, Kibana), Loki+Grafana, Datadog Logs, Splunk, CloudWatch Logs, Fluentd/Fluentbit as collectors.

The test: "Show me every log entry for request ABC-123 across all services in the last hour." If that takes more than 30 seconds, your log aggregation needs work.

---

## §2 The expert's mental model

When I evaluate logging infrastructure, I start with an investigation scenario: **A customer reports a failed transaction 2 hours ago. How quickly can I find every relevant log entry for that transaction across every service it touched?** The investigation time is the true measure of logging quality.

**What I look at first:**
- Log structure. Are logs JSON or key-value, or are they freeform text? Unstructured logs require regex parsing at query time, which is slow and fragile. Structured logs are immediately queryable.
- Correlation IDs. Can I trace a single request through 5 services? Without correlation IDs, debugging distributed systems is assembling a puzzle without edge pieces.
- Coverage gaps. Which services DON'T send logs to the central store? Every gap is a blind spot during investigations. Particularly dangerous: background jobs, scheduled tasks, and infrastructure components like load balancers.
- Retention. How far back can I search? If logs are retained for 7 days but the customer reports an issue from 10 days ago, the evidence is gone.

**What triggers my suspicion:**
- Engineers SSH into servers to read logs. This means the central logging is missing something — either the logs aren't there, or the search is too slow to be useful.
- Log levels used inconsistently. ERROR in one service means "something is critically broken." ERROR in another service means "a retry happened." Inconsistent severity makes filtering useless.
- No log-based alerting. If the logging system can detect patterns (error rate spikes, specific error messages) but doesn't alert on them, it's a diagnostic tool only — it can't shorten detection time.
- "We use print statements." Application logs are ad-hoc `console.log` or `print` calls with no structure, no context, and no consistency. This is the most common logging failure in startups.

**My internal scoring process:**
I score by investigation speed. Can you answer "what happened to request X?" in under 2 minutes? Under 30 seconds? Under 5 seconds? The faster the investigation, the better the logging. Everything else (structure, retention, tools) is in service of that speed.

---

## §3 The audit

### Log collection and coverage
- Is there a **log collection agent** running on every compute instance? (Fluentd, Filebeat, CloudWatch agent, Datadog agent, or equivalent.)
- Are **all application services** sending logs to the central store? List every service — which ones are missing?
- Are **infrastructure logs** collected? (Load balancer access logs, CDN logs, DNS query logs, firewall logs, WAF logs.)
- Are **container/orchestrator logs** collected? (Container stdout/stderr, Kubernetes events, pod lifecycle events.)
- Are **third-party service logs** collected where available? (Auth provider, payment processor, email service.)
- Are **background jobs and scheduled tasks** logging to the central store? (These are the most commonly missed log sources.)

### Log structure and quality
- Are logs **structured** (JSON, logfmt, or key-value) rather than freeform text?
- Is there a **consistent log schema** across services? (At minimum: timestamp, severity, service name, message, request/correlation ID.)
- Are **log levels used consistently**? (Define: DEBUG, INFO, WARN, ERROR, FATAL. Enforce the definitions across all services.)
- Do logs include **sufficient context**? (User ID, request parameters, operation being performed, related entity IDs.) Can you understand what was happening from the log entry alone?
- Are **sensitive fields** redacted or masked? (Passwords, tokens, PII, credit card numbers. Logging a full credit card number is a PCI violation.)
- Are **timestamps** in a consistent format and timezone (UTC) across all services?

### Correlation and tracing
- Is there a **correlation/request ID** generated at the entry point and propagated through all downstream services?
- Can you **trace a single request** through every service it touches by searching for its correlation ID?
- Are correlation IDs included in **HTTP response headers** so that users/support can provide them for investigation?
- Are **external request IDs** (from load balancers, CDNs, API gateways) linked to internal correlation IDs?
- Can you correlate **logs with traces** if distributed tracing is also in place? (Same ID used for both.)

### Storage and retention
- What is the **log retention period**? Does it meet business and compliance requirements?
- Is retention **tiered**? (Hot storage for recent logs with fast search, warm/cold storage for older logs with slower search.) Is the tiering cost-effective?
- What is the **total daily log volume**? Is it growing? Is the growth rate sustainable with current budget?
- Are **high-volume, low-value logs** managed? (Health check logs, debug-level logs in production.) Are they sampled, filtered, or stored separately?
- Is there a **data lifecycle policy**? Are old logs automatically archived or deleted?

### Search and investigation
- Can a full-text search across all logs complete in **under 10 seconds** for a 1-hour time window?
- Are **field-based queries** fast? (Find all ERROR logs from service X in the last 24 hours — under 5 seconds.)
- Can you **save and share searches**? (Saved queries for common investigation patterns.)
- Can you **build dashboards** from log data? (Error rate over time, most common error messages, slow request patterns.)
- Is there **log-based alerting**? (Alert when a specific error message appears N times in M minutes, or when error rate exceeds threshold.)
- Can you **export log data** for offline analysis? (CSV, JSON export for when the query is too complex for the UI.)

### Operational health
- Is the **logging pipeline monitored**? (Collection agent health, processing lag, storage capacity, search latency.)
- What happens when the logging pipeline is **overloaded**? (Are logs dropped? Queued? Does back-pressure affect the application?)
- Is there **alerting on logging pipeline failures**? (If logs stop flowing, how quickly is it detected?)
- What is the **end-to-end latency** from log emission to searchability? (Under 30 seconds is good. Under 5 is excellent. Over 5 minutes means real-time investigation is impossible.)
- Is the logging infrastructure **separated** from the application infrastructure? (If the app goes down and takes the logging with it, you can't diagnose why it went down.)

---

## §4 Pattern library

**The SSH investigation** — An incident is declared. The on-call engineer SSHs into 8 servers, greps through log files, copies results to a text editor, and manually correlates timestamps. The investigation takes 45 minutes. With centralized logging and a correlation ID, it would take 2 minutes. Fix: every log line goes to the central store. No exceptions, no "we'll add it later."

**The unstructured log swamp** — Logs are freeform strings: `"2024-01-15 Error processing order 12345 for user john@example.com"`. To find all order processing errors, you need a regex. To find all errors for a specific user, you need a different regex. To combine them, you need a PhD. Fix: structured logs with fields. `{"timestamp": "...", "level": "error", "service": "orders", "order_id": 12345, "user_email": "..."}`

**The log volume explosion** — A debug-level log inside a hot loop produces 100M log lines per day. The log pipeline chokes, search slows to a crawl, and the storage bill triples. Fix: log level discipline. DEBUG stays off in production. If you need high-volume logging temporarily, use sampling (log 1% of events) or a separate pipeline.

**The orphaned correlation ID** — The API gateway generates a request ID and passes it to the first service. The first service generates its OWN request ID and passes THAT downstream. Now there are two IDs, neither traces the full path. Fix: one correlation ID, generated at the entry point, propagated to every downstream service without modification.

**The PII in production logs** — Full email addresses, names, phone numbers, and occasionally credit card numbers in log entries. The logging system has become a secondary PII store that nobody audits and nobody encrypts properly. Fix: log sanitization at the source. Mask or hash PII fields before they reach the log pipeline. Audit regularly.

**The silent log pipeline failure** — The Fluentd agent crashed on 3 out of 20 servers. Nobody noticed because there's no monitoring of the log pipeline itself. For 2 weeks, those 3 servers have no logs in the central store. During an incident, the investigation has a blind spot exactly where the problem is. Fix: monitor the log pipeline. Agent health, throughput, error rates, lag.

**The timestamp timezone mismatch** — Service A logs in UTC. Service B logs in US/Eastern. Service C logs in the server's local timezone (which changes during DST). During an incident, correlating events across services requires mental timezone arithmetic at 3 AM. Fix: all services log in UTC. No exceptions. Convert to local time in the display layer if needed.

**The log retention cliff** — Logs are retained for 14 days to manage costs. A customer reports a bug they noticed 3 weeks ago. The logs are gone. The investigation is impossible. Fix: tiered retention — detailed logs for 30 days, summarized/sampled logs for 90 days, and indexed events for 1 year. Match retention to your incident investigation timeline, not just your storage budget.

---

## §5 The traps

**The "we log everything" trap** — Logging everything sounds thorough. In practice, it means enormous storage costs, slow queries, and so much noise that finding the signal is harder, not easier. Log what you need for debugging, operations, and compliance. Actively decide what NOT to log.

**The tool-as-solution trap** — "We deployed the ELK stack, so our logging is done." The tool is 20% of the solution. The other 80% is structured log formats, consistent schemas, correlation IDs, retention policies, and team training. A perfectly running Elasticsearch cluster with unstructured, uncorrelated logs is just a faster way to search through garbage.

**The retention-as-cost-only trap** — "We only keep 7 days of logs to save on storage." But compliance requires 90 days, and security investigations need 6 months of history. Retention is a business decision, not a cost optimization. Store critical logs in cold storage if cost is a concern, but don't delete evidence.

**The dashboard-as-monitoring trap** — Beautiful Kibana dashboards showing log patterns. Nobody looks at them unless there's an incident. Dashboards are investigation tools, not monitoring tools. If a dangerous log pattern (repeated errors, authentication failures, unexpected exceptions) isn't triggering an alert, it's not being monitored.

**The "it's just logs" security trap** — Log data often contains sensitive information (even after sanitization): user IDs, IP addresses, API endpoints, error messages that reveal system architecture. The logging system needs access controls, encryption, and audit logging of its own.

---

## §6 Blind spots and limitations

**Logs don't capture what didn't happen.** If a request was silently dropped by the load balancer, there's no application log for it. Log aggregation shows you what your services processed, not what they should have processed. Supplement with synthetic monitoring and infrastructure-level logging.

**Log aggregation doesn't replace distributed tracing.** Logs show events in sequence. Traces show the causal relationship between events. For complex distributed systems, you need traces to understand the "why" behind the "what" in logs. See Observability Depth (Framework 12).

**Log search is only as good as the log content.** The most sophisticated search infrastructure can't find information that wasn't logged. If a critical function logs "operation complete" without context, the log entry is findable but useless for debugging.

**Log aggregation has inherent latency.** Between the moment a log is written and the moment it's searchable, there's a pipeline delay. For real-time debugging, this delay matters. If you need sub-second log visibility, you may need a streaming pipeline alongside the aggregation pipeline.

**Log aggregation at scale is expensive.** At 10TB/day ingestion, log aggregation is a significant cost center. The cost of storing, indexing, and querying logs grows faster than the value of marginal log data. Budget for logging and optimize what you ingest.

---

## §7 Cross-framework connections

| Framework | Interaction with Log Aggregation |
|-----------|----------------------------------|
| **Monitoring and Alerting (05)** | Metrics show THAT something is wrong (quantitative). Logs show WHAT happened (qualitative). Log-based alerting bridges the gap — pattern-matching on log content triggers alerts. |
| **Observability Depth (12)** | Logs are one of the three observability pillars (logs, metrics, traces). Without structured, correlated logs, the observability story is incomplete. |
| **Incident Response (06)** | Logs are the primary investigation tool during incidents. If logs are missing, unstructured, or unsearchable, incident investigation takes hours instead of minutes. |
| **12-Factor App (01)** | Factor 11 says logs should be written to stdout and captured by the environment. This is the foundation of log aggregation — the app doesn't manage log routing, the platform does. |
| **Container Health (09)** | Container logs (stdout/stderr) are the primary log source in containerized environments. The log aggregation pipeline must capture container output reliably, including from ephemeral containers. |
| **Secret Rotation (10)** | Log sanitization is critical when secrets might appear in error messages. A failed connection string logged as an error might expose a password. Sanitize at the source. |
| **Security (cross-domain)** | Logs are both a security tool (audit trail, intrusion detection) and a security risk (PII exposure, credential leakage). Security teams need read access to logs for forensics; privacy teams need assurance that PII is sanitized. |
| **Compliance (cross-domain)** | SOC2 CC7.2 requires event logging for security-relevant events. GDPR requires that log data containing PII be subject to the same retention and deletion policies as other personal data. Compliance drives both what you log and how long you keep it. |
| **Data (cross-domain)** | Log data is increasingly fed into data pipelines for analytics (user behavior, feature usage, error patterns). The log aggregation system becomes a data source — schema consistency, reliability, and completeness matter for downstream consumers. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (operational risk) |
|---------|-------------------|---------------------|-----------------------------|
| **Small team, few services** | Log format inconsistencies | No correlation IDs | Logs only on local servers, no aggregation |
| **Microservices architecture** | Some services log differently | Investigation takes > 10 minutes | Cannot trace requests across services |
| **High-traffic platform** | Log pipeline latency > 2 minutes | High-volume logs not sampled/filtered | Log pipeline failures go undetected |
| **Regulated/compliant** | Minor PII exposure in logs | Retention below compliance requirements | No audit logging of log access |

**Severity multipliers:**
- **Architecture complexity**: Monolith with 1 log stream is simple. 50 microservices with 200 containers need rigorous log aggregation or investigation is impossible.
- **Incident frequency**: Teams with frequent incidents depend on logging for MTTR. Poor logging means longer outages, which means more revenue impact and more pager fatigue.
- **Compliance requirements**: HIPAA, SOC2, PCI all have log retention and access control requirements. Gaps are compliance findings.
- **Team size**: A team of 3 might manage with SSH access. A team of 30 cannot. Centralized logging is a scaling requirement.

---

## §9 Build Bible integration

| Bible principle | Application to Log Aggregation |
|-----------------|-------------------------------|
| **§1.5 Single source of truth** | The centralized log store is the single source of truth for operational events. If engineers are also checking local log files, there are two sources, and they'll diverge. |
| **§1.12 Observe everything** | Structured logging is the primary mechanism for observability. Every service, every component, every significant operation should produce structured log output. |
| **§1.4 Simplicity** | Log structure should be simple and consistent. One schema, one format, one timestamp format, one timezone. Complexity in log formats becomes complexity in every investigation. |
| **§6.7 The god file** | A single log stream from a monolith that contains every event type is the logging equivalent of a god file. Separate log streams by service or concern for manageable investigation. |
| **§6.8 The silent service** | A service that doesn't send logs to the central store is a silent service. It exists in production but is invisible to operators. Every service must log centrally. |
| **§1.8 Prevent, don't recover** | Log-based alerting (detecting error patterns before they become outages) is preventive. Log-based investigation after an outage is recovery. Do both, prioritize prevention. |
