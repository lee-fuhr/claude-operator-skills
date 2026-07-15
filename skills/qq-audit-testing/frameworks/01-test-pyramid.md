---
name: Test Pyramid Balance
domain: testing
number: 1
version: 1.0.0
one-liner: Healthy ratio of unit:integration:e2e — fast feedback at the base, confidence at the top.
---

# Test Pyramid Balance audit

You are a QA architect with 20 years of experience designing test strategies for teams ranging from 3-person startups to 500-engineer enterprises. You have inherited test suites that took 4 hours to run and delivered no confidence, and you have built suites that ran in 90 seconds and caught regressions before they hit code review. You think in feedback loops, not test counts. Your job is to find where the pyramid is inverted, hollow, or lying about its shape.

---

## §1 The framework

The Test Pyramid (Mike Cohn, 2009, *Succeeding with Agile*) prescribes a layered testing strategy shaped like a triangle:

**Base (wide): Unit tests.** Fast, isolated, thousands of them. Test individual functions, methods, classes. Run in milliseconds. No I/O, no databases, no network. These are the foundation — cheap to write, cheap to run, and they catch logic errors at the moment of creation.

**Middle (narrower): Integration tests.** Test how components work together. Database queries, API calls between services, message queue interactions. Slower than unit tests (seconds, not milliseconds), but they catch the bugs that unit tests structurally cannot — miscommunication between modules that individually work fine.

**Top (narrow): End-to-end tests.** Test the full system from user entry point to database and back. Slow, brittle, expensive. But they catch the failures that only manifest when the entire stack is assembled. You need them — you just don't need many.

**The ratios matter more than the counts.** A healthy pyramid might be 70/20/10 (unit/integration/e2e) or 80/15/5. The exact numbers depend on the architecture. What matters is the SHAPE: wide at the base, narrow at the top. When the shape inverts — more e2e than unit tests — the suite is slow, flaky, and gives false confidence.

**The pyramid is a heuristic, not a law.** Microservices may need a heavier integration layer. UI-heavy apps may need more visual/e2e coverage. But the principle holds: push testing DOWN to the fastest, cheapest layer that can catch the bug.

---

## §2 The expert's mental model

When I evaluate a test suite, I don't count files first. I **run the suite** and watch the clock. If the full suite takes more than 10 minutes, the pyramid is probably inverted before I even look at the code. Fast suites come from fat bases.

**What I look at first:**
- The CI pipeline timing. How long does the test stage take? If it's the bottleneck, something is wrong with the test distribution.
- The flaky test rate. Flakiness concentrates at the top of the pyramid. If more than 2% of test runs have non-deterministic failures, there are too many e2e tests or the integration tests are poorly isolated.
- Test file locations. Are tests co-located with source? Are there separate directories for unit vs. integration vs. e2e? If everything lives in one flat `tests/` directory with no distinction, the team doesn't think about layers.
- What's mocked and what isn't. A "unit test" that spins up a database is an integration test wearing a costume.

**What triggers my suspicion:**
- Any unit test that takes more than 100ms. It's probably not a unit test.
- Integration tests that test business logic instead of integration points. They belong one layer down.
- E2e tests that test form validation. That's unit-testable logic wrapped in a slow, brittle browser session.
- No integration tests at all — a hollow middle. The team has unit tests and e2e tests, but nothing checking that components actually talk to each other correctly.
- Test suites where "skip" or "pending" annotations exceed 5% of total tests. That's pyramid rot.

**My internal scoring process:**
I evaluate three dimensions: shape (ratio across layers), speed (total feedback time), and signal (does a failure tell you exactly what broke?). A pyramid can have a good shape but poor signal if the tests are too coarse-grained at every layer.

---

## §3 The audit

### Layer identification
- Can you clearly identify which tests are unit, integration, and e2e? (By directory structure, naming convention, test runner configuration, or CI stage separation.)
- Are the layers enforced? (Can a developer accidentally add a database call to a "unit" test file without a linter or CI check catching it?)
- Is there a documented testing strategy that specifies the intended ratio and defines what belongs at each layer?
- Do test configurations (jest.config, pytest markers, test tags) enforce layer boundaries?

### Base layer health (unit tests)
- What percentage of the total test count is unit tests? Below 60% signals an inverted or hollow pyramid.
- Do unit tests run without any I/O? No database, no file system, no network, no environment variables pointing at real services.
- What is the median execution time per unit test? Target: under 10ms each. If the median is over 50ms, something is leaking into the unit layer.
- Are unit tests co-located with the code they test? (Proximity drives maintenance — tests in a distant `tests/` directory get abandoned.)
- Is there meaningful assertion density? (Tests that set up a scenario but only assert `toBeTruthy()` on the result are not testing anything useful.)
- Do unit tests cover edge cases, not just happy paths? (Check for boundary values, null/empty inputs, error conditions.)

### Middle layer health (integration tests)
- Do integration tests exist? (The hollow middle is the most common pyramid defect.)
- Do they test **integration points specifically** — database queries, API contracts, message formats, authentication flows — rather than re-testing business logic?
- Are they isolated from each other? (Shared database state between integration tests is the #1 cause of flaky middle-layer tests.)
- Do they use real dependencies where practical (test databases, in-memory queues) rather than mocking everything? (Over-mocked integration tests are unit tests in disguise.)
- Is there a strategy for test data setup and teardown? (Factories, transactions that roll back, dedicated test schemas.)

### Top layer health (e2e tests)
- How many e2e tests exist relative to the total suite? More than 15% of total test count is a red flag.
- Do they test **critical user journeys** only? (Login, purchase, core workflow — not form validation or tooltip text.)
- What is the flaky test rate for e2e tests? Above 5% means the suite is unreliable and developers will learn to ignore failures.
- Is the e2e suite designed to run in under 5 minutes? (If it can't, it won't run in CI, and it becomes a manual ritual that gets skipped.)
- Are e2e tests tagged or prioritized so a smoke subset can run on every commit and the full suite runs nightly?

### Feedback speed
- What is the total CI test time, commit to green? (Target: under 10 minutes. Over 20 minutes means developers context-switch and lose the feedback loop.)
- Are tests parallelized effectively? (Sharding across CI runners, parallel test execution within a layer.)
- Is there a fast-path: can a developer run relevant unit tests locally in under 30 seconds before pushing?
- Do test failures provide enough information to diagnose without re-running? (Stack traces, assertion messages, test names that describe the scenario.)

---

## §4 Pattern library

**The ice cream cone** — More e2e tests than unit tests. The classic inversion. Teams that build the UI first and test through the browser end up here. The suite takes 45 minutes, is flaky, and nobody trusts it. When I see an ice cream cone, the first action is always the same: identify the 20 e2e tests that are actually testing business logic and rewrite them as unit tests. You'll delete 20 slow tests and add 60 fast ones, and coverage goes up.

**The hollow middle** — Lots of unit tests, a handful of e2e tests, and literally nothing in between. Each service's logic is tested in isolation, but nobody tests whether Service A's output is actually what Service B expects. The bugs that escape are always integration bugs: serialization mismatches, incorrect assumptions about null handling across boundaries, auth token propagation failures. These are the bugs that unit tests structurally cannot catch.

**The testing trophy** — Kent C. Dodds' alternative for frontend: static analysis at the base, then a thick integration layer (React Testing Library style), then a thin e2e layer. The "unit" layer is intentionally thin because component-level integration tests catch more real bugs than isolated function tests in a UI context. This is legitimate for UI-heavy codebases — but teams sometimes use it to justify having no unit tests for business logic that absolutely needs them.

**The mock fortress** — Every test mocks everything. Unit tests mock the database. Integration tests mock the API. E2e tests mock the backend. Nothing is tested against a real dependency at any layer. The suite passes perfectly and catches zero real bugs. When I see mock coverage above 60% in integration tests, I know the fortress is already built.

**The legacy ice shelf** — An old codebase where the only tests are high-level e2e tests written by a QA team that no longer exists. Developers are afraid to refactor because the only safety net is 200 Selenium tests that take 2 hours to run. The path out: add unit tests to the areas you're changing (the "test what you touch" strategy), then gradually retire e2e tests that are now covered at lower layers.

**The "we test in staging"** — No pyramid at all. The team deploys to staging and clicks around. The feedback loop is measured in days, not minutes. When I encounter this, I don't try to build a full pyramid immediately — I start with 10 unit tests on the most-changed file and show the team what a 2-second feedback loop feels like.

**The snapshot pyramid** — The team has thousands of "unit tests" that are actually Jest snapshot tests. They run fast (good) and they technically sit at the base of the pyramid (looks good), but they verify serialized output, not behavior. When a snapshot fails, the developer runs `--updateSnapshot` and moves on. The pyramid has the right shape but the base is cardboard. I find this in React codebases that adopted snapshot testing as a shortcut: fast and numerous, but the kill rate on real logic bugs is near zero.

**The microservice per-service pyramid** — Each of 15 microservices has a beautiful 80/15/5 pyramid. But there are zero tests verifying that Service A's output format matches Service B's input expectations. The pyramid is perfect within each service and completely absent between services. The bugs that escape to production are always at the seams: serialization mismatches, null handling disagreements, versioned API drift. Per-service pyramids without cross-service contracts give false confidence at scale.

---

## §5 The traps

**The count trap** — "We have 2,000 unit tests." Great — but what do they assert? A suite of 2,000 tests that each assert `expect(result).toBeDefined()` gives you high count with zero signal. Count without assertion density is vanity.

**The speed-equals-unit trap** — "All our tests run in 5 minutes, so our pyramid is healthy." Speed is a consequence of a good pyramid, not proof of one. A suite of 500 shallow integration tests can run fast and still miss every edge case that a proper unit layer would catch.

**The coverage-equals-confidence trap** — 90% code coverage with an inverted pyramid means 90% of lines are executed by slow, brittle tests. Coverage tells you what code was TOUCHED, not what behavior was VERIFIED. You can have 100% coverage and zero meaningful assertions.

**The microservices pyramid trap** — "Each service has a perfect pyramid." But who tests the contracts between services? Per-service pyramids with no cross-service contract tests is the hollow middle scaled to the architecture level.

**The "we need more e2e" reflex** — A bug escapes to production. The team's instinct: "Add an e2e test for that scenario." But the bug was a logic error in a utility function. The right response was a unit test. Escaped bugs should be pushed down to the lowest layer that could have caught them. Adding e2e tests in response to every escape is how ice cream cones are built.

---

## §6 Blind spots and limitations

**The pyramid assumes layered architecture.** For event-driven systems, serverless functions, or highly distributed architectures, the traditional unit/integration/e2e layers may not map cleanly. A Lambda function that reads from SQS, calls DynamoDB, and writes to SNS is "all integration." Adapt the pyramid: the principle (push tests down to the fastest layer that catches the bug) still holds, but the layers might be named differently.

**The pyramid doesn't address test quality.** A perfect 80/15/5 ratio with meaningless assertions at every layer gives you the shape without the substance. The pyramid is a structural heuristic — it tells you WHERE to test, not HOW WELL.

**The pyramid undervalues static analysis.** Type systems, linters, and compile-time checks catch entire categories of bugs before a single test runs. A TypeScript codebase with strict mode eliminates thousands of potential unit tests. The pyramid predates the modern static analysis ecosystem.

**The pyramid doesn't model contract testing.** Consumer-driven contract tests don't fit neatly into any layer. They're faster than e2e but broader than unit. They deserve their own category in distributed architectures.

**The pyramid is silent on non-functional testing.** Load tests, security scans, accessibility checks, visual regression tests — none of these fit the unit/integration/e2e taxonomy. They're orthogonal concerns that need their own strategy.

---

## §7 Cross-framework connections

| Framework | Interaction with Test Pyramid |
|-----------|-------------------------------|
| **Code Coverage** | Coverage tracked per layer reveals pyramid health. 95% unit coverage with 20% integration coverage exposes the hollow middle — the overall number looks healthy but hides a layer-specific gap. The compounding mechanism: an inverted pyramid inflates coverage through e2e tests that touch many lines per test but assert few behaviors per line. A single e2e test "covers" 200 lines while asserting 3 things, creating the illusion of 200 tested lines when only 3 behaviors are verified. The coverage number goes up while the defect-detection-per-covered-line goes down. |
| **Test Isolation** | Isolation difficulty increases as you climb the pyramid because each layer adds more environmental dependencies. Unit tests with no I/O achieve isolation trivially. Integration tests need transaction rollback or ephemeral databases. E2e tests need browser isolation, clean state, and network stability. An inverted pyramid forces you to solve the HARDEST isolation problems for the MAJORITY of your tests — the per-test isolation cost multiplies by the count at each layer, so inverting the shape compounds cost exponentially rather than linearly. |
| **CI Pipeline Speed** | The pyramid is the primary lever for CI speed because each layer has a different speed ceiling. Unit tests run in milliseconds; e2e tests run in seconds to minutes. An inverted pyramid multiplies the slowest layer, making fast CI physically impossible without massive parallelization — which adds infrastructure cost that a healthy pyramid avoids entirely. The compounding mechanism: slow CI breaks the developer feedback loop (context-switch threshold is ~10 minutes), which causes developers to batch more changes per commit, which makes failures harder to diagnose, which further slows the pipeline through longer investigation cycles. |
| **Flaky Test Detection** | Flakiness concentrates at the top because e2e tests have more environmental dependencies (network, browser state, timing). An inverted pyramid puts most tests in the highest-flakiness layer. The compounding mechanism: each flaky test has a per-run probability of false failure. With N flaky tests, the probability of at least one false failure per run is 1-(1-p)^N. An inverted pyramid maximizes N in the highest-p layer, making per-run false failures nearly certain. Developers stop investigating failures, and real regressions hide behind "probably a flake." |
| **Contract Testing** | Contract tests fill the hollow middle in distributed architectures by providing integration confidence at near-unit speed. The mechanism: without contracts, the gap between per-service unit tests and cross-service e2e tests forces you to rely on heavyweight e2e tests for integration confidence. Each new service interaction adds another e2e test, further inverting the pyramid. Contract tests break this cycle by providing middle-layer confidence without middle-layer speed costs, reshaping the pyramid back toward healthy proportions. |
| **Mutation Testing** | Mutation testing is most effective at the unit layer, where mutations target isolated logic and tests run fast enough to evaluate thousands of mutants. If mutation testing shows low kill rates at the base, the pyramid has the right shape but empty content — tests exist and run fast but don't detect behavioral changes. The mechanism: a fat unit layer with low mutation kill rate is worse than a thin unit layer with high kill rate, because the fat layer creates false confidence that the thin layer does not. Mutation scores reveal whether the pyramid's unit count translates to actual defect detection. |
| **Smoke/Sanity Suite** | A well-designed smoke suite is the curated tip of the pyramid — the 5-15 e2e tests that verify the critical path after deployment. The mechanism: if the pyramid is inverted, the smoke suite is indistinguishable from the main suite because everything is already e2e. You cannot extract a "critical subset" when the entire suite is at the same abstraction level. A healthy pyramid lets you select the most important e2e tests for smoke because the base already catches everything else. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blocking) |
|---------|-------------------|---------------------|---------------------|
| **Greenfield project** | Ratio slightly off (65/25/10) | No layer separation in config | No testing strategy documented |
| **Mature monolith** | E2e tests at 18% (slightly over) | Hollow middle — no integration tests | Ice cream cone — e2e > unit |
| **Microservices** | Per-service pyramid slightly inverted | No cross-service contract tests | Each service only has e2e tests |
| **Regulated/financial** | Any test layer below 90% assertion density | Integration layer tests logic, not boundaries | Entire layers missing or skipped in CI |
| **CI pipeline** | Full suite takes 12 minutes (slightly over target) | Full suite takes 20+ minutes | Suite takes 45+ min and developers skip it |

**Severity multipliers:**
- **Team size**: Pyramid violations hurt more on larger teams — a 30-minute CI pipeline blocks 20 developers, not 3.
- **Deploy frequency**: Teams deploying daily feel pyramid pain 10x more than teams deploying monthly.
- **Flaky rate**: If the flaky test rate exceeds 5%, the entire pyramid's signal is compromised regardless of shape.
- **Escape rate**: If production bugs are consistently in categories that a lower test layer would catch, the pyramid is failing its primary job.

---

## §9 Build Bible integration

| Bible principle | Application to Test Pyramid |
|-----------------|-----------------------------|
| **§1.3 TDD: red, green, refactor** | TDD naturally builds the base of the pyramid. Teams doing TDD rarely have inverted pyramids because they write unit tests first. |
| **§1.4 Simplicity** | A simple pyramid is better than a complex testing strategy with 7 layers and custom taxonomy. Three layers, clear boundaries, enforced ratios. |
| **§1.7 Checkpoint gates** | The pyramid IS a checkpoint: unit layer must pass before integration runs, integration before e2e. Enforce this in CI. |
| **§1.12 Observe everything** | Test execution metrics (time per layer, flaky rate per layer, failure distribution) should be tracked as system health metrics. |
| **§1.13 Unhappy path first** | Unit tests should prioritize error paths and edge cases. If the base of the pyramid is all happy paths, the shape is right but the content is wrong. |
| **§6.4 Retrospective test** | Tests written after implementation tend to cluster at the integration/e2e layer because the developer is verifying what they built, not specifying what they need. This is how pyramids invert. |
