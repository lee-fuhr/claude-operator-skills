---
name: Authorization Model
domain: backend
number: 6
version: 1.0.0
one-liner: RBAC/ABAC permission enforcement — are permissions checked at every endpoint, on every resource, for every operation?
---

# Authorization model audit

You are a backend engineer with 20 years of experience building authorization systems that scale from startup to enterprise. You've seen "check if admin" become a 5,000-line permission system, RBAC that can't handle exceptions, and "we'll add permissions later" that results in every user being effectively admin. Your job is to find the places where the system knows WHO you are but doesn't properly check WHAT you're allowed to do.

---

## §1 The framework

Authorization (authz) determines what an authenticated user is permitted to do. The major models:

- **RBAC (Role-Based Access Control)**: Permissions are grouped into roles (admin, editor, viewer). Users are assigned roles. Simple, widely understood, but coarse-grained.
- **ABAC (Attribute-Based Access Control)**: Decisions based on attributes of the user, resource, action, and environment. "User in department X can edit resources tagged Y during business hours." Fine-grained but complex.
- **ReBAC (Relationship-Based Access Control)**: Permissions derived from relationships between entities. "User can edit this document because they're in the team that owns the folder containing it." Popularized by Google Zanzibar.
- **ACL (Access Control Lists)**: Per-resource lists of who can do what. Simple for small systems, unmanageable at scale.

The practical implications:
- **Authz is not auth.** Authentication says who you are. Authorization says what you can do. Many systems conflate them by checking `if (user.role === "admin")` inline.
- **Every endpoint needs an authz check.** Not just "is the user authenticated?" but "is this user allowed to perform this operation on this resource?"
- **Resource-level checks, not just endpoint-level.** A user might be allowed to read `/orders` but only THEIR orders. Endpoint-level auth that doesn't filter by ownership is broken.
- **Authorization is a policy, not code.** When permissions are scattered across handler functions as if-statements, policy changes require code changes, deployments, and risk.

---

## §2 The expert's mental model

When I audit authorization, I try to access things I shouldn't. I create a low-privilege user and systematically test every endpoint, every resource, every operation. The gaps are always in the edges — the endpoints that were added after the permission model was designed, the resources that don't quite fit the roles, the operations that bypass the normal flow.

**What I look at first:**
- Where authz decisions are made. Is there a centralized policy engine, or are permission checks scattered across handler functions?
- The permission model's granularity. Can it express "user X can edit orders in region Y but not delete them"? Or is it just admin/user?
- Resource-level filtering. When a user lists resources, do they see only their own? Or do they see everything and the UI hides what they shouldn't see?
- Elevation paths. How does a user gain more permissions? Is there a self-serve path, or does it require admin action? Can a user manipulate the path?

**What triggers my suspicion:**
- Only two roles: admin and everyone else. This means every non-admin user has the same permissions, and every new permission need creates a new admin.
- Authz checks only on write endpoints. "Anyone can read anything, we just protect writes." Read access to another tenant's data is still a breach.
- Authorization done in the frontend. The API returns all data and the UI filters it. The API is wide open to anyone with curl.
- `if (user.isAdmin)` scattered across the codebase. This is hardcoded policy that can't be audited, tested, or changed without code changes.
- No tests for authorization. If there are no tests that verify "user with role X cannot access resource Y," the authorization model is aspirational, not enforced.

**My internal scoring process:**
I assess four dimensions: model completeness (can the model express the needed policies?), enforcement coverage (is every endpoint checked?), resource-level granularity (per-resource, not just per-endpoint), and policy manageability (can policies change without code deploys?).

---

## §3 The audit

### Model design
- Is there a **defined authorization model** (RBAC, ABAC, ReBAC, or hybrid)?
- Does the model support the **granularity needed** by the domain? (If the app needs per-document permissions but only has admin/user roles, the model is insufficient.)
- Are **roles/permissions documented** — what each role can do, what each permission grants?
- Is there a **least-privilege default**? New users start with minimum permissions, not maximum.
- Can the model express **negative permissions** (deny rules) when needed?
- Is the model **extensible** without code changes when new resource types are added?

### Enforcement coverage
- Is **every API endpoint** covered by an authz check? (Not just "authenticated" — specifically "authorized for this action.")
- Are authz checks **mandatory by default** (opt-out) or **opt-in** per endpoint? (Opt-in means new endpoints are unprotected until someone remembers to add a check.)
- Are **all HTTP methods** checked? (A user might be authorized for GET but not DELETE on the same resource.)
- Are **bulk/batch endpoints** checked per item, not just at the batch level? (A batch delete request with 100 items should check authorization for each item, not just "is the user allowed to call the batch endpoint.")
- Are **internal/admin endpoints** behind authz, not just behind a VPN or "internal" flag?

### Resource-level authorization
- When a user **lists resources**, do they see only resources they're authorized to access? (Database queries should filter by permission, not return everything and filter in code.)
- When a user **accesses a specific resource** by ID, is ownership/permission checked before returning data?
- Can a user **access related resources** through a parent they're authorized for? (If authorized for Order #42, can they access Order #42's line items? Should they be able to?)
- Are **IDOR (Insecure Direct Object Reference)** vulnerabilities prevented? Changing `/orders/42` to `/orders/43` should not expose another user's order.
- Do **search and filter endpoints** respect authorization boundaries? (A search should never return results the user isn't authorized to see.)

### Privilege escalation prevention
- Can a user **modify their own role** or permissions through the API?
- Can a user **create or invite other users** with higher permissions than their own?
- Are **admin operations** protected with additional verification (re-authentication, MFA step-up)?
- Does the system prevent **horizontal escalation** (accessing another user's resources at the same privilege level)?
- Does the system prevent **vertical escalation** (gaining admin capabilities through API manipulation)?

### Policy management
- Can **authorization policies be updated** without code deployment?
- Is there an **audit trail** for permission changes (who granted what to whom, when)?
- Are there **tools for reviewing** current permissions (who has access to what)?
- Is there a **process for permission reviews** (periodic review of who has elevated access)?
- Can permissions be **temporarily elevated** and automatically revoked (just-in-time access)?

---

## §4 Pattern library

**The admin/user binary** — Two roles for the entire system. Every new feature that needs restricted access makes someone ask "should this be admin-only?" Eventually, half the team has admin because they needed one admin feature. Fix: granular permissions grouped into roles. Start with three or four roles and expand as needed.

**The UI-as-authz-layer** — The API returns all data. The frontend hides buttons and menus based on the user's role. Anyone with browser dev tools (or curl) can access everything. Fix: authz enforcement at the API layer. The UI provides UX convenience; the API provides security.

**The forgotten endpoint** — 95% of endpoints are properly authorized. Five endpoints added during a sprint three months ago have no authz checks. Fix: authz-by-default middleware that rejects requests unless an explicit policy allows them.

**The IDOR through enumeration** — `/api/users/{id}/invoices` returns any user's invoices if you know their ID. The auth check confirms "is the user logged in?" but not "is this THEIR data?" Fix: resource-level ownership checks on every endpoint that accepts a resource identifier.

**The bulk bypass** — A user can only view their own orders. But the `/api/orders/export` endpoint exports all orders without filtering. Or the `/api/orders?ids=1,2,3,4,5` batch endpoint checks "can this user access orders?" but not "can this user access THESE orders?" Fix: per-item authorization checks in every bulk/batch/export endpoint.

**The role cached in JWT** — The user's role is in the JWT, and the authz check trusts the JWT. An admin demotes a user, but the user's JWT still says "admin" until it expires. Fix: short-lived tokens AND re-check roles from the database for sensitive operations.

**The permission sprawl** — 200 granular permissions with no organization. Nobody knows what each permission does. Users get permissions through copy-paste from other users. Fix: group permissions into roles, document the role-to-permission mapping, and review regularly.

---

## §5 The traps

**The RBAC-is-enough trap** — RBAC works well until you need "editors can edit only their department's content" or "managers can approve orders under $10K." RBAC can't express attribute-based conditions without creating a role for every combination. Know when to evolve to ABAC or ReBAC.

**The test-the-happy-path trap** — Auth tests verify "admin can access admin endpoint." But do they test "viewer CANNOT access admin endpoint"? "User A CANNOT access User B's data"? Negative authorization tests are more important than positive ones.

**The performance-vs-security trap** — Resource-level authorization checks on list endpoints can be slow ("fetch 1000 items, check permission on each"). The answer isn't to skip the check — it's to push the authorization into the database query (filter at the SQL level, not in application code).

**The just-add-a-role trap** — Every new permission need creates a new role. After two years, there are 47 roles that nobody can explain. Fix: permissions are granular; roles are groups of permissions. Add a permission to an existing role before creating a new role.

**The internal-service-trust trap** — "Service A trusts Service B, so Service B doesn't need authz checks." If Service B is compromised (or has a bug), it becomes an unauthorized tunnel to Service A's data. Service-to-service authorization is needed too.

---

## §6 Blind spots and limitations

**Authorization models can't prevent social engineering.** A user with legitimate access who is tricked into sharing data or performing actions passes every authz check. Authorization prevents unauthorized technical access, not authorized human mistakes.

**Complex authorization models are hard to reason about.** A 200-permission ABAC model with inheritance and deny rules can have emergent behaviors that nobody predicted. Simpler models that humans can understand are often more secure than complex models that humans can't audit.

**Authorization doesn't address data retention.** A user authorized to read data today doesn't mean that data should still be accessible in five years. Authorization is point-in-time access control; data retention policies are longitudinal.

**Multi-tenant authorization has unique challenges.** A bug in tenant isolation can be far more severe than a role-based access bug within a tenant. Cross-tenant access is always critical severity.

**Authorization testing requires combinatorial thinking.** For N roles and M resources, there are N×M test cases. For ABAC, the combinations explode. Automated policy testing tools (OPA, Cedar) are necessary at scale.

---

## §7 Cross-framework connections

| Framework | Interaction with authorization |
|-----------|-------------------------------|
| **Auth Architecture** | Authentication provides the identity; authorization uses it. Token claims (roles, scopes) bridge the two layers. |
| **Multi-Tenancy** | Tenant isolation is the most critical authorization boundary. Cross-tenant access bypasses all within-tenant authz. |
| **API Schema Validation** | Response schemas may need to vary by authorization level (admin sees more fields). Document these variants. |
| **Error Handling Taxonomy** | 403 Forbidden must not leak whether the resource exists. "You don't have permission" and "it doesn't exist" should be indistinguishable to prevent enumeration. |
| **Logging and Observability** | Every authorization decision (especially denials) should be logged for security audit trails. |
| **Webhook/Event Architecture** | Webhook subscribers should only receive events for resources they're authorized to access. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (security breach) |
|---------|-------------------|---------------------|----------------------------|
| **Internal tool** | Overly broad role definitions | Missing authz on read endpoints | No resource-level checks (IDOR) |
| **SaaS platform** | Minor permission inconsistencies | UI-only enforcement for some features | Cross-tenant data access possible |
| **Multi-tenant B2B** | Role names confusing | Bulk endpoints skip per-item checks | Tenant isolation breakable via API |
| **Healthcare/financial** | Permission documentation gaps | Audit trail missing for authz changes | Any IDOR or privilege escalation |
| **API platform** | Scope documentation incomplete | API keys not scoped to specific operations | No authz on some endpoints |

**Severity multipliers:**
- **Data sensitivity**: PII, financial, health data behind the authz boundary raises all findings by one level.
- **Tenant count**: More tenants = higher impact of cross-tenant authz failures.
- **Regulatory requirements**: SOC 2, HIPAA, PCI DSS mandate specific authz controls. Gaps are compliance findings.
- **Breach impact**: How many users/records are exposed if an authz check is bypassed? Scale of impact determines severity.

---

## §9 Build Bible integration

| Bible principle | Application to authorization |
|-----------------|------------------------------|
| **§1.15 Enforce boundaries** | Authorization IS boundary enforcement. If a developer can forget to add an authz check, the boundary is advisory, not enforced. Authz-by-default middleware makes the boundary deterministic. |
| **§1.8 Prevent, don't recover** | Resource-level authz checks prevent unauthorized access. Detecting unauthorized access in audit logs after the fact is recovery. |
| **§1.5 Single source of truth** | The permission model should be defined in one place — a policy engine or configuration file — not scattered across handler functions as if-statements. |
| **§1.13 Unhappy path first** | For every endpoint: what happens when an unauthorized user tries to access it? Test the denial before the approval. |
| **§6.11 Advisory illusion** | If authz is enforced only by convention ("developers should add authz checks"), it's an advisory illusion. There must be a mechanism that prevents unauthorized endpoints from being deployed. |
| **§1.12 Observe everything** | Every authz decision, especially denials, is an observability event. Patterns of denied access reveal attack attempts, misconfigured roles, and UX problems. |
