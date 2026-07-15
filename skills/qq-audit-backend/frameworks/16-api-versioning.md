---
name: API Versioning Strategy
domain: backend
number: 16
version: 1.0.0
one-liner: Breaking change management — can you evolve the API without stranding existing clients or forcing synchronized upgrades?
---

# API versioning strategy audit

You are a backend engineer with 20 years of experience maintaining APIs that outlive the teams that built them. You've managed APIs with hundreds of clients where a single breaking change triggered months of migration work, and you've inherited APIs with no versioning strategy where every change was a gamble. Your job is to find the places where API evolution will break clients or stall development.

---

## §1 The framework

API versioning is the discipline of managing change in an API's contract over time. The strategies:

- **URL path versioning** (`/v1/users`, `/v2/users`): Most visible to clients. Easy to route. Creates distinct API "editions." Used by Stripe, GitHub, Google.
- **Header versioning** (`Accept: application/vnd.api+json; version=2`): Cleaner URLs. Harder for clients to discover. Used by GitHub (alongside URL) and some enterprise APIs.
- **Query parameter versioning** (`/users?version=2`): Easy to implement. Considered less RESTful. Rarely recommended but occasionally used.
- **Content negotiation** (`Accept: application/vnd.company.v2+json`): Fine-grained per-resource versioning. Complex client implementation.
- **Date-based versioning** (`Stripe-Version: 2024-01-15`): Client pins to a date, gets behavior as of that date. Powerful for incremental evolution.
- **No versioning** (additive-only changes): Never break the contract. Only add, never remove. Works for simple APIs; breaks down under pressure.

What constitutes a breaking change:
- Removing a field from a response
- Changing a field's type
- Renaming a field
- Making an optional field required
- Changing the meaning of a value
- Removing an endpoint
- Changing error response format
- Tightening validation rules

---

## §2 The expert's mental model

When I audit versioning, I think about the day the team needs to make a breaking change. If there's no versioning strategy in place, that day is a crisis. If there's a strategy, it's routine.

**What I look at first:**
- Is there ANY versioning strategy? Many APIs have none — they've never made a breaking change (or they have, and didn't realize it).
- The deprecation process. When a version is superseded, how are clients informed? What's the timeline? Is there enforcement?
- The number of active versions. One version is simple. Two is manageable. Five concurrent versions is a maintenance nightmare.
- Whether breaking changes have actually occurred. If the API has been live for two years with no breaking changes, the versioning strategy might be untested.

**What triggers my suspicion:**
- No versioning mechanism at all. "We've never needed it." You will.
- Multiple active versions with no deprecation timeline. Each version is maintained indefinitely. The team supports code paths that nobody uses.
- Versioning applied inconsistently. Some endpoints have version prefixes, others don't. Version 1 and version 2 share some endpoints and diverge on others.
- "Internal API, we don't need versioning." Internal clients are still clients. Breaking their integrations during a deployment is still a breaking change.
- Semantic versioning on the API (v2.3.1) — SemVer is for libraries, not APIs. API versions should be simple major numbers or dates.

**My internal scoring process:**
I evaluate three dimensions: strategy clarity (is there a defined approach?), execution consistency (is it applied everywhere?), and lifecycle management (deprecation, sunset, client migration).

---

## §3 The audit

### Strategy definition
- Is there a **documented versioning strategy**?
- Does the team have a **definition of "breaking change"** that's shared and understood?
- Is the **versioning mechanism** (URL, header, date) consistently applied across all endpoints?
- Is the **default version** defined? (What happens when a client doesn't specify a version?)
- Are **non-breaking changes** (adding optional fields, adding endpoints) deployed without version bumps?

### Breaking change detection
- Is there **automated breaking-change detection** in the CI pipeline? (OpenAPI diff, schema comparison tools.)
- Can the team **distinguish** breaking changes from non-breaking changes before deployment?
- Are there **integration tests** from the client's perspective that would catch a breaking change?
- Is there a **changelog** for API changes that clients can subscribe to?

### Deprecation and sunset
- Is there a **deprecation process** for old versions? (Announcement → deprecation period → sunset.)
- Are **deprecated versions** marked in the API (response headers, documentation)?
- Is there a **sunset timeline** (e.g., "deprecated versions are supported for 12 months")?
- Is **usage** of deprecated versions monitored? (How many clients are still using v1?)
- Are **sunset dates enforced**, or do deprecated versions live forever?

### Version maintenance
- How many **active versions** are maintained? (More than 2-3 concurrent versions suggests a problem.)
- Is the **code structure** designed for multi-version support? (Shared business logic with version-specific serialization, not duplicated codebases.)
- Can **bug fixes** be applied to all active versions without excessive effort?
- Is there a **migration guide** for clients upgrading between versions?

### Client communication
- Are clients **notified** of upcoming changes (email, changelog, deprecation headers)?
- Is there **documentation per version** so clients can reference their specific version's behavior?
- Are **deprecation warnings** included in API responses (`Deprecation` header, `Sunset` header)?
- Is there a **developer portal or changelog** where clients can track API evolution?

---

## §4 Pattern library

**The accidental breaking change** — A developer renames a field from `user_name` to `username` in a response. No version bump. Clients that parse `user_name` start getting `null` or errors. Fix: breaking-change detection in CI that compares the API spec before and after.

**The forever-v1** — The API launched as v1 three years ago. There's no v2 plan. Breaking changes are avoided at all costs, leading to awkward workarounds: `user_name_v2`, `new_status`, `fixed_total`. Fix: plan for versioning from the start. Workarounds accumulate into unmaintainable schemas.

**The version explosion** — Every sprint creates a new version because "we might break something." Six months in, there are 12 versions and the team maintains all of them. Fix: version on actual breaking changes only. Most changes are additive and don't require a new version.

**The internal API without versioning** — "It's internal, we control all the clients." But the mobile app is a client, and users don't update on your schedule. Or the partner integration is internal to the team but external to the deployment cycle. Fix: any client with a different deployment cycle than the API needs versioning.

**The v2 rewrite** — The team decides v2 will be a complete rewrite with a new data model, new error format, and new conventions. V1 and v2 share nothing. Maintaining both is like maintaining two separate APIs. Fix: incremental evolution. V2 should differ from v1 only where necessary.

**The deprecated-but-eternal** — V1 was deprecated two years ago with a "6-month sunset." Two years later, 30% of traffic is still on v1. Nobody enforced the sunset because "we can't break those clients." Fix: monitor usage during deprecation. Actively reach out to clients. Enforce the sunset date.

---

## §5 The traps

**The "additive only" trap** — Committing to never making breaking changes. This works until it doesn't. Eventually, you need to change a type, remove a misleading field, or restructure a response. Having no versioning strategy means that day is a crisis.

**The "just add a field" trap** — Adding `email_v2`, `status_new`, `corrected_total` to avoid breaking changes. The response becomes a museum of past decisions. Future developers can't tell which fields are current. Fix: make the breaking change in a new version and deprecate the old one.

**The header-versioning discovery trap** — Clients must know to send a version header. If they don't, they get the default (which might be the oldest or newest version, depending on the strategy). URL versioning is more discoverable.

**The "test all versions" trap** — Maintaining comprehensive tests for five concurrent versions is five times the testing work. The test suite balloons. Fix: reduce the number of concurrent versions through active deprecation and sunset enforcement.

**The backwards compatibility forever trap** — Supporting every version indefinitely because "someone might still use it." At some point, old versions must be retired. Set expectations from day one: "versions are supported for N months after deprecation."

---

## §6 Blind spots and limitations

**Versioning doesn't solve design problems.** If the API's core data model is wrong, versioning just lets you be wrong at different URLs. Fix the underlying design; use versioning to manage the transition.

**Behavioral changes are invisible to schema versioning.** If the API starts returning results in a different order, or changes the semantics of a filter parameter, the schema hasn't changed but the behavior has. These are "dark" breaking changes that schema diffing can't detect.

**Webhook and event versioning is separate from API versioning.** If the API is v2 but webhooks still send v1 payloads, clients on v2 get inconsistent data formats. Version webhooks alongside the API.

**Client-side version management is a burden.** Every version the API supports is a version clients must be aware of. Minimizing concurrent versions reduces the cognitive load on both sides.

---

## §7 Cross-framework connections

| Framework | Interaction with API versioning |
|-----------|-------------------------------|
| **RESTful Design** | URL structure directly affects versioning strategy. `/v1/users` is a URL design decision. |
| **API Schema Validation** | Schema diffing between versions is how you detect breaking changes. Without schemas, versioning is guesswork. |
| **Error Handling Taxonomy** | Changing the error format IS a breaking change. Error format versioning must be aligned with API versioning. |
| **Webhook/Event Architecture** | Event payloads need versioning alongside API responses. Clients consuming v2 API shouldn't receive v1 events. |
| **Pagination** | Changing pagination strategy (offset to cursor) is a breaking change that versioning must manage. |
| **Auth Architecture** | Auth mechanism changes (API key to OAuth) may need to be versioned or managed with a migration path. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (client breakage) |
|---------|-------------------|---------------------|----------------------------|
| **Internal API (one client)** | No formal versioning strategy | Undocumented breaking changes | Breaking change without notice |
| **Public API (many clients)** | Missing deprecation headers | No automated breaking-change detection | Breaking change deployed to production |
| **Partner API (SLA-bound)** | Verbose version documentation | No sunset timeline for deprecated versions | Version sunset without migration support |
| **Mobile app backend** | Minor version inconsistencies | No version pinning for mobile clients | Breaking change that crashes old app versions |
| **Microservice mesh** | Internal version inconsistencies | No contract testing between services | Service deploys breaking change without checking consumers |

**Severity multipliers:**
- **Client count**: More clients = higher cost of any breaking change.
- **Client update speed**: Mobile apps and IoT devices update slowly. Breaking changes for slow-updating clients are more severe.
- **Contractual obligations**: If the API has an SLA that includes stability guarantees, unversioned changes may violate the contract.
- **Ecosystem maturity**: A new API with beta clients can be more aggressive with changes than a mature API with paying customers.

---

## §9 Build Bible integration

| Bible principle | Application to API versioning |
|-----------------|-------------------------------|
| **§1.5 Single source of truth** | The API spec for each version is the source of truth for that version's behavior. When code and spec disagree, the spec wins. |
| **§1.8 Prevent, don't recover** | Automated breaking-change detection in CI prevents accidental breakage. Discovering a breaking change from a client's bug report is recovery. |
| **§1.7 Checkpoint gates** | Deprecation → sunset is a checkpoint gate. "Version v1 will be sunset on DATE. Gate: client usage below THRESHOLD." |
| **§1.10 Document when fresh** | Document the migration path between versions when you create the new version, not when clients start asking how to upgrade. |
| **§6.10 Unenforceable punchlist** | A "clients should migrate to v2" announcement without monitoring, reminders, or enforcement deadlines is an unenforceable punchlist. |
| **§1.6 Config-driven** | Version routing (which version serves which clients) should be configuration, not hardcoded routing rules. |
