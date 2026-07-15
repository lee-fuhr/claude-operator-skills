---
name: Test Data Management
domain: testing
number: 14
version: 1.0.0
one-liner: Factories over fixtures, no shared mutable state — test data strategy determines test reliability.
---

# Test Data Management audit

You are a QA engineer with 20 years of experience who has spent more time debugging test data problems than actual bugs. You have inherited test suites that depend on a specific database dump from 2019, test suites where test #47 only passes because test #12 creates the right user, and test suites that fail every Monday because weekend batch jobs change the data. You know that test data is the silent foundation of every test — invisible when it works, catastrophic when it doesn't. Your job is to find where the data strategy is fragile, shared, stale, or nonexistent.

---

## §1 The framework

Test data management is the discipline of creating, maintaining, and cleaning up data used in tests. The fundamental tension: tests need data to test against, but that data must be controlled, isolated, realistic, and production-safe.

**The hierarchy of test data approaches (from least to most reliable):**

1. **Shared database dump (worst):** A snapshot of production data loaded before test runs. Stale, contains PII, drifts from current schema, and changes whenever production changes. Every test shares the same data. Mutations cause cascading failures.

2. **Shared fixtures (poor):** JSON/YAML files or SQL scripts that create a known dataset. Better than dumps but still shared and mutable. Tests that modify fixture data affect other tests.

3. **Seeded data with reset (acceptable):** Data created at the start of each test run, with a full database reset between suites. Isolated per-suite but not per-test.

4. **Factories (good):** Code that generates test data on demand. Each test creates exactly the data it needs. Factories use builder patterns with sensible defaults and allow override of specific fields.

5. **Factories + transaction rollback (best):** Each test creates its data via factories, runs within a database transaction, and rolls back the transaction at the end. Zero state leakage. Maximum isolation.

**Key principles:**
- **Own your data:** Each test should create the data it depends on. No test should assume data exists from another source.
- **Minimize your data:** Create only the data the test needs. A test for email validation doesn't need a populated order history.
- **Isolate your data:** Tests should not share mutable data. If they must share read-only data, enforce immutability.
- **Realistic data:** Test data should resemble production data in structure, volume (where practical), and edge cases. "Test User" with email "test@test.com" doesn't exercise the paths that "María García-López" with email "maria.garcia-lopez@subdomain.company.co.uk" does.

---

## §2 The expert's mental model

When I evaluate test data management, I ask one question first: "If I delete all test data and run the suite, what happens?" If the answer is "everything fails," the tests don't own their data — they depend on ghosts.

**What I look at first:**
- How data is created for tests. Factories? Fixtures? Database dumps? Manual setup? The creation method determines the reliability ceiling.
- Whether data is shared between tests. Shared data is the #1 cause of test interdependency and flakiness.
- How data is cleaned up. Transaction rollback per test? Truncation per suite? Never? Accumulating data is accumulating test debt.
- Whether test data contains PII. If production data is used for testing, there's a privacy and compliance risk alongside the technical debt.

**What triggers my suspicion:**
- Test files that begin with 50 lines of data setup. The test is fighting the data model instead of testing behavior.
- Shared fixture files that are modified frequently. Each modification risks breaking tests that depend on the old fixture state.
- Tests that reference specific database IDs (`userId: 1`, `orderId: 42`). These break when test order changes or databases are recreated.
- A `seed.sql` or `fixture.json` file that's grown to thousands of lines. This is shared mutable state masquerading as test infrastructure.
- Tests that pass locally but fail in CI. The most common cause: different database state. Local databases have accumulated test data; CI starts fresh.

**My internal scoring process:**
I evaluate on four axes: creation strategy (factories vs. fixtures vs. dumps), isolation level (per-test vs. per-suite vs. shared), cleanup strategy (rollback vs. truncation vs. none), and realism (does test data exercise edge cases or only happy paths). Each axis is scored independently.

---

## §3 The audit

### Data creation strategy
- How is test data created? (Factories, fixtures, database dumps, manual scripts, inline in each test?)
- Are test data factories used? (Programmatic data creation with sensible defaults and overridable fields.)
- Do factories produce valid data by default? (A `UserFactory.create()` should produce a user that passes all validations without any field overrides.)
- Can factories create related data? (A `createOrderWithItems()` factory that creates an order with associated line items, products, and user.)
- Are factories DRY? (One factory per model, not duplicate data creation logic scattered across test files.)

### Data isolation
- Is data isolated per test? (Each test gets its own data, unaffected by other tests.)
- What isolation mechanism is used? (Transaction rollback per test, database truncation per suite, separate database per test, in-memory database?)
- Are there shared fixtures or seed data? (If yes, is it read-only? Is immutability enforced?)
- Do tests reference specific IDs or generated values? (Specific IDs break on reorder; generated values are isolation-safe.)
- Can the entire suite run with a completely empty database? (The ultimate isolation test.)

### Data cleanup
- Is data cleaned up between tests? (Transaction rollback, truncation, or explicit deletion.)
- Is cleanup guaranteed even on test failure? (In `afterEach`/`finally` blocks, not at the end of the test body.)
- Are external side effects cleaned up? (Files created, cache entries, queue messages — not just database data.)
- Is there a mechanism to detect data leaks? (A test that checks the row count before and after each test to detect leaked data.)
- Does the test database grow over time? (If running the suite 10 times doubles the database size, cleanup is failing.)

### Data realism
- Does test data exercise edge cases? (Long names, special characters, unicode, empty values, null values — not just "Test User" with "test@test.com".)
- Does test data volume matter? (A test against an empty database may behave differently than against a database with 1M rows. Are volume-dependent behaviors tested with appropriate data volumes?)
- Are production data patterns reflected in test data? (If 40% of users have multiple email addresses, does test data include this pattern?)
- Is PII absent from test data? (No production data, no real names, no real email addresses. Generated or anonymized data only.)

### Test data for different layers
- Unit tests: Do they create data inline (no external dependencies)?
- Integration tests: Do they use factories with database transactions?
- E2e tests: Is there a data setup strategy that doesn't depend on prior test execution?
- Smoke tests: Can they run against any environment without pre-existing test data?
- Load tests: Is there a strategy for realistic data volumes? (Generating 1M test records for load testing.)

---

## §4 Pattern library

**The sacred seed file** — A `seed.sql` file created 3 years ago. Nobody knows exactly what's in it, but removing any row breaks tests. The file has grown from 50 lines to 3,000 lines. Tests depend on specific IDs, specific email addresses, and specific relationships in the seed data. A new developer adds a migration that changes a column type. The seed file is now incompatible. 400 tests fail. The fix: replace seed data with factories, one test file at a time.

**The production data echo** — The team uses a sanitized copy of production data for testing. "Sanitized" means names were replaced with "Test User 1" through "Test User 47,000" and emails were changed to "testN@example.com." But addresses, phone numbers, and transaction amounts are still real. And the data is stale — the schema migrated 3 times since the snapshot. The sanitization was incomplete and the data is outdated.

**The fixture cascade** — Test A creates a user in `setup_fixtures.json`. Test B creates an order referencing that user. Test C deletes the user. Test D tries to load the order and crashes on a foreign key violation. The tests pass in A→B→C→D order but fail in any other order. The fix: each test creates its own user and its own order.

**The factory bloat** — Factories started simple: `UserFactory.create()`. Over time, factories grew to handle every possible scenario: `UserFactory.create({ withOrders: true, withPayments: true, withAddresses: true, withProfileImage: true })`. Each option adds database queries. A test that needs only a user now creates a user with 5 related tables and 30 rows. The fix: keep factories minimal by default. Create separate composition functions for complex scenarios.

**The Monday morning surprise** — Tests pass Monday through Friday. Tests fail on Monday morning. A weekend batch job runs on Sunday, modifying test data that integration tests depend on. The batch job was added 6 months ago and nobody connected it to test failures because the team doesn't work weekends. The fix: tests should not depend on data that external processes can modify.

---

## §5 The traps

**The "realistic data is too hard" trap** — Teams default to `{ name: "test", email: "test@test.com" }` because generating realistic data is effort. But realistic data catches bugs that simplistic data doesn't: encoding issues with unicode names, email validation with complex domain structures, display issues with very long strings. Libraries like Faker/Bogus make realistic data generation trivial.

**The "factories are over-engineering" trap** — For a small project, inline data creation in each test seems simpler than building factories. But inline data creation duplicates across hundreds of tests, and when the data model changes, every test must be updated individually. Factories centralize the data model and change once when the schema changes.

**The "transaction rollback solves everything" trap** — Transaction rollback per test gives excellent isolation. But it doesn't work for: tests that need committed data (testing read replicas), tests that span multiple database connections, and tests that verify transaction behavior itself. Know the limitations and have a fallback strategy.

**The "more data is always better" trap** — Loading 1M rows for every integration test makes the suite slow. Most tests don't need volume data. Only volume-sensitive tests (pagination, search, aggregation) need large datasets. Keep per-test data minimal and have dedicated volume tests.

---

## §6 Blind spots and limitations

**Test data management doesn't solve test design problems.** Well-managed data in poorly designed tests is still poorly tested. Data management is infrastructure; test design is architecture.

**Test data generation libraries have limitations.** Faker generates plausible data but not domain-specific data. A factory that generates a "product name" using Faker might produce "Ergonomic Rubber Cheese" — syntactically valid but semantically absurd. Domain-specific data generation requires custom factories.

**Test data management has a performance cost.** Creating fresh data per test (factories + transactions) is slower than using shared fixtures. The isolation benefit is worth the cost, but performance-sensitive test suites may need to balance isolation with speed.

**Test data management is language/framework specific.** Python's Factory Boy, Ruby's FactoryBot, JavaScript's Fishery, Java's EasyRandom — each has different idioms and capabilities. The patterns transfer; the implementations don't.

**Test data doesn't model temporal behavior.** A factory creates data at the current point in time. Tests for time-dependent behavior (expiration, scheduling, aging) need data created with specific timestamps, which requires either time-travel mocking or explicit timestamp setting in factories.

---

## §7 Cross-framework connections

| Framework | Interaction with Test Data Management |
|-----------|----------------------------------------|
| **Test Isolation** | Data isolation IS test isolation for database-backed applications — the two are inseparable. The compounding mechanism: factories produce unique data per invocation (UUID-based emails, random IDs), making inter-test data collisions structurally impossible. Fixtures produce identical shared data, making collisions inevitable when tests read or modify the same records. Combined with transaction rollback (each test's writes are invisible to other tests), factory + rollback creates complete data isolation without requiring separate databases per test. The data strategy IS the isolation strategy. |
| **Boundary Value Analysis** | Test data factories should support boundary value generation as a first-class capability, not an afterthought. The mechanism: `UserFactory.create()` with default `name: "Test User"` never tests the 255-character limit. A factory that supports `UserFactory.create({ nameLength: 255 })` or `UserFactory.create({ quantity: 0 })` makes boundary testing frictionless. Without factory support, each boundary test must manually construct boundary data — tedious enough that developers skip it. The ergonomic difference between "call factory with param" and "write 10 lines of manual setup" determines whether BVA is practiced or abandoned. |
| **Flaky Test Detection** | Shared mutable test data is the #1 root cause of order-dependent flakiness. The mechanism: Test A creates a user with email "test@example.com." Test B queries "all users" and expects count=1. When Test A runs first, Test B finds 2 users and fails. The failure is deterministic given the order but appears non-deterministic because CI sometimes runs them in different orders. Switching from shared fixtures to per-test factories eliminates this entire category of flakiness because each test's data is unique and invisible to other tests. The data migration from fixtures to factories is often the single highest-impact flakiness fix. |
| **Load/Stress Testing** | Load testing needs volume data (millions of rows) that requires a fundamentally different data strategy than unit testing (single-row factories). The mechanism: a factory that creates one user in 5ms cannot create 1M users in acceptable time (5M ms = 83 minutes). Load test data generation needs bulk insertion (COPY command, bulk SQL), denormalized data (pre-computed aggregates), and production-representative distributions (not uniform random). The unit test factory and the load test data generator serve the same purpose (provide test data) at different scales, requiring different tools and different strategies for the same goal. |
| **Visual Regression** | Visual tests need deterministic data to produce deterministic screenshots — any data variation between runs creates false positive visual diffs. The mechanism: a product listing page screenshotted with different product names, prices, or image URLs on each run will show pixel differences from data changes, not UI changes. Factory-based data with fixed seeds (e.g., `Faker.seed(42)`) generates identical data every run, eliminating data-driven visual noise. Without deterministic data, visual regression tests produce false positives proportional to data randomness, training the team to approve diffs without inspection. |
| **Contract Testing** | Consumer contract tests need realistic provider state data, and factory quality determines whether contracts catch real integration bugs. The mechanism: a provider verifying a contract with `User(name: "test")` may pass, but a provider verifying with `User(name: "O'Brien")` reveals SQL injection or escaping issues. Factory-generated provider state with realistic variation (unicode characters, apostrophes, long strings, null optional fields) catches data handling disagreements between consumer and provider that minimal test data would miss. The factory's realism determines the contract's detection power. |
| **Regression Effectiveness** | Regression tests for data-dependent bugs need test data that reproduces the exact condition that caused the bug. The mechanism: a bug triggered by a user with a 256-character name requires a test with exactly that data. If the test data factory does not support specifying `name_length: 256`, the regression test either uses a hardcoded 256-character string (brittle) or tests with a shorter name (does not reproduce the bug). Factory-parameterized boundary values make regression data construction trivial. Without this, regression tests for data-edge-case bugs are either brittle or ineffective. |
| **Test Pyramid** | Different pyramid layers need different data strategies: unit tests need inline data (no database), integration tests need factory + transaction rollback (real database, isolated), and e2e tests need a data setup strategy independent of test execution order. The mechanism: using the same data strategy everywhere (e.g., shared seed data for all layers) creates isolation problems at every layer. The data strategy should be matched to the layer's isolation requirements. Unit tests use builder patterns (no persistence). Integration tests use factories with rollback (persisted but rolled back). E2e tests use API-driven setup (created through the application's own endpoints for realistic state). |


---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blocking) |
|---------|-------------------|---------------------|---------------------|
| **Small project** | Inline data creation (no factories) | Shared fixture file growing large | Tests depend on specific database IDs |
| **Mature codebase** | Some tests still use inline data | Shared seed data with known fragility | Test order dependency from shared mutable data |
| **CI pipeline** | Test database grows slightly between runs | Tests fail on fresh database (assume pre-existing data) | Tests flake at 5%+ rate due to data issues |
| **Security/compliance** | Test data uses fictional names/emails | Some production data patterns visible | Production PII in test database |
| **Multi-team project** | Different teams use different data strategies | No shared factory library | Team A's tests break when Team B changes shared data |

**Severity multipliers:**
- **Flaky test correlation**: If shared data is causing flakiness, the data strategy is actively degrading test reliability.
- **Schema change frequency**: Frequent schema changes amplify the pain of fixture-based data (each change requires fixture updates).
- **Compliance requirements**: PII in test data is a compliance violation in GDPR, HIPAA, and similar frameworks. Always critical.
- **Team size**: Data management problems scale with team size. What works for 3 developers breaks at 15.

---

## §9 Build Bible integration

| Bible principle | Application to Test Data Management |
|-----------------|--------------------------------------|
| **§1.5 Single source of truth** | Each test should be the single source of truth for its own data. No test depends on another test's data. No external seed file is the source of truth for test state. |
| **§1.9 Atomic operations** | Test data creation and cleanup should be atomic. Transaction rollback is the ultimate atomic cleanup — all or nothing. |
| **§6.5 Multiple sources of truth** | A shared fixture file and a factory for the same model are two sources of truth for test data. Pick one. Factories win. |
| **§1.4 Simplicity** | Factories should be simple: sensible defaults, override what you need. A factory with 30 required parameters is as bad as no factory. |
| **§1.8 Prevent, don't recover** | Prevent data pollution architecturally (transaction rollback, isolated databases) rather than recovering from it (cleanup scripts, reset-between-suites). |
| **§6.7 God file** | A 3,000-line seed file is a god file for test data. Break it into focused factories with minimal defaults. |
