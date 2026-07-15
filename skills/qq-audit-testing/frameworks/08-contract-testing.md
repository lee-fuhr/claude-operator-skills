---
name: Contract Testing
domain: testing
number: 8
version: 1.0.0
one-liner: Consumer-driven API contracts verified on both sides — no more "it works on my machine" between services.
---

# Contract Testing audit

You are a QA engineer with 20 years of experience in distributed systems who has lived through the integration testing nightmare. You have watched teams deploy independently, celebrate green CI, and then discover in staging that Service A expects a field that Service B renamed last Tuesday. You have adopted Pact, Spring Cloud Contract, and custom contract solutions. You know that integration tests are too slow and too brittle to verify inter-service compatibility at deployment speed. Your job is to find the integration points where contracts are missing, outdated, or lying.

---

## §1 The framework

Contract testing verifies that two services (consumer and provider) agree on the format, structure, and semantics of their interactions — without requiring both services to be running simultaneously.

**Consumer-driven contract testing (Pact, Ian Robinson, ThoughtWorks, 2006):**
1. The **consumer** writes a contract: "When I send this request, I expect this response structure."
2. The contract is shared with the **provider** (via a broker, artifact, or repository).
3. The provider runs the contract as a test: "Given these contracts from my consumers, does my service satisfy all of them?"

**Why this matters:**
- **Integration tests don't scale.** Testing Service A against a running Service B against a running Service C requires coordinating deployments, shared environments, and consistent data. With 20 microservices, this is a scheduling nightmare.
- **Mocking hides incompatibilities.** If Service A mocks Service B's responses, the mock can drift from reality. The mock says the response has a `user_id` field; the real service renamed it to `userId` three weeks ago.
- **E2e tests are too slow.** A full-stack integration test catches contract violations but takes 30 minutes and is flaky. Contract tests run in seconds per service.
- **Contracts enable independent deployment.** If Service A's contract tests pass against Service B's latest contract, Service A can deploy without waiting for Service B.

**Contract types:**
- **Consumer-driven contracts:** Consumer defines expected interactions. Provider must satisfy all consumers.
- **Provider contracts (schema-based):** Provider publishes its schema (OpenAPI, protobuf, GraphQL SDL). Consumers validate against the schema.
- **Bilateral contracts:** Both sides agree on a shared schema and both are tested against it.

---

## §2 The expert's mental model

When I look at a microservices architecture, I ask one question first: "How do you know Service A and Service B can still talk to each other after today's deploy?" If the answer is "integration tests in staging" or "we deploy together," contracts are missing.

**What I look at first:**
- The dependency graph. Which services call which? Every arrow in the graph needs a contract.
- The deployment cadence. Services deploying independently without contract verification are playing roulette with compatibility.
- The schema evolution strategy. How are breaking changes handled? Versioning? Deprecation periods? If there's no strategy, contracts are either absent or ignored.
- The mock fidelity. If consumer tests mock provider responses, how do the mocks stay in sync with reality? If the answer is "developers update them manually," drift is guaranteed.

**What triggers my suspicion:**
- Services that deploy together on the same schedule. This suggests tight coupling and that independent deployment has been abandoned because contracts don't exist.
- Integration environment queues. "We can't test because staging is being used by another team." This is the symptom that contract tests would cure.
- "It worked in dev" as a common incident root cause. The dev environment mocks/stubs hid a contract mismatch.
- API versioning that's inconsistent or absent. Consumers don't know which version they're targeting; providers don't know which versions are still in use.
- No Pact broker, no schema registry, no shared contract artifacts. If contracts aren't stored somewhere accessible to both sides, they don't exist.

**My internal scoring process:**
I map every inter-service interaction and classify it: has consumer contract, has provider contract, has both, has neither. The score is the percentage of interactions with bilateral contract coverage. Anything below 80% in a microservices architecture is a ticking time bomb.

---

## §3 The audit

### Contract coverage
- Is every inter-service interaction covered by a contract? (HTTP APIs, message queues, events, shared databases — all are integration points.)
- Are contracts consumer-driven? (Consumer specifies what it needs, not what the provider offers. This prevents testing against fields the consumer doesn't actually use.)
- Are contracts tested on BOTH sides? (Consumer verifies against the contract, AND provider verifies it satisfies the contract.)
- Are asynchronous interactions (events, messages) covered? (Contract testing often focuses on HTTP and ignores message queues, event buses, and webhooks.)
- Are shared database interactions covered? (If Service A reads from Service B's database, the schema IS the contract — is it tested?)

### Contract infrastructure
- Is a Pact broker or equivalent in use? (Contracts need to be stored, versioned, and accessible to both parties.)
- Can contracts be verified in CI without spinning up other services? (The entire point is avoiding the integration environment dependency.)
- Are contract versions tracked? (Which version of the consumer expects which version of the contract?)
- Can new contracts be introduced without blocking existing deployments? (Additive contracts should be non-breaking.)
- Is the "can I deploy?" check automated? (Given the latest contract verification results, is there a gate that prevents deploying an incompatible version?)

### Contract maintenance
- Are contracts updated when APIs change? (Stale contracts are worse than no contracts — they provide false confidence.)
- Is there a process for breaking changes? (Consumer notified, deprecation period, migration path.)
- Are unused contracts cleaned up? (If a consumer no longer exists, its contracts should be removed from the provider's verification suite.)
- Do contracts test meaningful interactions, not just schema? (A contract that only verifies response shape but not response content is a schema test, not a behavior contract.)
- Are contracts reviewed as part of code review? (A PR that changes an API response should also update the contract.)

### Consumer-side verification
- Do consumer tests run against the contract (not against mocks written by hand)?
- If mocks are generated from contracts, is the generation automated? (Manual mock updates = eventual drift.)
- Are consumer tests testing real interaction patterns? (Not hypothetical requests that the consumer never actually makes.)
- Do consumer contracts reflect actual production traffic patterns? (A contract for a field that's never requested is dead weight.)

### Provider-side verification
- Does the provider verify ALL consumer contracts in its CI? (Not just its own test suite — every consumer's expectations.)
- Can the provider see which consumers depend on which fields? (This informs safe deprecation.)
- Does the provider's contract verification use realistic state setup? (Provider states/fixtures for contract verification should reflect real data, not minimal stubs.)
- Are provider contract tests fast enough to run on every commit? (If verification takes too long, it gets pushed to nightly, and incompatible code ships during the day.)

---

## §4 Pattern library

**The mock drift catastrophe** — Consumer A mocks Provider B's response: `{ userId: 123, name: "Alice" }`. Provider B renames `userId` to `user_id` in a refactor. Consumer A's tests still pass against its own mock. Provider B's tests pass because it doesn't have consumer contracts. Both deploy. Consumer A crashes in production on undefined `userId`. Contract testing would have caught this the moment Provider B changed the field name.

**The shared staging bottleneck** — Five teams share one staging environment. Team 1 breaks staging on Monday; teams 2-5 can't test until Thursday. Each team deploys once a week instead of daily. Contract tests eliminate the shared environment dependency — each service verifies its contracts independently.

**The event schema ghost** — Microservices communicate via events on Kafka. Service A publishes `OrderCreated` events. Service B consumes them. Service A adds a required field to `OrderCreated`. Service B doesn't know. Service B crashes on the new field validation. Nobody thought to test event contracts because Pact was "only for HTTP."

**The version matrix explosion** — Service A v2.1 works with Service B v3.0 but not v3.1. Service C v1.5 works with Service B v3.1 but not v3.0. Without contracts, the team maintains a manual compatibility matrix that's always outdated. With contracts, the compatibility matrix is computed automatically from contract verification results.

**The "optional field" trap** — Provider adds an optional field to the response. No contract breaks. Consumer starts using the optional field. Now the field is effectively required for that consumer, but the contract still says "optional." Provider removes the "optional" field. Consumer breaks. The contract never captured the consumer's actual dependency.

---

## §5 The traps

**The "we have OpenAPI specs" trap** — An OpenAPI spec is a provider-driven schema, not a consumer-driven contract. It says what the provider OFFERS, not what each consumer NEEDS. A consumer that uses 3 of 20 fields should test those 3, not validate the entire schema. Schema validation catches structural changes; contract testing catches behavioral ones.

**The "contracts are just schema validation" trap** — A contract that only validates `{ statusCode: 200, body: { type: "object" } }` is a schema test. A real contract tests: "When I request user 123, I get back a name field that's a non-empty string and an email field that matches the email format." Schema + semantics = contract.

**The "provider tests are enough" trap** — "Our provider has comprehensive tests." Great — but do those tests verify the EXACT interactions that consumers rely on? A provider test might verify response format without verifying the specific subset of fields Consumer A depends on. The consumer's expectations must be explicitly tested.

**The "too many microservices for contracts" trap** — "We have 200 services, we can't write contracts for all of them." Start with the critical path: the 10 services involved in the primary user journey. Those 10 services' contracts will prevent 80% of integration failures.

---

## §6 Blind spots and limitations

**Contract testing doesn't test system behavior.** It verifies that two services CAN communicate, not that the overall workflow WORKS. A contract-passing system can still have business logic bugs, data consistency issues, and end-to-end failures. Contract tests replace integration environment smoke tests for compatibility — not for system correctness.

**Contract testing is weaker for implicit dependencies.** If Service A depends on Service B's side effects (Service B writes to a shared cache that Service A reads), the contract testing model doesn't naturally capture this. Explicit API contracts are clean; implicit data dependencies need additional tooling.

**Contract testing assumes discoverable consumers.** In open API ecosystems (public APIs, third-party integrations), you don't know all your consumers. Provider-driven schema testing (OpenAPI, protobuf) is necessary for public APIs where consumer-driven contracts are impractical.

**Contract testing doesn't cover non-functional requirements.** Latency, throughput, error rates, timeout behavior — these are inter-service concerns that contracts don't address. A contract says "this field will be present." It doesn't say "the response will arrive in under 200ms."

**Version management complexity grows with consumers.** With 20 consumers each at different versions, the provider's contract verification matrix becomes complex. A Pact broker with "can I deploy" checks manages this complexity, but it's a non-trivial infrastructure investment.

---

## §7 Cross-framework connections

| Framework | Interaction with Contract Testing |
|-----------|-----------------------------------|
| **Test Pyramid** | Contract tests fill the hollow middle of the pyramid by providing integration confidence at near-unit speed. The mechanism: without contracts, the gap between per-service unit tests and cross-service e2e tests is bridged only by shared staging environments (slow, flaky, contended). Each new service interaction requires another e2e test, further inverting the pyramid. Contract tests run independently per service at integration-test speed (seconds, not minutes), providing middle-layer confidence without the shared environment that makes e2e tests expensive. They reshape the pyramid by replacing heavyweight e2e tests with lightweight bilateral verification. |
| **Error Scenario Simulation** | Contracts should define error responses with the same precision as success responses. The mechanism: a contract that only specifies "200 returns {name, email}" leaves error handling unverified. When the provider changes its 404 response from `{error: "not found"}` to `{message: "resource not found", code: "NOT_FOUND"}`, the consumer's error parser breaks silently. Error contracts make error format changes a detectable contract violation, preventing the most dangerous class of integration bug — the error path that was never specified and therefore never tested on either side. |
| **Happy/Sad Path** | Contracts tend to cover happy paths only because contract authoring follows the same psychological pattern as test writing — developers specify what should work, not what should fail. The mechanism: a contract for `GET /users/123` typically specifies "returns user data." But what does `GET /users/999999` return? What does an expired auth token produce? Each unanswered question is a sad path contract that exists in production but not in verification. Adding error contracts systematically (404, 401, 422, 500) extends the contract surface to cover the paths where integration bugs most commonly hide. |
| **Test Data Management** | Provider state setup for contract verification requires realistic test data, and the data quality determines whether the contract test catches real integration bugs. The mechanism: a provider verifying a contract with `User(name: "test")` may pass, but a provider verifying with `User(name: "ñ日本語🎉")` reveals encoding mismatches. Contract verification fixtures should use factory-generated data that includes edge cases (long strings, unicode, special characters) to catch data handling disagreements between consumer and provider. Data quality in contract fixtures determines the contract's bug-detection power. |
| **Feature Flag Testing** | Feature flags that change API behavior create multiple contract states — the flag-on response and the flag-off response may have different schemas. The mechanism: Consumer A expects the old response format. The provider enables a flag that adds a field and changes a field type. The old contract still passes (the old fields are present), but the consumer is now receiving unexpected additional data that may break parsing. Contracts should specify behavior for each flag state, and the "can I deploy" check should verify contracts against the flag configuration of the target environment. |
| **Data Migration Testing** | Schema migrations can break API contracts by changing the shape of data that flows through the API. The mechanism: a database column rename from `user_name` to `username` changes the API response field name if the API layer maps directly from the database. Contract verification after migration catches this before deployment. Without post-migration contract verification, the migration succeeds (database is correct) but the API contract is broken (consumers receive unexpected field names). Running contract tests as a post-migration gate prevents this class of deployment failure. |
| **Smoke/Sanity Suite** | Contract tests and smoke tests serve complementary deployment verification roles — contracts verify bilateral compatibility before deployment, smoke tests verify system health after deployment. The mechanism: contracts catch "these two services cannot talk" before either deploys. Smoke tests catch "these two services are deployed but something environmental (DNS, TLS, config) prevents communication." A deployment pipeline that runs contracts pre-deploy and smoke tests post-deploy covers both compatibility (contract) and connectivity (smoke) gaps. |
| **Regression Effectiveness** | Integration bugs that escape to production often stem from exactly the gaps that contract testing prevents — response format changes, field type changes, and error format changes. The mechanism: cross-referencing escaped integration bugs with contract coverage reveals a pattern: most escapes are at the seam between services where one side changed behavior without notifying the other. Each such escape is evidence that a bilateral contract would have caught the incompatibility. Escape analysis becomes a contract coverage prioritization tool — services with the most escapes need contracts first. |


---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (blocking) |
|---------|-------------------|---------------------|---------------------|
| **Monolith** | No contracts (acceptable for internal module calls) | API to external consumers has no contract | Public API with no schema or contract |
| **2-5 microservices** | One interaction missing contract coverage | Async interactions (events) not covered | No contract infrastructure at all |
| **10+ microservices** | Some internal interactions uncovered | No automated "can I deploy" check | Services deploy independently with no contract verification |
| **Public API** | Schema not auto-generated from code | No deprecation process for field changes | Breaking changes ship without consumer notification |
| **Event-driven architecture** | Some event schemas not in registry | Event contract changes not tested by consumers | No event contract testing at all |

**Severity multipliers:**
- **Deploy frequency**: Teams deploying multiple times per day need contracts more urgently than teams deploying weekly.
- **Consumer count**: A service with 15 consumers needs bilateral contracts more than a service with 2 consumers.
- **Change frequency**: APIs that change weekly need contracts more than stable APIs that change quarterly.
- **Blast radius**: A contract violation on the authentication service affects every other service. Central services need contracts first.

---

## §9 Build Bible integration

| Bible principle | Application to Contract Testing |
|-----------------|---------------------------------|
| **§1.5 Single source of truth** | The contract IS the single source of truth for inter-service communication. Without it, truth is split between the consumer's mock and the provider's implementation, and they drift. |
| **§1.8 Prevent, don't recover** | Contracts prevent deployment of incompatible versions. The alternative — catching mismatches in staging or production — is recovery after the damage is done. |
| **§1.7 Checkpoint gates** | The "can I deploy?" check is a checkpoint gate: the deployment only proceeds if contract verification passes. No manual approval needed — the gate is automated. |
| **§6.5 Multiple sources of truth** | A hand-written mock and the real API are two sources of truth about the same interaction. Contract testing collapses them into one: the contract. |
| **§1.12 Observe everything** | Contract verification results should be visible: which contracts pass, which fail, which are pending. A dashboard showing contract health across all services is essential observability. |
| **§1.4 Simplicity** | Contract testing simplifies integration testing. Instead of maintaining complex staging environments, verify contracts independently per service. The testing infrastructure becomes simpler even as the architecture grows. |
