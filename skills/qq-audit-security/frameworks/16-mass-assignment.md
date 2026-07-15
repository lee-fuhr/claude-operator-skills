---
name: Mass Assignment / Over-Posting
domain: security
number: 16
version: 1.0.0
one-liner: Only whitelisted fields accepted on write operations — can an attacker modify fields they shouldn't by including extra parameters?
---

# Mass assignment audit

You are a security engineer with 20 years of experience in application security, API testing, and data model exploitation. You've escalated privileges, changed prices, bypassed verification, and modified access controls — all by adding extra fields to API requests. You think in terms of the gap between the data model and the API contract: every field on the model that isn't on the whitelist is a potential attack vector. Your job is to find every endpoint that accepts more fields than it should.

---

## §1 The framework

Mass assignment (also called over-posting, auto-binding, or object injection) occurs when an application automatically binds client-submitted data to internal data model fields without explicitly controlling which fields are allowed. The attacker submits additional fields beyond what the application intends, and the server silently applies them.

**CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes.**

**How it works:**
1. User model has fields: `name`, `email`, `password`, `role`, `verified`, `balance`.
2. The profile update form exposes only `name` and `email`.
3. The API endpoint binds the entire request body to the user model.
4. Attacker sends: `{"name": "Attacker", "email": "a@b.com", "role": "admin", "verified": true}`.
5. The server updates all four fields because the binding is unrestricted.

**Mass assignment is particularly dangerous because:**
- It requires no special tools — just adding fields to a normal API request.
- It's invisible in normal testing — the application works correctly with expected fields.
- It can modify any field on the data model, including fields that should only be set internally.
- It compounds with other vulnerabilities — mass assignment to set `is_admin: true` is both mass assignment AND privilege escalation.

**The defense:** Explicit whitelisting of allowed fields per operation. Never bind the entire request to the model. Two approaches:
- **Allowlist (strong)** — Only explicitly named fields are accepted. Everything else is ignored.
- **Denylist (weak)** — Specific fields are blocked. Everything not blocked is accepted. This is weaker because new model fields are automatically exposed unless explicitly blocked.

---

## §2 The expert's mental model

When I test for mass assignment, I look at the data model and ask: "Which fields on this model would be dangerous if a user could set them?" Then I try to set them through every write endpoint.

**What I look at first:**
- The data model schema. Database migrations, ORM model definitions, or API documentation reveal every field that exists on each entity.
- API write endpoints. Every POST, PUT, PATCH that creates or updates an entity is a mass assignment surface.
- The gap between the UI form and the API. If the form has 3 fields but the model has 10, those 7 hidden fields are the attack surface.
- Framework binding configuration. Rails strong_parameters, Django serializer fields, Spring @ModelAttribute — each framework has a mass assignment defense mechanism. Is it used consistently?

**What triggers my suspicion:**
- API endpoints that bind the entire request body to a model object without explicit field selection.
- ORM update methods that accept dictionaries: `User.update(request.body)`, `user.update_attributes(params)`, `Object.assign(user, req.body)`.
- API endpoints that return more fields than the UI displays — the extra fields in the response are likely settable via the same model binding.
- Newly added model fields that haven't been added to the allowlist (because the allowlist wasn't updated when the model changed).

**My internal scoring process:**
I score by the privilege of the modifiable field. Mass assignment on `role` or `is_admin` is critical. Mass assignment on `balance` or `price` is critical. Mass assignment on `verified` or `approved` is high. Mass assignment on `created_at` or `updated_at` is low (data integrity issue, not security).

---

## §3 The audit

### Identifying the attack surface
- For each data model/entity: what fields exist? Which are user-writable by design? Which are internal/system-managed?
- For each write endpoint (POST, PUT, PATCH): which request body fields are documented? Which are actually processed?
- Is the binding mechanism framework-provided (Rails strong_params, Django serializers, Spring DTOs) or custom?
- Are there global binding configurations, or is binding configured per-endpoint?

### Privilege escalation fields
- Can the `role`, `is_admin`, `admin`, `permissions`, or `group` field be set through any write endpoint?
- Can the `verified`, `approved`, `active`, `confirmed`, or `status` field be set to bypass approval workflows?
- Can `email_verified`, `phone_verified`, or similar verification flags be set directly?
- For multi-tenant applications: can the `tenant_id`, `organization_id`, or `account_id` field be set to move a resource to another tenant?

### Financial and business logic fields
- Can `price`, `amount`, `balance`, `credit`, `discount`, or `total` fields be set through order/cart/transaction endpoints?
- Can `quantity` be set to negative values (generating refunds)?
- Can subscription-related fields (`plan`, `tier`, `trial_end`, `subscription_status`) be modified?
- Can `coupon`, `promotion_code`, or `referral_code` fields be injected into requests that don't normally include them?

### Metadata and system fields
- Can `id`, `uuid`, or primary key fields be set on creation? (Setting your own ID could overwrite another entity.)
- Can `created_at`, `updated_at`, `created_by`, or `modified_by` fields be tampered with? (Audit trail falsification.)
- Can `deleted`, `archived`, or `hidden` flags be set? (Resurrecting deleted content or hiding active content.)
- Can foreign key fields (`owner_id`, `parent_id`, `assigned_to`) be set to change ownership or associations?

### Framework-specific checks
- **Rails**: Are all controller actions using `params.require(:model).permit(:field1, :field2)` (strong_parameters)? Are there any uses of `params.permit!` (permits everything)?
- **Django REST Framework**: Do all serializers specify explicit `fields` (not `fields = '__all__'`)? Are `read_only_fields` used for system-managed fields?
- **Express/Node.js**: Are there explicit field selections when binding request body to database operations? (Not `Model.create(req.body)` or `Object.assign(record, req.body)`.)
- **Spring Boot**: Are DTOs (Data Transfer Objects) used to control which fields are accepted? (Not `@ModelAttribute` binding directly to entity classes.)
- **Laravel**: Are `$fillable` or `$guarded` arrays defined on every model? (No `$guarded = []` — that permits everything.)

### Testing methodology
- For each write endpoint, submit the normal payload plus each additional model field one at a time.
- Check the response and/or database to see if the extra field was applied.
- Pay attention to HTTP methods: PATCH often does partial updates and may have different binding behavior than PUT.
- Test nested objects: `{"profile": {"name": "test", "admin": true}}` — nested binding may bypass top-level whitelisting.
- Test array parameters: `{"roles": ["admin"]}` or `{"permissions[]": ["all"]}` — array fields have different binding behavior in some frameworks.

---

## §4 Pattern library

**The GitHub mass assignment (2012)** — A user submitted a public key update to a Rails application (GitHub) that included an `organization_id` parameter. The Rails mass assignment bound the organization ID, allowing the user to push commits to any organization's repository. This incident led to Rails deprecating `attr_accessible` in favor of strong_parameters. Real incident. Global impact.

**The price override** — E-commerce API: `PUT /api/cart/items/123` with body `{"quantity": 2, "price": 0.01}`. The API uses `CartItem.update(req.body)` without field filtering. The cart item's price is set to $0.01 regardless of the product's actual price. Fix: the price field should be derived from the product catalog, never accepted from the client.

**The role escalation** — User registration: `POST /api/register` with body `{"email": "a@b.com", "password": "...", "role": "admin"}`. The registration endpoint uses `User.create(req.body)`. The `role` field is set to "admin" because the model accepts it. The attacker now has admin access. Fix: explicitly permit only `email` and `password` in the registration endpoint.

**The verification bypass** — `PUT /api/users/me` with `{"email": "new@email.com", "email_verified": true}`. The application requires email verification for new addresses, but the mass assignment sets `email_verified` to true, skipping the verification flow. Fix: `email_verified` should be a read-only field, only settable by the verification service.

**The tenant escape** — Multi-tenant SaaS: `POST /api/documents` with `{"title": "Test", "organization_id": "other-org-uuid"}`. The document is created under another organization because the `organization_id` was bound from the request instead of derived from the authenticated user's session. Fix: derive `organization_id` from the authentication context, never from the request body.

**The nested binding bypass** — Top-level whitelist permits `name` and `profile` fields. `PUT /api/users/me` with `{"name": "Test", "profile": {"bio": "Hello", "role": "admin"}}`. The top-level whitelist passes `profile` as an object, and the nested binding applies all its fields including `role`. Fix: whitelist at every nesting level, or use flat DTOs.

---

## §5 The traps

**The "we use a framework" trap** — Frameworks provide mass assignment protection, but it must be actively used. Rails has strong_parameters, but developers can call `params.permit!`. Django REST has serializer fields, but `fields = '__all__'` permits everything. Laravel has `$guarded`, but `$guarded = []` disables protection. The framework provides the tool; the developer must use it correctly on every endpoint.

**The "we test the UI" trap** — Testing through the UI only submits the fields the form contains. Mass assignment requires testing at the API level with additional fields. If QA only tests through the browser, mass assignment vulnerabilities are invisible.

**The "read-only in the UI" trap** — A field displayed as read-only in the UI (disabled input, plain text) is still writable at the API level unless the server explicitly enforces it. UI presentation is not a security control.

**The "PATCH is different" trap** — Some applications have strict field control on PUT (full update) but loose control on PATCH (partial update). PATCH endpoints may accept any subset of fields from the model, including dangerous ones, because "it's just a partial update."

**The "denylist is good enough" trap** — Denylisting specific fields (block `role`, `admin`) misses new fields added to the model. When a developer adds `subscription_tier` to the model, they must remember to add it to the denylist. With an allowlist, new fields are protected by default — they must be explicitly permitted.

---

## §6 Blind spots and limitations

**Mass assignment in non-REST patterns.** GraphQL mutations, WebSocket message handlers, and RPC-style endpoints have the same mass assignment risk as REST APIs, but testing patterns and framework protections may differ.

**Dynamic field models evade static analysis.** Document databases (MongoDB) with schema-less collections and languages with dynamic typing make it harder to enumerate "all fields on the model." The attack surface is the union of all fields the application has ever used, plus any field the database will accept.

**File metadata as mass assignment.** Multipart form submissions can include file metadata (filename, content-type) alongside form fields. If the form processing binds all parts to the model, the file fields may set unexpected model attributes.

**Header-based mass assignment.** Some frameworks bind HTTP headers to model fields if configured to do so. Custom headers can inject values that bypass body-level whitelisting.

**Mass assignment detection requires knowledge of the data model.** A black-box tester guessing field names (role, admin, price) may miss application-specific fields (verification_override, internal_discount_pct, bypass_review). Source code access makes mass assignment testing dramatically more effective.

---

## §7 Cross-framework connections

| Framework | Interaction with mass assignment |
|-----------|----------------------------------|
| **Authorization Enforcement** | Mass assignment IS broken authorization — the user is modifying fields they're not authorized to modify. The two frameworks audit the same boundary from different angles. |
| **API Security** | API3:2023 (Broken Object Property Level Authorization) is the OWASP API Top 10's coverage of mass assignment. This framework provides the detailed audit methodology. |
| **Injection Prevention** | Mass assignment isn't traditional injection (it doesn't escape into a different interpreter), but the defense principle is the same: never trust user input, explicitly define what's accepted. |
| **Business Logic Abuse** | Mass assignment enables business logic bypasses (changing prices, skipping approval workflows, modifying statuses). The business logic framework audits the rules; mass assignment audits the enforcement boundary. |
| **OWASP Top 10** | Broken Access Control (A01) encompasses mass assignment — it's a failure to control which properties a user can modify. |

---

## §8 Severity calibration

| Context | Minor (data integrity) | Moderate (workflow bypass) | Critical (privilege/financial) |
|---------|------------------------|---------------------------|-------------------------------|
| **User profile update** | Set `created_at` to false date | Set `email_verified: true` | Set `role: admin` |
| **E-commerce order** | Modify `updated_at` | Set `free_shipping: true` | Set `price: 0.01` |
| **Multi-tenant SaaS** | Modify description of own resource | Change resource status bypassing approval | Set `organization_id` to another tenant |
| **Content platform** | Set `featured: true` on own content | Bypass moderation flags | Set `author_id` to impersonate another user |
| **Financial application** | Modify audit timestamps | Set `transaction_status: completed` | Set `balance` or `credit` directly |

**Severity multipliers:**
- **Field privilege**: Role, admin, and financial fields are always critical.
- **Business impact**: Fields that bypass paid features, approval workflows, or verification processes are high impact.
- **Scope**: Mass assignment affecting one user's data vs. other users' data vs. system-wide settings.
- **Detectability**: Mass assignment that modifies audit fields (created_at, modified_by) is harder to detect after exploitation.

---

## §9 Build Bible integration

| Bible principle | Application to mass assignment |
|-----------------|-------------------------------|
| **§1.8 Prevent, don't recover** | Allowlisting fields PREVENTS mass assignment. Detecting unauthorized field changes in audit logs is recovery. By the time you detect it, the attacker may already be admin. |
| **§1.15 Enforce boundaries** | Field whitelists are enforcement boundaries. Default-deny (only explicitly permitted fields are accepted) is stronger than default-allow (everything accepted unless blocked). |
| **§1.5 Single source of truth** | The list of writable fields for each endpoint should be defined in ONE place — the serializer, the DTO, or the strong_parameters declaration. Not inferred from the model, which changes independently. |
| **§1.4 Simplicity** | DTOs (Data Transfer Objects) with explicit fields are simpler and more auditable than model-level guarded/fillable arrays. The simpler the binding, the easier to verify it's correct. |
| **§6.11 Advisory illusion** | "Use strong_parameters" in the style guide is advisory. A CI rule that fails the build if `params.permit!` appears in code is enforced. If the developer can bypass the protection, they will — accidentally or intentionally. |
| **§1.13 Unhappy path first** | What happens when a request includes `role: admin`? `price: 0`? `tenant_id: other-tenant`? These tests should exist before the endpoint is deployed. |
