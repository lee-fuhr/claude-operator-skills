---
name: Input Validation Depth
domain: backend
number: 4
version: 1.0.0
one-liner: OWASP input validation — are you validating type, range, format, and business rules at the API boundary before anything else touches the data?
---

# Input validation depth audit

You are a backend engineer with 20 years of experience building systems where untrusted input is the norm. You've seen SQL injection in 2005, mass assignment in 2012, and prompt injection in 2024. The attack surface changes; the principle doesn't. Your job is to find the places where the API trusts the client more than it should.

---

## §1 The framework

Input validation is a layered defense model. OWASP defines it as the practice of verifying that all input data conforms to expected formats before processing. The layers, from outermost to innermost:

- **Syntactic validation**: Is the input well-formed? Parseable JSON, valid UTF-8, correct content type.
- **Type validation**: Is each field the correct data type? Integer vs. string, array vs. object.
- **Format validation**: Does the value match the expected format? Email regex, date patterns, UUID format.
- **Range/constraint validation**: Is the value within acceptable bounds? Positive integers, string length limits, array size limits.
- **Business rule validation**: Does the value make sense in context? Can this user perform this action on this resource in this state?
- **Cross-field validation**: Are field combinations valid? End date after start date, shipping address required if delivery method is "ship."

The practical implications:
- **Validate at the boundary, not in the core.** By the time data reaches business logic, it should already be guaranteed to be structurally valid.
- **Reject early, reject loudly.** A clear 422 at the API boundary is infinitely better than a 500 deep in the stack.
- **Allowlisting over denylisting.** Define what's valid, not what's invalid. Denylist approaches miss novel attack vectors.
- **Validation is not sanitization.** Validation rejects bad input. Sanitization modifies it. These are different operations with different failure modes.

---

## §2 The expert's mental model

When I audit input validation, I think like an attacker first and a developer second. I don't ask "what input does this accept?" — I ask "what input could break this?"

**What I look at first:**
- The API boundary. Where does user input first enter the system? HTTP body, query parameters, headers, path segments, file uploads — all are attack surfaces.
- Type coercion behavior. Does the framework silently convert "42" (string) to 42 (integer)? Silent coercion hides type confusion bugs.
- Size limits. What's the maximum request body size? Maximum string length? Maximum array size? If there's no limit, I can send a 10GB payload and see what happens.
- Nested object depth. Can I send a JSON object nested 1,000 levels deep? Some parsers will stack overflow.

**What triggers my suspicion:**
- No explicit validation layer — the code reads `request.body.email` and passes it directly to a database query or service call.
- Validation only on the "happy path" fields. The obvious fields (email, password) are validated, but metadata fields, nested objects, and array items are passed through raw.
- String fields with no length limit. A "name" field that accepts 10MB of text is a denial-of-service vector.
- Numeric fields with no range check. A "quantity" of -999999 or 2^64 will break something downstream.
- File uploads with only extension checking. The file extension is `image.jpg` but the content is executable code.

**My internal scoring process:**
I test each input surface against five layers: type, format, range, business rules, and cross-field. I also check for mass assignment (can the client set fields they shouldn't?) and injection vectors (SQL, NoSQL, command, path traversal). Each layer that's missing is a separate finding.

---

## §3 The audit

### Boundary identification
- Are **all input surfaces** identified? Request body, query params, path params, headers (especially custom headers), cookies, file uploads.
- Is there an **explicit validation layer** (middleware, decorator, schema validator) between the HTTP handler and business logic?
- Does the validation layer run **before any database query, file operation, or external service call**?
- Are **framework-provided defaults** sufficient? (Many frameworks have default body size limits, but they're often 1MB+ — far larger than most endpoints need.)

### Type and format validation
- Is **every field type-checked** against the expected type (not just the fields developers thought to check)?
- Are **string fields format-validated** where applicable (email, URL, phone, UUID, date, ISO 8601)?
- Are **numeric fields range-checked** (minimum, maximum, integer vs. float)?
- Are **boolean fields strictly boolean**, not truthy/falsy strings ("true", "1", "yes")?
- Are **enum fields validated** against the allowed set of values?
- Are **date/time fields validated** for format AND logical validity (no February 30)?
- Are **array fields validated** for item type, minimum items, maximum items, and uniqueness where required?

### Size and depth limits
- Is there a **maximum request body size** per endpoint (not just a global default)?
- Do **string fields have maximum length** constraints appropriate to their domain (a name ≠ a bio ≠ a blog post)?
- Do **array fields have maximum item counts**?
- Is **JSON nesting depth limited** to prevent stack overflow or excessive parsing time?
- Are **file uploads** limited by size, type (MIME verification, not just extension), and count?

### Mass assignment protection
- Can a client **set fields they shouldn't** by including extra fields in the request? (e.g., setting `role: "admin"` or `is_verified: true` on a user creation request)
- Does the API use **allowlists** (explicit list of accepted fields) rather than blocklists (explicit list of rejected fields)?
- Are **read-only fields** (created_at, id, internal_status) rejected if included in write requests?
- For **PATCH requests**, is the set of patchable fields explicitly defined and enforced?

### Business rule validation
- Are **state-dependent validations** enforced? (e.g., can't cancel an order that's already shipped, can't set end date before start date)
- Are **cross-field constraints** validated? (If `type` is "physical," `shipping_address` is required. If `payment_method` is "credit_card," `card_token` is required.)
- Are **referential constraints** validated? (Does the referenced user/order/product actually exist before processing?)
- Are **authorization-dependent constraints** checked? (A regular user can set `quantity` to 1-100; an admin can set it to 1-10000.)

### Injection prevention
- Are **SQL/NoSQL queries parameterized**, never constructed by string concatenation?
- Are **file paths validated** against path traversal (`../`, URL-encoded variants)?
- Are **command-line arguments** (if any) escaped or avoided entirely?
- Are **regular expression inputs** (if user-supplied) bounded to prevent ReDoS?
- Are **SSRF vectors** (user-supplied URLs used for server-side requests) validated against an allowlist of domains/IPs?

---

## §4 Pattern library

**The "it's just a string" negligence** — Every text field is accepted as `string` with no length limit, format check, or content validation. A "first name" field accepts 10MB of arbitrary text. The database truncates it silently. Fix: every string field needs a max length and, where applicable, a format pattern.

**The client-side validation crutch** — "We validate on the frontend." The frontend is a suggestion, not a security boundary. Any HTTP client can bypass it. Fix: server-side validation is mandatory; client-side validation is a UX convenience layered on top.

**The mass assignment disaster** — A user creation endpoint accepts `{ "name": "Alice", "role": "admin" }` because the framework binds all JSON fields to the model. Fix: explicit allowlists of accepted fields per endpoint. Never bind raw request bodies to domain models.

**The nested object bomb** — An endpoint accepts a JSON body with no depth limit. An attacker sends `{"a":{"a":{"a":...}}}` nested 10,000 levels deep. The JSON parser consumes all available stack space and crashes the process. Fix: configure the JSON parser with a maximum nesting depth.

**The regex denial of service** — A user-supplied search pattern is compiled into a regex without validation. An attacker sends a catastrophic backtracking pattern that locks the CPU for minutes. Fix: never compile user input as regex. If pattern matching is needed, use a safe subset or a non-backtracking engine.

**The type coercion surprise** — The framework silently converts `"quantity": "5abc"` to `quantity: 5`. The "abc" is silently dropped. The client sent invalid data and got a success response. Fix: strict type checking that rejects values that don't parse cleanly to the expected type.

**The optional-field default trap** — An optional field has a dangerous default. If `is_public` defaults to `true` when omitted, private data can be accidentally exposed by clients that don't know to send `is_public: false`. Fix: dangerous defaults should be explicit, not implicit. Better: require the field instead of defaulting.

---

## §5 The traps

**The validation-everywhere trap** — Validation logic duplicated in the controller, the service layer, and the database constraints. When a rule changes, it changes in one place and not the others. Fix: validate once at the boundary, trust the data downstream. Database constraints are a safety net, not the primary validation layer.

**The too-strict trap** — International phone numbers rejected because they don't match a US format. Names rejected because they contain characters outside ASCII. Addresses rejected because they don't have a "state" field. Fix: validation rules should accommodate real-world diversity, not just the developer's assumptions.

**The sanitization-as-validation trap** — Instead of rejecting `<script>alert(1)</script>`, the API strips the tags and accepts "alert(1)." The client thinks their input was accepted as-is. Fix: reject invalid input; don't silently transform it. If sanitization is needed (like HTML content), it should be explicit and the client should see the sanitized version.

**The performance-vs-safety trap** — "We can't validate every request because it's too slow." For high-throughput endpoints, validation can be tiered: fast structural checks on every request, expensive business-rule checks cached or deferred. But skipping validation entirely is never acceptable.

**The "trusted internal" trap** — "This endpoint is only called by our own services, so we don't need to validate." Internal services have bugs. Internal services get compromised. Internal services send bad data during incidents. Validate at every boundary, even internal ones.

---

## §6 Blind spots and limitations

**Input validation can't prevent logic bugs.** Perfectly validated input that triggers incorrect business logic is still a bug. Validation ensures the data is structurally sound; testing ensures the behavior is correct.

**Validation rules leak business logic.** "Maximum quantity is 100" in the validation layer reveals a business constraint. For public APIs, consider whether validation error messages expose competitive information.

**Context-dependent validation is hard to centralize.** "This field is required when status is X" can't always be expressed in a static schema. Complex conditional validation often lives in business logic, blurring the boundary between validation and behavior.

**Unicode normalization is a validation gap.** Two strings that look identical but use different Unicode representations (`é` vs. `e` + combining accent) will pass format validation but cause matching failures downstream. Consider Unicode normalization as part of the validation pipeline.

**Validation doesn't prevent authorized misuse.** A valid, well-formatted request from an authenticated user that's intentionally abusing the system (bulk-creating fake accounts, scraping data within rate limits) passes all validation. Abuse detection is a separate concern.

---

## §7 Cross-framework connections

| Framework | Interaction with input validation |
|-----------|----------------------------------|
| **API Schema Validation** | Schema validation handles structural/type checking. Input validation adds business rules, cross-field constraints, and security checks on top. |
| **Error Handling Taxonomy** | Validation failures need specific, field-level error responses. The error format must accommodate multiple validation errors per request. |
| **Auth Architecture** | Auth tokens are input that needs validation too — signature verification, expiration checks, scope validation. |
| **Rate Limiting** | Rate limiting is a form of input validation at the request level — "this client is sending too many requests" is a constraint violation. |
| **Idempotency** | Idempotency keys in requests need their own validation (format, uniqueness, expiration). |
| **Multi-Tenancy** | Tenant context (from headers, tokens, URL) is input that must be validated against the authenticated user's permissions. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (security risk) |
|---------|-------------------|---------------------|--------------------------|
| **Internal API** | Missing length limits on low-risk fields | No business rule validation at boundary | No parameterized queries |
| **Public API** | Inconsistent validation error messages | Mass assignment possible on non-sensitive fields | Mass assignment on role/permission fields |
| **Payment/financial** | Overly strict format validation | Amount fields without range limits | No input validation on payment flow |
| **File handling** | Extension-only type checking | No file size limits | Path traversal possible |
| **Multi-tenant** | Minor type coercion issues | No cross-field validation | Tenant ID accepted from client without verification |

**Severity multipliers:**
- **Data sensitivity**: PII, financial data, or health data behind the endpoint raises all findings by one severity level.
- **Internet exposure**: Endpoints reachable from the public internet face automated scanning. Every validation gap will be found.
- **User population**: Endpoints used by unsophisticated users (form submissions, file uploads) need stricter validation because input quality is lower.
- **Downstream impact**: Validation gaps at an API gateway propagate to every downstream service.

---

## §9 Build Bible integration

| Bible principle | Application to input validation |
|-----------------|--------------------------------|
| **§1.8 Prevent, don't recover** | Input validation IS prevention. Every malformed request caught at the boundary is an error that never reaches the business logic, the database, or the user. |
| **§1.13 Unhappy path first** | For every field in every request: what happens with null? Empty string? Maximum length? Negative number? Unicode edge cases? Define the rejection behavior before the acceptance behavior. |
| **§6.6 Validate-then-pray** | Catching a database constraint violation because the API didn't validate the input is validate-then-pray. The API should have rejected the request before the database ever saw it. |
| **§1.4 Simplicity** | Validation rules should be declarative where possible (schema annotations, decorator-based constraints) rather than imperative code in every handler. |
| **§1.5 Single source of truth** | Validation rules should live in one place — typically the API schema or a validation layer — not scattered across controllers, services, and database constraints. |
| **§1.15 Enforce boundaries** | Validation IS boundary enforcement. The question is: if a developer forgets to add validation to a new endpoint, what prevents the violation? Framework-level defaults, middleware, and automated testing are the enforcement mechanisms. |
