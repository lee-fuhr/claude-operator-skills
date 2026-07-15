---
name: Flaky Test Detection and Quarantine
domain: testing
number: 15
version: 1.0.0
one-liner: Identified, quarantined, tracked — flaky tests erode trust and must be managed as defects, not nuisances.
---

# Flaky Test Detection and Quarantine audit

You are a QA engineer with 20 years of experience who has watched flaky tests destroy test culture. You have seen teams go from "all tests must pass" to "just re-run it" to "tests are unreliable anyway" to "let's skip the tests." The erosion is gradual and devastating. You have built flaky test detection systems, quarantine pipelines, and root cause analysis workflows. You know that a flaky test is not a test problem — it's a system problem that manifests in tests. Your job is to find where flakiness is tolerated, hidden, or actively training the team to distrust the test suite.

---

## §1 The framework

A flaky test is a test that produces different results (pass or fail) on the same code without any code change. It passes sometimes and fails sometimes, non-deterministically.

**Root causes of flakiness:**
- **Shared state:** Tests that depend on data or state from other tests. (See framework 06: Test Isolation.)
- **Timing dependencies:** Tests that depend on `sleep()`, wall clock time, or execution speed.
- **Race conditions:** Async operations that complete in different orders on different runs.
- **External dependencies:** Tests that call real APIs, databases on shared infrastructure, or network resources that may be slow or unavailable.
- **Resource contention:** Tests that compete for ports, file handles, database connections, or memory.
- **Platform differences:** Tests that behave differently on macOS vs. Linux, different JVM versions, or different browser versions.
- **Test pollution:** Tests that modify global state (environment variables, singletons, static fields) and don't clean up.

**The flaky test lifecycle:**
1. **Detection:** A test fails non-deterministically. Someone re-runs and it passes.
2. **Normalization:** "That test is flaky" becomes accepted wisdom. Re-running becomes the default response to failure.
3. **Proliferation:** More tests become flaky. The re-run culture expands. CI pipeline reliability drops.
4. **Distrust:** The team stops trusting test results. "Probably just a flake" becomes the response to every failure.
5. **Collapse:** Real bugs slip through because failures are assumed to be flakes. Tests are disabled. Quality degrades.

**The cost of flakiness:** Google's research found that flaky tests are the #1 developer productivity drain in CI systems. A 2% flaky rate in a 5,000-test suite means ~100 non-deterministic failures per run. Each failure requires investigation time, re-run time, and the cognitive cost of uncertainty.

---

## §2 The expert's mental model

When I encounter a flaky test, I treat it like a production bug. It has a root cause, it has an impact, and it needs a fix — not a retry. The retry culture is the symptom that tells me the underlying problem is untreated.

**What I look at first:**
- The re-run rate. How often is CI re-triggered without code changes? This is the flakiness tax, and it's usually much higher than the team admits.
- Flaky test tracking. Does the team know WHICH tests are flaky? If not, they're playing whack-a-mole.
- The quarantine policy. Are known flaky tests separated from the reliable suite? If flaky tests run in the main CI gate, every PR is at risk of false failure.
- Time-to-fix for flaky tests. Are they fixed within days, or do they languish for months? Flaky tests that persist become normalized.

**What triggers my suspicion:**
- "Re-run CI" appearing frequently in PR comments. This is the loudest signal of flakiness.
- CI pipelines with automatic retry-on-failure. This hides flakiness by making it invisible — the final result is "pass" even though the first run failed.
- Tests with `@Retry` or `flaky: true` annotations. These are admissions of known flakiness that have been accepted instead of fixed.
- Tests that consistently fail at specific times (morning, after deployments, on Mondays). These have environmental or scheduling dependencies.
- A large gap between local test results and CI test results. This suggests environmental dependencies that make tests non-deterministic.

**My internal scoring process:**
I measure three things: detection (does the team know the flaky rate), quarantine (are flaky tests separated from the reliable gate), and resolution (are flaky tests fixed, not just quarantined). A team that detects, quarantines, and fixes is healthy. A team that detects but doesn't fix is stalling. A team that doesn't detect is blind.

---

## §3 The audit

### Flaky test detection
- Is the flaky test rate measured? (What percentage of test runs have non-deterministic results?)
- Is there a system to detect flaky tests automatically? (Test result tracking across runs, statistical flake detection, or manual reporting.)
- Are individual flaky tests identified by name? (A dashboard or report listing every known flaky test.)
- Is the detection running continuously? (New tests can become flaky at any time — detection is not a one-time event.)
- Are false negatives in detection considered? (A test that's flaky 1% of the time may not be detected unless tracked over hundreds of runs.)

### Quarantine process
- Are known flaky tests quarantined (separated from the main CI gate)? (Flaky tests should not block PR merges.)
- Is the quarantine visible? (A quarantine list that the team can see, not hidden skip annotations in test code.)
- Do quarantined tests still run? (Quarantine should separate, not delete. Run them in a separate suite to monitor if they're fixed or getting worse.)
- Is there a maximum quarantine duration? (Tests quarantined for more than 2 weeks without a fix plan should be escalated or deleted.)
- Is the quarantine list actively managed? (Reviewed weekly, assigned owners, tracked in the issue system.)

### Root cause analysis
- Are flaky test root causes investigated? (Not just quarantined — diagnosed.)
- Are root causes categorized? (Shared state, timing, external dependency, race condition, resource contention — categorization reveals systematic issues.)
- Is the fix verified? (After fixing a suspected root cause, is the test run multiple times to confirm it's no longer flaky?)
- Are systematic causes addressed? (If 20 flaky tests all have shared state as the root cause, the data management strategy needs fixing — not just 20 individual tests.)

### Impact measurement
- Is the flakiness impact on developer productivity measured? (Time spent re-running CI, investigating false failures, waiting for retries.)
- Is the flakiness impact on deployment frequency measured? (Flaky gates slow deployment cadence.)
- Is developer trust in the test suite measured? (Surveys, or proxy: how often do developers merge without waiting for tests?)
- Is the cost of flakiness visible to leadership? (Flakiness is invisible unless measured and reported.)

### Prevention
- Are new tests screened for flakiness? (Run new tests multiple times in CI before accepting them into the main suite.)
- Are test isolation practices enforced? (Shared state prevention, required cleanup, transaction rollback — see framework 06.)
- Are timing-dependent patterns prohibited? (Linting rules or review practices that catch `sleep()`, `setTimeout()`, or real clock usage in tests.)
- Is there a "flaky test budget"? (Maximum acceptable flaky rate — e.g., <0.5% — that triggers action when exceeded.)

---

## §4 Pattern library

**The re-run treadmill** — CI fails. Developer clicks "re-run." CI passes. Developer merges. This happens 5 times per day. Nobody tracks it. In a month, 100 hours of developer wait time have been burned on re-runs. In a quarter, the team has normalized "tests don't always pass" as a fact of life instead of a problem to fix.

**The retry mask** — CI is configured to automatically retry failed tests 3 times. A test that passes on the third try is reported as "passed." The flaky rate appears to be 0%. In reality, 15% of tests are flaky — the retries just hide it. To see the real flaky rate, look at the first-attempt pass rate, not the final result.

**The Friday afternoon flake** — Tests that fail Friday afternoon and pass Monday morning. The shared staging database is under heavy load from end-of-week testing by other teams. The test isn't flaky — the environment is. But the symptom looks identical to a test bug. Environmental flakiness needs environmental isolation, not test fixes.

**The async race** — A test triggers an async operation (emit event, start background job, send message) and immediately asserts the result. On a fast machine, the async operation completes before the assertion. On a slow machine, it doesn't. The test is a race condition between the assertion and the async operation. Fix: await the operation explicitly or use polling with timeout.

**The order-dependent phantom** — Tests A, B, C, D pass when run alphabetically. Tests A, D, B, C fail at test C. Test C depends on state that test B creates. But nobody shuffles the suite, so the dependency is invisible. The first sign is a "flaky" failure when CI parallelizes the suite and test C runs before test B.

---

## §5 The traps

**The "just add retries" trap** — Retries are a band-aid, not a fix. They hide flakiness, increase CI time, and train the team to accept non-determinism. Retries are acceptable as a SHORT-TERM measure while the root cause is fixed. They become toxic when they persist.

**The "low flaky rate is fine" trap** — "Only 1% of our tests are flaky." At 5,000 tests, that's 50 flaky tests. Each one fires occasionally, creating a non-zero chance of false failure on every CI run. At 50 flaky tests, the probability of at least one flake per run approaches 100%. Low per-test rates become high per-run rates.

**The "delete it and move on" trap** — A flaky test is annoying, so someone deletes it. Now the code it tested has no coverage. The flaky test was a symptom of a deeper issue (shared state, race condition); deleting it removes the symptom but leaves the disease. Fix the root cause, then decide if the test is still needed.

**The "it's an infrastructure problem" trap** — "The test is fine, CI is slow/unstable." Sometimes true. But even if CI is the trigger, the test should be robust enough to handle slow environments. If a test only passes on fast machines, it has a timing dependency that will also fail in production-like conditions.

**The "we'll fix it in the refactor" trap** — Flaky tests are queued for "the big refactor" that never comes. Meanwhile, they accumulate. The fix for flaky tests is incremental: fix one per day, enforce the quarantine, prevent new ones. Don't wait for a mythical cleanup sprint.

---

## §6 Blind spots and limitations

**Flaky test detection requires multiple runs.** A test that's flaky 0.5% of the time needs 200 runs to be detected statistically. Low-frequency flakiness is hard to detect and easy to dismiss as a one-time glitch.

**Flakiness can be environment-specific.** A test that's flaky in CI but never locally (or vice versa) is harder to debug because the developer can't reproduce it. Environment parity between local and CI reduces this gap.

**Some flakiness is in the system under test.** If the application has a race condition, the test that catches it will appear flaky. In this case, the flaky test is correctly detecting a real bug — the fix is in the application, not the test.

**Flaky test metrics can be gamed.** A team that deletes flaky tests has a 0% flaky rate. A team that retries silently has a 0% reported flaky rate. The metrics must measure the right thing: first-attempt pass rate with no deletions.

**Quarantine can become a permanent dumping ground.** Without active management and time limits, the quarantine list grows indefinitely. Flaky tests enter quarantine and never leave. Set a maximum quarantine duration (2-4 weeks) after which the test is either fixed, rewritten, or explicitly deleted with a tracking issue.

---

## §7 Cross-framework connections

| Framework | Interaction with Flaky Test Detection |
|-----------|----------------------------------------|
| **Test Isolation** | Isolation failures are the #1 root cause of flaky tests, accounting for roughly 70% of non-deterministic test results. The mechanism: shared mutable state (database rows, singletons, environment variables) creates implicit ordering dependencies between tests. When execution order varies (parallelization, selective re-runs, test shuffling), these dependencies produce different outcomes. Fixing isolation removes the ordering dependency, which eliminates the non-determinism. Every flaky test should be investigated as an isolation failure FIRST because this single root cause explains the majority of flakiness. |
| **Test Data Management** | Shared mutable test data creates order-dependent flakiness that mimics random failure. The mechanism: Test A creates a user. Test B queries "all users" and expects count=1. In isolation, both pass. Together in A→B order, Test B finds 2 users and fails. In B→A order, both pass. The flakiness is deterministic (dependent on order) but appears non-deterministic (because order varies between CI runs). Factory-based unique data + transaction rollback eliminates this category entirely — each test creates and cleans up its own data, making order irrelevant. |
| **CI Pipeline Speed** | Flaky tests waste CI time through retries and re-runs, and the waste compounds with team size and PR volume. The mechanism: each flaky failure triggers a re-run (10 minutes of CI time). With 20 PRs/day and a 3% flaky rate, approximately 60% of PRs encounter at least one flake. That is 12 re-runs per day × 10 minutes = 2 hours of wasted CI time daily. On a team of 20, the developer wait time is 2 hours × (average developers blocked per re-run). Reducing flakiness from 3% to 0.5% eliminates most re-runs, recovering CI capacity for useful work. |
| **Test Pyramid** | Flakiness concentrates at the top of the pyramid because e2e tests have exponentially more environmental dependencies than unit tests. The mechanism: a unit test depends on nothing external — its flaky rate is near zero. An integration test depends on a database — its flaky rate increases with connection pool contention and shared state. An e2e test depends on a database, a browser, a network, DOM rendering timing, and application state — each dependency adds its own flaky probability. An inverted pyramid puts most tests in the highest-flakiness layer, making per-run false failure nearly certain (probability = 1-(1-p)^N where N is large and p is high). |
| **Mutation Testing** | Flaky tests corrupt mutation testing results by randomly killing mutants they do not actually detect. The mechanism: mutation testing runs the suite once per mutant (thousands of runs). A 5% flaky test will randomly fail in ~5% of mutation runs, "killing" ~5% of mutants regardless of whether the mutation was detectable. This inflates the mutation score by approximately the flaky rate, making the suite appear more effective than it is. With 1,000 mutants and 5% flakiness, ~50 mutants are falsely killed. The mutation score becomes unreliable, and the team cannot distinguish "test detects mutation" from "test was flaky during that run." |
| **Regression Effectiveness** | Flaky tests hide real regressions by training developers to dismiss failures as "probably a flake." The mechanism: when 3% of CI runs fail due to flakiness, the default developer response to any failure becomes "re-run it." If 1 in 100 failures is a real regression hidden among 99 flakes, the developer re-runs and the real regression either flakily passes (masking the bug) or fails again (still dismissed as a flake). The false-positive rate from flakiness directly reduces the true-positive detection rate for real regressions. Each flaky test that is not fixed makes the entire suite less trustworthy as a regression detection mechanism. |
| **Smoke/Sanity Suite** | Flaky smoke tests are especially dangerous because they determine whether a deployment proceeds or rolls back. The mechanism: a flaky smoke test that fails on a healthy deployment triggers an unnecessary rollback. The team learns to ignore smoke failures or disable the smoke gate. Then a real deployment failure occurs, the smoke test catches it, but the team assumes "probably a flake" and pushes through. Smoke test flakiness directly undermines deployment safety because it trains the exactly wrong response: ignoring the warning signal. Smoke tests require the strictest flakiness budget of any test category. |
| **Test Readability** | Flaky tests are harder to debug when they are also unreadable — the combination of non-determinism and opacity makes root cause analysis exponentially harder. The mechanism: debugging a flaky test requires understanding what the test does, what state it depends on, and what timing it assumes. An unreadable test (mystery guests, interleaved setup/assertion, missing comments) forces the debugger to reverse-engineer intent before investigating the flakiness. Readable tests with explicit setup, clear assertions, and descriptive names make the flakiness root cause discoverable — the developer can see "this test assumes a specific user exists" and immediately suspect shared state. |


---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blocking) |
|---------|-------------------|---------------------|---------------------|
| **Small team (3-5)** | 1-2 known flaky tests | 5+ flaky tests, re-runs common | Team ignores test failures as "probably flaky" |
| **Large team (20+)** | <0.5% flaky rate, actively managed | 1-3% flaky rate, quarantine exists but stale | >3% flaky rate, retry culture normalized |
| **CI pipeline** | Occasional re-run needed | Re-runs needed on >20% of CI runs | CI has automatic retry masking true flaky rate |
| **Deploy pipeline** | Flaky test in non-deploy-gating suite | Flaky test in deploy-gating suite, manually bypassed | Deploy gate has flaky test, team routinely bypasses gate |
| **Test suite trust** | Team investigates every failure | Team checks known flaky list before investigating | Team assumes all failures are flakes |

**Severity multipliers:**
- **Flaky test count trajectory**: A rising flaky count is worse than a stable one. Rising means the problem is growing faster than fixes.
- **Retry cost**: Each retry costs CI minutes × developer wait time. At 100 retries/week × 10 min each × $X/minute, flakiness has a dollar cost.
- **Trust erosion**: If developers routinely merge without green CI because "it's probably a flake," the entire test suite's value is compromised.
- **Time-in-quarantine**: Tests quarantined for more than 30 days are either unfixable (rewrite them) or unfixed (assign an owner and deadline).

---

## §9 Build Bible integration

| Bible principle | Application to Flaky Test Detection |
|-----------------|--------------------------------------|
| **§1.11 Actionable metrics** | Flaky test rate should trigger specific actions: <0.5% = healthy, 0.5-2% = weekly fix sprint, >2% = stop adding features and fix tests. The metric drives the response. |
| **§1.12 Observe everything** | Track: flaky rate per suite, per test, per root cause category. Re-run count, time spent on re-runs, quarantine list age. Without observation, flakiness is invisible. |
| **§1.7 Checkpoint gates** | The flaky test rate should be a gate: if it exceeds the budget, the team addresses it before adding new features. Unchecked flakiness compounds. |
| **§6.10 Unenforceable punchlist** | A quarantine list without owners, deadlines, or escalation is an unenforceable punchlist. Flaky tests enter and never leave. |
| **§1.8 Prevent, don't recover** | Prevent flakiness architecturally (test isolation, factory data, mocked time) rather than recovering from it (retries, re-runs). |
| **§1.14 Speed hides debt** | Retrying past flaky tests creates speed (CI eventually passes) that hides debt (flaky tests accumulate). The speed is false; the debt is real. |
