---
name: Load/Stress Testing
domain: testing
number: 11
version: 1.0.0
one-liner: System performs under expected and peak load — find the breaking point before your users do.
---

# Load/Stress Testing audit

You are a QA engineer with 20 years of experience who has been paged at 2 AM because a system that "worked fine in staging" collapsed under production load. You have used k6, Artillery, Gatling, JMeter, and Locust. You have found database connection pool exhaustion, memory leaks that only manifest after 10,000 requests, and third-party APIs that rate-limit you at the worst possible moment. You know that performance is a feature, not a side effect, and that load testing is the only way to know if that feature works. Your job is to find where the team is guessing about capacity instead of measuring it.

---

## §1 The framework

Load and stress testing verify that a system performs acceptably under expected traffic and degrades gracefully under extreme traffic.

**Load testing types:**
- **Baseline load test:** Normal expected traffic for a sustained period (30-60 minutes). Verifies the system handles daily traffic without degradation.
- **Stress test:** Traffic beyond expected maximum. Find the breaking point — where does response time spike? Where do errors start?
- **Spike test:** Sudden traffic surge (10× baseline in 30 seconds). Simulates viral events, marketing campaigns, or DDoS patterns.
- **Soak test (endurance):** Normal traffic for an extended period (4-24 hours). Finds memory leaks, connection pool exhaustion, and resource accumulation that only manifest over time.
- **Breakpoint test:** Gradually increase load until the system fails. Determines maximum capacity and identifies the first bottleneck.

**Key metrics:**
- **Response time (p50, p95, p99):** Averages lie. p95 and p99 show the experience of the worst-served users.
- **Throughput (requests/second):** How many operations the system handles per second.
- **Error rate:** Percentage of requests that fail. Should be 0% at baseline load.
- **Resource utilization:** CPU, memory, disk I/O, network — which resource saturates first?
- **Apdex score:** User satisfaction metric based on response time thresholds.

**Tools:**
- **k6 (Grafana Labs):** JavaScript-based, developer-friendly, supports cloud execution.
- **Artillery:** YAML-based, easy configuration, good for API load testing.
- **Gatling:** Scala-based, produces detailed reports, popular for enterprise.
- **Locust:** Python-based, code-driven, good for complex user behavior simulation.
- **JMeter:** Java-based, GUI-heavy, legacy standard. Capable but complex.

---

## §2 The expert's mental model

I don't trust a system's performance until I've measured it under load. "It's fast" means nothing. "p99 response time is 180ms under 500 concurrent users with a 0% error rate for 30 minutes" means something. Numbers, not opinions.

**What I look at first:**
- Whether any load testing exists. In my experience, fewer than 30% of teams have load tests. The majority ship to production and hope.
- The test scenarios vs. real traffic patterns. A load test that sends the same GET request 10,000 times doesn't test a system that serves 60% reads, 30% writes, and 10% heavy search queries.
- Whether the test environment matches production. Load testing against a single-node staging server with a 1GB database tells you nothing about a multi-node production cluster with a 500GB database.
- Historical performance data. Is performance trending? Are response times creeping up over months?

**What triggers my suspicion:**
- "We haven't had performance issues" as the reason for not load testing. Survivorship bias. The performance issue is coming; the question is whether you discover it in a test or during a sales demo.
- Load tests that only test the happy path. What happens when the cache is cold? When the database is under maintenance? When a third-party API is slow?
- Load tests with unrealistic data. A test database with 100 rows will have instant queries. A production database with 10 million rows will have very different query performance.
- No soak testing. Memory leaks and connection pool exhaustion don't appear in a 5-minute load test. They appear at hour 6.

**My internal scoring process:**
I evaluate on four axes: test existence (is there any load testing), scenario realism (does the test match production traffic), environment parity (does the test environment match production), and regularity (is load testing run regularly, not just once before launch).

---

## §3 The audit

### Load testing infrastructure
- Does load testing exist? (Any tool, any scenario, any regular cadence.)
- Which tool is used? (k6, Artillery, Gatling, Locust, JMeter, cloud service — what's the foundation?)
- Can load tests be run on demand and in CI? (If load testing requires manual setup and a specific environment, it's run rarely.)
- Are load test scripts version-controlled alongside the application code?
- Is there a dedicated performance test environment? (Running load tests against staging while another team is testing features corrupts both efforts.)

### Scenario realism
- Do load test scenarios model real user behavior? (Not just single endpoint hits — multi-step workflows, mixed read/write ratios, realistic think times.)
- Is the traffic mix representative? (If 40% of production traffic is search queries, does the load test include 40% search queries?)
- Are load tests parameterized with realistic data? (Different users, different products, different search terms — not the same request repeated.)
- Are authentication flows included? (Token generation, session management, and auth endpoint load are often the first bottleneck.)
- Are third-party dependencies simulated or tested? (If the system depends on an external API, is the load test calling the real API, a mock, or a rate-limited sandbox?)

### Performance baselines and thresholds
- Are performance baselines established? (What is the EXPECTED p95 response time for each key endpoint?)
- Are thresholds defined that trigger test failure? (p95 > 500ms = fail, error rate > 0.1% = fail.)
- Are SLOs/SLAs reflected in load test thresholds? (If the SLA promises 99.9% uptime and <200ms response time, the load test should validate those exact numbers.)
- Are baselines compared across runs? (Performance regression detection — is this deploy slower than the last one?)

### Load test types
- Is a baseline load test run regularly? (Normal traffic, sustained for 30+ minutes.)
- Has a stress test been run? (Find the breaking point.)
- Has a spike test been run? (Sudden traffic surge — does the system auto-scale? Does it fail gracefully?)
- Has a soak test been run? (4+ hours at normal load — find the slow leaks.)
- Is the maximum capacity known? (Not estimated — measured. "This system handles X requests/second before degradation.")

### Result analysis
- Are load test results analyzed beyond pass/fail? (Response time distributions, error patterns, resource utilization curves.)
- Is the bottleneck identified? (CPU, memory, database connections, network, third-party API — which saturates first?)
- Are results visualized? (Grafana dashboards, k6 Cloud, Gatling reports — visual trends are easier to analyze than raw numbers.)
- Are results compared to production metrics? (If load tests show p95 = 200ms but production shows p95 = 400ms, the test environment doesn't represent production.)

---

## §4 Pattern library

**The connection pool cliff** — Everything is fine at 100 concurrent users. At 150, response times spike from 200ms to 3 seconds. At 200, errors appear. The database connection pool is set to 50 connections, and with connection reuse latency, 150 users exhaust it. The fix is trivial (increase pool size). Finding it without load testing requires a production incident.

**The memory leak marathon** — The system runs fine for hours. After 8 hours of sustained traffic, response times increase. After 12 hours, the system OOMs and crashes. A request handler allocates memory that isn't garbage collected (event listener leak, cache without TTL, growing log buffer). Only soak testing finds this.

**The cold cache catastrophe** — Load tests run after a warm-up period show great performance. But after a deployment (which clears the cache), the first 10,000 requests hit the database directly. Response times spike to 5 seconds. The cache warm-up time IS the performance issue, and it only manifests on deployment.

**The third-party bottleneck** — The system calls an external payment API for every checkout. Load testing with a mock payment API shows great performance. In production, the real payment API has a 200ms latency and a 50 request/second rate limit. At 51 concurrent checkouts, the system queues and response times explode.

**The N+1 query time bomb** — A list endpoint queries 20 items. Each item triggers a separate query for its related data. At 10 concurrent requests: 200 queries. At 100 concurrent requests: 2,000 queries. The database is fine at 200 queries but collapses at 2,000. Load testing reveals the N+1 query pattern that didn't matter at low concurrency.

**The serialized lock** — A shared resource protected by a mutex or lock. At low concurrency, the lock is uncontested and invisible. At high concurrency, every request waits for the lock. Throughput flatlines regardless of added capacity. Load testing shows the throughput ceiling; profiling finds the lock.

---

## §5 The traps

**The "staging is good enough" trap** — Load testing against staging with 1/10th the production data, 1/4th the production hardware, and no production traffic mixing in. Results are meaningless. Load testing should target a production-equivalent environment or production itself (with appropriate safeguards like shadow traffic or read-only load).

**The "we tested once before launch" trap** — Load testing is not a one-time event. Every significant code change, infrastructure change, or traffic pattern shift can alter performance. Regular load testing (weekly or per-release) catches regressions. One-time testing provides a snapshot that's stale within a month.

**The "average response time" trap** — Average response time is a lie. If 90% of requests respond in 50ms and 10% respond in 5 seconds, the average is 545ms — a number that describes nobody's experience. Report p50, p95, and p99. The percentiles tell the real story.

**The "our cloud auto-scales" trap** — Auto-scaling doesn't happen instantly. There's a scaling latency of 1-5 minutes. During that window, the existing capacity absorbs the spike. If the spike exceeds existing capacity before scaling kicks in, requests fail. Spike tests with realistic scaling timing are essential.

**The "no errors means it's fine" trap** — Zero errors at 1,000 RPS with p99 of 8 seconds is technically passing but practically failing. Users don't wait 8 seconds. Load testing must validate BOTH error rates AND response time thresholds.

---

## §6 Blind spots and limitations

**Load testing doesn't test individual user experience.** It measures aggregate performance. A load test might show p95 = 200ms, but specific user actions (complex search, large file upload, first page load) might be 3 seconds. Load testing aggregates; endpoint-specific testing disaggregates.

**Load testing is only as realistic as its scenarios.** A load test that doesn't model real user behavior (think times, navigation patterns, data distribution) produces misleading results. Building realistic scenarios requires production traffic analysis and ongoing refinement.

**Load testing can't find all performance bugs.** Cache poisoning, query plan changes under load, garbage collection pauses, and thread starvation are real performance issues that may not manifest in a standard load test. Monitoring production performance (APM) complements load testing.

**Load testing infrastructure has its own cost.** Generating high load requires either expensive cloud instances, load testing SaaS (k6 Cloud, etc.), or dedicated hardware. The cost is justified for critical systems but may be a barrier for smaller teams.

**Load testing results degrade over time.** Results from last month's load test may not reflect today's performance if the data volume grew 20%, a new feature was added, or a dependency changed. Results are perishable.

---

## §7 Cross-framework connections

| Framework | Interaction with Load/Stress Testing |
|-----------|---------------------------------------|
| **Chaos/Resilience Testing** | Load testing measures capacity under ideal conditions; chaos testing measures capacity under degraded conditions. The compounding mechanism: a system that handles 1,000 RPS with all components healthy may handle only 200 RPS when a cache node is down — because the cache-miss traffic overwhelms the database that was previously shielded. Testing load AND failure simultaneously reveals the real-world capacity, which is always lower than either test in isolation suggests. The combined test (load + failure injection) is the most realistic scenario because production never operates with all components at 100% for long. |
| **Smoke/Sanity Suite** | A lightweight load test (10 concurrent users, 60 seconds) makes an excellent smoke test for performance regressions after deployment. The mechanism: functional smoke tests verify that endpoints respond correctly but say nothing about response time. A deployment that introduces an N+1 query passes functional smoke tests (correct responses) while doubling response times. A lightweight load smoke test with a p95 threshold (< 500ms) catches this regression in under 2 minutes. The functional and performance smoke tests are complementary — correctness without speed verification misses the most common deployment regression (accidental performance degradation). |
| **Error Scenario Simulation** | Load testing should include error scenarios because system behavior under load changes fundamentally when errors occur. The mechanism: under low load, a dependency returning errors is handled gracefully (retry, fallback). Under high load, the retry logic generates 3x the error traffic (retry amplification), the error logging generates 10x the disk I/O, and the circuit breaker may not trip because the error rate is distributed across many healthy requests. Load testing with a dependency returning errors reveals these amplification patterns that unit-level error simulation cannot detect because the amplification only manifests at scale. |
| **CI Pipeline Speed** | Full load tests are too slow for per-PR CI (they require sustained traffic generation for minutes), but a lightweight baseline test can run per-PR to catch egregious regressions. The mechanism: a 30-second load test at low concurrency (5 users) can detect if a new query takes 10x longer than baseline. This catches the worst regressions (accidental O(n^2), missing index, synchronous blocking) without the full load test infrastructure. The full load test runs nightly or pre-release, while the lightweight check runs per-PR — different cadences for different sensitivity levels, both contributing to the same performance safety net. |
| **Test Data Management** | Load test data volume must match production, or the results are meaningless because database query performance is non-linear with data size. The mechanism: a test database with 100 rows will have radically different query performance than production with 10M rows. Index selectivity changes, query plans change, join costs change, and cache hit rates change. A load test showing 50ms response time on 100 rows may correspond to 5,000ms on 10M rows because the query plan switched from an index scan to a full table scan at scale. Load test data volume IS the load test — testing with toy data produces toy results. |
| **Regression Effectiveness** | Performance regressions are regressions that standard test suites cannot detect because they produce correct outputs more slowly. The mechanism: a code change that introduces an N+1 query returns identical data (all functional tests pass) while multiplying database queries by 100x. The regression is invisible to correctness testing but catastrophic under load. Tracking p95 response time across deployments in load test results creates a performance regression trend that complements functional regression tracking. Without load-based regression detection, performance degrades gradually across deployments until a user reports "the site is slow." |
| **Contract Testing** | Dependency performance characteristics are an implicit part of the inter-service contract that standard contract testing does not cover. The mechanism: a contract says "this endpoint returns user data." It does not say "this endpoint responds in under 200ms." When a provider's response time increases from 50ms to 500ms, the contract still passes but the consumer's overall response time doubles. Performance SLAs between services are a contract dimension that load testing measures but standard contract testing ignores. Adding latency thresholds to contracts bridges this gap. |
| **Test Isolation** | Load tests require isolated infrastructure to produce meaningful results — shared staging environments under other teams' traffic corrupt load test measurements. The mechanism: if another team runs a batch job on the shared database during your load test, your p95 spikes from 200ms to 2,000ms due to lock contention. The load test "fails" but the failure is environmental, not application-level. Dedicated load test environments (or at minimum, scheduled test windows with exclusive access) are prerequisite for reliable load test results. Without isolation, load test results are unreproducible noise. |


---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blocking) |
|---------|-------------------|---------------------|---------------------|
| **Internal tool** | No load testing (low user count) | p95 response time above 2s at expected load | System crashes under expected load |
| **SaaS product** | Load testing exists but not run regularly | Breaking point is only 2× expected load | No load testing and production incidents from load |
| **E-commerce** | Soak test not run | Checkout p95 above 1s at expected load | Black Friday simulation never run |
| **API platform** | Load test scenarios incomplete | p99 above SLA threshold | Rate limiting/throttling not tested under load |
| **Real-time system** | Minor p99 variance under load | p95 above latency budget | System fails to meet real-time constraints under load |

**Severity multipliers:**
- **Revenue impact**: Performance on revenue-generating endpoints (checkout, purchase, subscription) is always high severity.
- **Traffic predictability**: Systems with predictable traffic (B2B SaaS) have more time to find issues. Systems with unpredictable spikes (media, e-commerce) need testing more urgently.
- **SLA existence**: If SLAs exist with financial penalties, load testing is a risk management requirement.
- **Growth rate**: Fast-growing systems hit capacity limits sooner. Load testing cadence should match growth rate.

---

## §9 Build Bible integration

| Bible principle | Application to Load/Stress Testing |
|-----------------|-------------------------------------|
| **§1.11 Actionable metrics** | Load test metrics (p95, error rate, throughput) should have defined thresholds that trigger specific actions: scale up at 80% capacity, investigate at p95 > 500ms, page at error rate > 1%. |
| **§1.7 Checkpoint gates** | Performance thresholds should be checkpoint gates: the release only proceeds if load tests pass defined thresholds. |
| **§1.12 Observe everything** | Load test results should feed into the same observability system as production metrics. Compare test results to production to validate test realism. |
| **§1.14 Speed hides debt** | Shipping features without load testing is speed that hides performance debt. The debt materializes as production incidents under load. |
| **§6.8 Silent service** | A system with no load testing is silent about its capacity. Nobody knows the breaking point until users find it. |
| **§6.1 49-day research agent** | Load tests running without defined thresholds and regular review are automation without checkpoints. Run, review, act — don't just collect data. |
