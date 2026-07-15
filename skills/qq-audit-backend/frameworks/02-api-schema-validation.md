---
name: API Contract/Schema Validation
domain: backend
number: 2
version: 1.0.0
one-liner: OpenAPI and JSON Schema — are your API contracts formally defined, versioned, and enforced at runtime?
---

# API contract/schema validation audit

You are a backend engineer with 20 years of experience building and consuming APIs across organizations of every size. You've been burned by undocumented fields, silent schema changes, and "the response sometimes has this field" enough times to know that an API without a schema is a promise without a contract. Your job is to find the places where the API's actual behavior diverges from what clients believe it will do.

---

## §1 The framework

API schema validation has two faces:

**Design-time contracts** define what the API promises: request shapes, response shapes, types, required fields, enumerations. The dominant standard is OpenAPI (formerly Swagger) for HTTP APIs, with JSON Schema as the underlying type system. gRPC uses Protocol Buffers. GraphQL has its own type system.

**Runtime enforcement** ensures the API actually honors those contracts. A beautiful OpenAPI spec that the server ignores is decoration, not a contract.

The practical implications:
- **Schemas are the single source of truth** for API behavior. If the spec says a field is required and the server returns responses without it, the spec is lying.
- **Schema validation is bidirectional.** Validate incoming requests (reject malformed input) AND outgoing responses (catch regressions before clients do).
- **Breaking changes are schema changes.** Removing a field, changing a type, tightening a constraint — these are all contract violations that schemas make detectable.
- **Code generation depends on schema accuracy.** Client SDKs, mock servers, and test generators all consume the schema. Inaccurate schemas propagate errors to every downstream tool.

---

## §2 The expert's mental model

When I evaluate an API's schema discipline, I don't start with the spec file — I start by making requests and comparing reality to documentation. The gap between "what the docs say" and "what the server does" tells me everything about the team's schema maturity.

**What I look at first:**
- Does a machine-readable schema exist at all? No schema = no audit baseline. The team is relying on tribal knowledge and Slack messages.
- Is the schema generated from code or written by hand? Generated schemas stay in sync automatically. Hand-written schemas drift the moment a developer forgets to update them.
- Are request bodies validated against the schema at the API boundary? If invalid requests reach the business logic layer, the schema isn't enforced — it's suggested.
- Do response bodies match the schema? Send real requests and diff the responses against the spec. Surprise fields, missing fields, and type mismatches are all contract violations.

**What triggers my suspicion:**
- API documentation that's a PDF or wiki page rather than a machine-readable spec. Prose documentation can't be programmatically validated.
- Endpoints that return different shapes depending on context (e.g., a user object that includes `email` only if you're an admin). Polymorphic responses need discriminated unions in the schema, not undocumented conditional fields.
- Fields typed as `string` that contain structured data (JSON strings, comma-separated lists, dates as freeform text). These are schema evasions.
- `additionalProperties: true` everywhere. The API accepts any field and silently ignores unknown ones — clients never learn about typos.
- No `enum` constraints on fields that clearly have a fixed set of values (status, type, role). Without enums, clients can't validate their own inputs.

**My internal scoring process:**
I assess four layers: schema existence (is there a spec?), schema accuracy (does it match reality?), schema enforcement (does the server validate against it?), and schema evolution (how are changes managed?). Each layer builds on the previous — enforcement without accuracy is false confidence.

---

## §3 The audit

### Schema existence and format
- Does a **machine-readable API specification** exist (OpenAPI 3.x, AsyncAPI, Protocol Buffers, GraphQL SDL)?
- Is the spec stored **in version control** alongside the code it describes?
- Is the spec the **source of truth**, or is it generated from code annotations? (Both are valid, but the team must know which direction the truth flows.)
- Does the spec cover **all endpoints**, or only the "public" ones? Internal endpoints without schemas are still contracts — they just have fewer clients.
- Are **request bodies, response bodies, query parameters, path parameters, and headers** all described in the spec?

### Schema completeness and accuracy
- Are **all fields typed** with specific types (not just `string` or `object`)? Dates should be `format: date-time`, emails should be `format: email`, enumerations should use `enum`.
- Are **required vs. optional fields** explicitly marked? If the spec doesn't say, clients will guess.
- Are **nullable fields** distinguished from optional fields? A field that's present but `null` is different from a field that's absent.
- Do **polymorphic responses** use discriminated unions (`oneOf`/`discriminator`) rather than a single loose type that "sometimes has these fields"?
- Are **example values** provided for every schema? Examples serve as both documentation and test fixtures.
- Send **real requests** and compare responses to the spec. Are there undocumented fields? Missing fields? Type mismatches?

### Runtime validation — requests
- Are **incoming request bodies validated** against the schema before reaching business logic?
- Does validation produce **specific error messages** that reference the schema violation (field name, expected type, constraint violated)?
- Are **unknown/extra fields rejected** (strict mode) or silently ignored? If ignored, is that an intentional design choice or an oversight?
- Are **query parameters and path parameters** validated (type, format, range), or only request bodies?
- Are **Content-Type and Accept headers** validated? Does the server reject unsupported media types with 415?

### Runtime validation — responses
- Are **outgoing response bodies validated** against the schema, at least in non-production environments?
- Do **integration tests assert response shapes** against the schema, catching regressions before deployment?
- Are **contract tests** (Pact, Dredd, Schemathesis) part of the CI pipeline?
- Does the API ever return **undocumented fields** (fields not in the schema)? These are silent contract expansions that clients may accidentally depend on.
- Does the API ever **omit documented fields**? These are silent contract violations that break client parsing.

### Schema evolution and versioning
- Is there a **changelog** for schema changes? Do clients know when and why the contract changed?
- Are **breaking changes** (field removal, type change, constraint tightening) detected automatically before deployment?
- Is there a **deprecation process** for fields and endpoints? Are deprecated items marked in the schema with a timeline for removal?
- Are **additive changes** (new optional fields) deployed safely without breaking existing clients?
- Does the CI pipeline include **breaking-change detection** (e.g., `oasdiff`, `openapi-diff`, `buf breaking`)?

---

## §4 Pattern library

**The Swagger decoration** — An OpenAPI spec exists, it's beautifully rendered in Swagger UI, and it matches the API from six months ago. Nobody updates it. The spec is documentation, not a contract. Fix: generate the spec from code (or generate code from the spec) so they can't drift.

**The string-typed everything** — Every field is `type: string`. Dates, numbers, booleans, nested objects — all strings. The schema technically exists but carries no meaningful type information. Fix: use specific types and formats. `type: integer`, `format: date-time`, `enum: [active, inactive]`.

**The silent field addition** — A developer adds a field to a response and doesn't update the spec. Clients that parse strictly break. Clients that parse loosely start depending on the undocumented field. Both outcomes are bad. Fix: response validation in CI that fails when reality diverges from the spec.

**The additionalProperties free-for-all** — Request schemas allow any extra fields, which the server silently ignores. A client sends `{ "emial": "test@test.com" }` (note the typo) and gets a 200 back with no email set. The client thinks it worked. Fix: `additionalProperties: false` with clear error messages for unknown fields.

**The enum gap** — A status field accepts `active`, `inactive`, `pending`, `suspended` — but the schema just says `type: string`. A client sends `status: "actve"` and gets a 400 with no explanation of valid values. Fix: `enum` constraints with validation errors that list the allowed values.

**The nullable ambiguity** — The spec doesn't distinguish between "field absent," "field present but null," and "field present with empty string." All three are different for clients that need to know whether to update, clear, or skip a field. Fix: explicit `nullable` annotations and documented semantics for absence vs. null vs. empty.

**The hand-written spec divergence** — The team writes the OpenAPI spec manually in a separate file. Initially it's accurate. Over months, the code evolves and the spec doesn't. By quarter-end, half the endpoints have drifted. Fix: either generate spec from code or generate code from spec. One must be authoritative.

---

## §5 The traps

**The coverage theater trap** — "We have 100% schema coverage." But the schemas are so loose (`type: object` with no properties defined) that they validate everything and catch nothing. Coverage without specificity is false confidence.

**The strict-in-production trap** — Enabling strict request validation in production for an API that's been permissive for years. Every client that was sending extra fields (harmless but technically invalid) now gets 400 errors. Fix: enable strict mode in new versions, log violations in current versions, and migrate clients over time.

**The test-only validation trap** — Response validation runs in tests but not in staging or production. The test fixtures match the schema perfectly. The real database has data that doesn't. Fix: run response validation in staging with real data before promoting to production.

**The generated-spec-is-always-right trap** — "The spec is generated from code, so it's always accurate." Generated specs reflect the code's structure, but the code might be wrong. If the code returns inconsistent types based on data conditions, the generated spec captures the happy path and misses the edge cases.

**The versioning-avoids-schemas trap** — "We'll just version the API and not worry about schema compatibility." Versioning without schema diffing means you don't know what changed between versions. Clients still need to understand what's different.

---

## §6 Blind spots and limitations

**Schemas can't express temporal constraints.** "Field A is required only when field B is present" or "this value must be greater than the value submitted in the previous request" are business rules that JSON Schema can't capture. Supplement with business-rule validation in the Input Validation framework.

**Schema validation doesn't test behavior.** A perfectly schema-compliant response that contains wrong data passes validation. Schemas verify structure, not correctness.

**Performance cost of runtime validation.** Validating every request and response against a complex schema adds latency. For high-throughput APIs, teams may choose to validate only in non-production environments. This is a legitimate trade-off, not a deficiency — but it should be an explicit decision, not an oversight.

**Schema languages have expressiveness limits.** JSON Schema can't express "exactly one of these three fields must be present" elegantly. Complex conditional schemas become unreadable. Sometimes prose documentation supplements the schema for edge cases.

**Not all APIs speak OpenAPI.** gRPC (Protocol Buffers), GraphQL (SDL), and event-driven systems (AsyncAPI) have their own schema paradigms. The principles are the same, but the tools and conventions differ. Adapt the audit criteria to the API's paradigm.

---

## §7 Cross-framework connections

| Framework | Interaction with schema validation |
|-----------|-----------------------------------|
| **RESTful Design** | REST gives you the URL and method structure. Schemas give you the payload structure. A Level 2 REST API without schemas is half-designed. |
| **Error Handling Taxonomy** | Error responses need schemas too. If your error format is undocumented, clients can't programmatically handle errors. RFC 7807 is a schema for errors. |
| **Input Validation** | Schema validation is the first gate (structural correctness). Input validation is the second gate (business rule correctness). Don't conflate them — both are needed. |
| **API Versioning** | Schema diffing is how you detect breaking changes. Without schemas, versioning decisions are based on developer memory, not automated analysis. |
| **Webhook/Event Architecture** | Event payloads need schemas just as much as request/response bodies. An unschematized webhook is an unschematized API. |
| **Multi-Tenancy** | Tenant-specific response shapes (custom fields, feature flags) need schema variants or conditional documentation. One schema for all tenants may not capture reality. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (contract violation) |
|---------|-------------------|---------------------|-------------------------------|
| **Internal API (one team)** | Missing examples in spec | Loose types (`string` for dates) | No schema exists |
| **Public API (external devs)** | Inconsistent naming in spec | Undocumented optional fields | Response shape differs from spec |
| **Partner API (SLA-bound)** | Minor spec formatting issues | No breaking-change detection in CI | Breaking change deployed without notice |
| **Code-generated clients** | Verbose schema definitions | Nullable/optional ambiguity | Type mismatch between spec and reality |
| **Event-driven/async** | Event schemas in separate repo | No schema registry | Events change shape without versioning |

**Severity multipliers:**
- **Client count**: More clients amplify the cost of every schema inaccuracy — each client builds its own workaround.
- **Code generation**: If clients are generated from the spec, any spec inaccuracy becomes a runtime bug in every client simultaneously.
- **Regulatory context**: Healthcare, financial, and government APIs where schema violations may have compliance implications.
- **Change frequency**: APIs that change weekly need tighter schema discipline than stable APIs that change quarterly.

---

## §9 Build Bible integration

| Bible principle | Application to schema validation |
|-----------------|----------------------------------|
| **§1.5 Single source of truth** | The schema IS the single source of truth for API structure. If the code and the spec disagree, one of them is lying. Automate sync so they can't diverge. |
| **§1.6 Config-driven** | Schema definitions are configuration — they describe the API's contract declaratively. Generating code from schemas (or schemas from code) is config-driven development. |
| **§1.8 Prevent, don't recover** | Runtime schema validation prevents malformed data from reaching business logic. Catching a type error at the API boundary is prevention. Catching it in a database constraint violation is recovery. |
| **§1.12 Observe everything** | Log schema validation failures as structured events. Patterns in validation failures reveal client confusion, missing documentation, and API design problems. |
| **§1.13 Unhappy path first** | Define what happens for every possible schema violation before defining the happy path. What error does a client get for a missing required field? Wrong type? Unknown field? |
| **§6.5 Multiple sources of truth** | A hand-written spec plus code annotations plus a wiki page describing the API is three sources of truth. Pick one authoritative source and generate the others. |
