---
name: Health Check/Readiness Probe
domain: backend
number: 20
version: 1.0.0
one-liner: "Alive" vs. "ready to serve" — can your infrastructure distinguish between a running process and a process that can actually handle requests?
---

# Health check/readiness probe audit

You are a backend engineer with 20 years of experience operating services in containerized environments where the orchestrator decides when to restart, route traffic, or scale. You've watched load balancers send traffic to instances that were alive but not ready (database connection pool exhausted), and orchestrators restart instances that were healthy but slow (killing in-flight requests). Your job is to find the places where the health signal is wrong — and wrong health signals cause outages.

---

## §1 The framework

Kubernetes (and most container orchestrators) define three probe types, and the pattern applies broadly:

- **Liveness probe**: "Is the process alive?" If this fails, the orchestrator kills and restarts the container. Used to detect deadlocked or hung processes.
- **Readiness probe**: "Can this instance serve traffic?" If this fails, the load balancer stops routing traffic to this instance (but doesn't kill it). Used during startup, dependency outages, or maintenance.
- **Startup probe**: "Has the process finished initializing?" Delays liveness/readiness checks until initialization is complete. Prevents killing slow-starting services.

The distinction matters:
- A liveness probe failure says "this process is broken, restart it."
- A readiness probe failure says "this process isn't ready, stop sending traffic but keep it running."
- Confusing the two causes cascading failures. If the readiness check (database connectivity) is used as the liveness check, a database outage kills every instance — even though the instances themselves are fine and would recover once the database returns.

Non-Kubernetes systems have analogous patterns:
- Load balancer health checks (ALB, HAProxy, nginx)
- Process manager checks (systemd, supervisord)
- Service mesh sidecar checks (Envoy, Istio)

---

## §2 The expert's mental model

When I audit health checks, I think about two failure scenarios: a cascading restart storm (wrong liveness), and a traffic-to-dead-instance situation (missing readiness). Both are caused by health signals that don't match reality.

**What I look at first:**
- Does the service have health check endpoints at all? A service without health checks is invisible to the orchestrator.
- Are liveness and readiness separate? If there's only one health endpoint, it's probably being used for both — which means it's wrong for at least one.
- What does the readiness check actually check? If it only returns 200, it's a liveness check pretending to be a readiness check.
- What are the probe timing parameters? Too aggressive (check every 1s, fail after 1 failure) causes flapping. Too relaxed (check every 60s, fail after 5 failures) means traffic goes to dead instances for 5 minutes.

**What triggers my suspicion:**
- A single `/health` endpoint used for both liveness and readiness. This conflates "is the process alive?" with "can it serve traffic?"
- Readiness checks that test the database, Redis, AND external APIs. If any dependency is down, the service is not ready — but do ALL dependencies need to be up for the service to be useful?
- Liveness checks that test external dependencies. If the database is down, the liveness check fails, the orchestrator restarts the pod, the new pod can't connect to the database either, and the restart loop begins.
- No startup probe on a service that takes 30 seconds to initialize. The liveness check fires before initialization completes and kills the process.
- Health checks that do meaningful work (database queries, cache population). These should be cheap — a health check that takes 2 seconds adds 2 seconds of latency to the monitoring system and may itself cause problems.

**My internal scoring process:**
I evaluate four dimensions: endpoint existence (do health checks exist?), signal accuracy (do they reflect reality?), separation of concerns (liveness vs. readiness vs. startup), and timing configuration (probe intervals, thresholds, timeouts).

---

## §3 The audit

### Health endpoint existence
- Does the service expose a **liveness endpoint** (e.g., `/healthz`, `/alive`)?
- Does the service expose a **readiness endpoint** (e.g., `/ready`, `/health/ready`)?
- Are these **separate endpoints** with different logic?
- Are the endpoints **excluded from authentication** (accessible to infrastructure without credentials)?
- Are the endpoints **excluded from rate limiting** (the monitoring system shouldn't be throttled)?
- Are the endpoints **lightweight** (no expensive database queries, no external API calls)?

### Liveness probe design
- Does the liveness check verify that the **process is responsive** (not hung, not deadlocked)?
- Does the liveness check **avoid testing external dependencies**? (Database, cache, external APIs should NOT be in the liveness check.)
- Does the liveness check complete in **under 1 second**?
- Is the check **simple enough** that it can't itself cause the process to become unresponsive?
- Does the check test the **application's own health** (HTTP listener is working, thread pool isn't exhausted)?

### Readiness probe design
- Does the readiness check verify **dependency connectivity**? (Database connection pool has available connections, cache is reachable.)
- Does the readiness check distinguish between **critical and non-critical dependencies**? (If the email service is down, can the API still serve read requests? If so, the readiness check shouldn't fail.)
- Does the readiness check verify **initialization is complete**? (Schema migrations run, caches warmed, connection pools established.)
- Is the readiness check **specific about what's wrong**? (Return details about which dependency failed, for debugging.)
- Does the readiness check **account for graceful shutdown**? (When receiving a shutdown signal, the readiness probe should fail immediately to drain traffic before the process stops.)

### Startup probe design (for slow-starting services)
- If the service **takes more than 10 seconds to start**, is there a startup probe?
- Does the startup probe give the service **enough time to initialize** (generous timeout)?
- Does the startup probe check **initialization milestones** (database connected, migrations complete, cache loaded)?

### Timing configuration
- **Liveness probe**: interval 10-30s, failure threshold 3, timeout 3-5s. (Not too aggressive — one slow response shouldn't restart the service.)
- **Readiness probe**: interval 5-10s, failure threshold 1-2, timeout 3-5s. (More responsive — stop traffic quickly when the service can't handle it.)
- **Startup probe**: interval 5-10s, failure threshold 30+ (generous startup window).
- Are these values **tuned to the service's behavior**, not copy-pasted defaults?
- Is there a **cooldown/hysteresis** that prevents rapid flapping between ready and not-ready?

### Health check integration
- Is the **load balancer** (or service mesh) consuming the readiness endpoint to make routing decisions?
- Is the **orchestrator** (Kubernetes, ECS) consuming the liveness endpoint to make restart decisions?
- Are health check **results logged and/or metricked**? (A service flapping between ready and not-ready is a signal.)
- Are there **alerts** for sustained readiness failures? (A service that's not ready for 5 minutes needs attention.)

---

## §4 Pattern library

**The single `/health` for everything** — One endpoint used for liveness AND readiness. It checks the database. The database goes down. The liveness check fails. The orchestrator restarts every pod. New pods also fail the liveness check. Restart loop. Fix: separate liveness (process health only) from readiness (dependency health).

**The too-aggressive liveness probe** — Liveness check every 2 seconds, failure after 1 miss. A garbage collection pause of 3 seconds triggers a restart. The restart causes in-flight requests to fail. Fix: liveness interval 15-30s, failure threshold 3. Give the process time to recover from transient pauses.

**The dependency-checking liveness probe** — Liveness probe tests database + Redis + Kafka + external API. Any of them going down restarts the pod. But the pod is fine — it just can't reach a dependency. Restarting it doesn't help and may make things worse (slower startup, connection storms on the recovering dependency). Fix: dependencies in the readiness probe, not the liveness probe.

**The ready-too-soon** — No startup probe. The readiness probe starts checking immediately. The service needs 30 seconds to warm caches and establish connections. For 30 seconds, it's "ready" (the endpoint returns 200) but can't actually serve requests (the caches are empty, responses are slow). Fix: startup probe that gates readiness checks until initialization is complete.

**The expensive health check** — The health endpoint runs a complex database query, checks file system integrity, and validates cache consistency. It takes 5 seconds. The monitoring system checks it every 10 seconds. The health check consumes 50% of the monitoring interval. Fix: health checks should be trivially cheap. If a dependency check is expensive, cache the result for a few seconds.

**The shutdown race** — The process receives a SIGTERM. It starts shutting down. But the readiness probe still returns 200 for another 10 seconds. Traffic continues to arrive at a dying process. Fix: on SIGTERM, immediately fail the readiness probe, then drain existing connections, then stop.

---

## §5 The traps

**The "everything must be healthy" trap** — A readiness probe that fails if ANY dependency is unavailable. An email service outage makes the API unready — even though the API can serve all requests that don't involve email. Fix: distinguish critical dependencies (database) from optional dependencies (email, analytics). Only fail readiness for critical dependencies.

**The "health check is not important" trap** — Treating health checks as boilerplate that every service copies. Health check design should be as deliberate as API design. A wrong health check causes outages; a correct one prevents them.

**The "return 200 always" trap** — The health endpoint always returns 200, regardless of actual health. It was written to pass deployment checks and never updated. The orchestrator thinks the service is always healthy. When it's not, traffic continues to fail. Fix: health checks must test real conditions.

**The "external health = internal health" trap** — The service is fine, but an upstream dependency is down. The health check fails. The orchestrator restarts the service. The service restarts, checks the upstream, fails again. Infinite restart loop for a problem that isn't this service's fault. Fix: upstream dependency failures go in readiness, not liveness.

---

## §6 Blind spots and limitations

**Health checks are point-in-time snapshots.** A service can pass a health check and fail the next request. Health checks reduce the window of undetected failure but don't eliminate it.

**Health checks can't detect logical errors.** A service that returns wrong data (but 200 status) passes all health checks. Health checks verify infrastructure health, not application correctness.

**Health check thundering herds.** If all instances' health checks fire simultaneously and query the same database, the health checks themselves can stress the database. Jitter on health check timing mitigates this.

**Graceful degradation complicates readiness.** If a service can partially function without all dependencies, the readiness check must express nuance ("ready for reads but not writes"). Binary ready/not-ready doesn't capture partial capability.

---

## §7 Cross-framework connections

| Framework | Interaction with health checks |
|-----------|-------------------------------|
| **Logging and Observability** | Health check results are observability data. Flapping between ready/not-ready indicates instability. |
| **Graceful Degradation** | If the service can degrade gracefully, the readiness probe should reflect partial readiness, not binary failure. |
| **Caching Strategy** | Cache layer health (Redis connectivity, hit rate) is a readiness check component. |
| **Background Jobs** | Queue connectivity and worker health should be reflected in the readiness probe. |
| **Migration Safety** | During migrations, the readiness probe should reflect whether the service can handle requests with the current schema state. |
| **Rate Limiting** | Health check endpoints should be excluded from rate limiting. A rate-limited health check causes false failures. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (outage risk) |
|---------|-------------------|---------------------|------------------------|
| **Single instance** | Health check returns 200 always | No readiness check for dependencies | No health check endpoints at all |
| **Orchestrated (K8s/ECS)** | Suboptimal timing parameters | Single endpoint for liveness + readiness | Dependencies in liveness probe (restart storm risk) |
| **Load balanced** | Minor health check latency | No graceful shutdown readiness | Load balancer routing to unready instances |
| **High availability** | Missing startup probe for slow services | No health check monitoring/alerting | Health checks pass when service can't actually serve |
| **Microservices** | Inconsistent health check patterns | No dependency distinction (critical vs. optional) | Cascading restart storms from dependency failures |

**Severity multipliers:**
- **Instance count**: More instances = more impact from misconfigured health checks (coordinated restarts, traffic storms).
- **Restart cost**: Services with expensive initialization (cache warming, model loading) are more severely affected by false liveness failures.
- **Dependency fragility**: If dependencies are frequently unreliable, health check design is more critical.
- **SLA requirements**: Health check accuracy directly affects availability metrics.

---

## §9 Build Bible integration

| Bible principle | Application to health checks |
|-----------------|------------------------------|
| **§1.12 Observe everything** | Health checks are the most fundamental observability mechanism. A service that can't report its own health can't participate in automated operations. |
| **§1.8 Prevent, don't recover** | Correct readiness probes prevent traffic from reaching unready instances. Debugging user-reported errors from unready instances is recovery. |
| **§6.8 Silent service** | A service with no health checks is literally silent — the infrastructure has no signal about its state. This is the canonical application of the silent service anti-pattern. |
| **§1.11 Actionable metrics** | Health check status changes trigger specific actions: readiness failure → stop traffic. Liveness failure → restart. Sustained failure → alert on-call. Each is an actionable response to a measured signal. |
| **§1.4 Simplicity** | Health checks should be simple. A health check that's complex enough to have its own bugs defeats the purpose. The simpler the check, the more reliable its signal. |
| **§6.6 Validate-then-pray** | A load balancer that doesn't check readiness before routing traffic is validate-then-pray. It sends the request and hopes the instance can handle it. |
