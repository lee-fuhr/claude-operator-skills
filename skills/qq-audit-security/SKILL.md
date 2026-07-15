---
name: qq-audit-security
description: Serialized security audit using 23 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "security audit"
  - "vulnerability audit"
  - "owasp review"
  - "security framework review"
  - "pen test"
  - "run security audit"
---

# Audit security with expert personas

Audit security by running 23 expert personas in serial, fixing critical issues per framework before verifying.

23 security frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Is it safe? Would a security engineer approve?

Supersedes: ad-hoc security checklists, one-off OWASP scans.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-security`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-security OWASP Top 10`, "just run XSS on the form handler", "CSRF on the checkout flow", etc.

Match the framework name fuzzily — "owasp", "top 10", "xss", "cross site scripting" should all match the right framework. "csrf", "anti-forgery", "request forgery" should all match CSRF Protection. If ambiguous, show the 2-3 closest matches and ask.

### Mode 3: List frameworks (help/list/discovery)

Triggers: "list", "what do you have", "what frameworks", "help", "which ones", "show me", etc.

Show the framework table from the framework inventory below, then ask which one(s) to run.

---

## Smart interview (runs before any audit)

**DO NOT ask dumb questions.** Before asking anything, gather what you already know:

1. **Check conversation context** — What product are we working on? What files have been discussed? What has the user been complaining about?
2. **Check project CLAUDE.md** — Product description, tech stack, target audience.
3. **Check recent session state** — What was just built or changed?

**Pre-fill and present assumptions:**

> "Here’s what I know going in:
> - **Product:** [name] — [description from context]
> - **Tech stack:** [framework, language, hosting — inferred from project]
> - **Auth model:** [session-based / JWT / OAuth — inferred from code]
> - **Known attack surface:** [public APIs, file uploads, user input, third-party integrations]
> - **Scope:** [full app / specific endpoints / specific component]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell whether auth is session-based or JWT, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s key routes, middleware, and API endpoints to understand scope
3. Map the attack surface: public endpoints, auth flows, data stores, third-party integrations

### Phase 2: Serial framework execution

For each framework (in order 1-23):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-security/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent’s output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks

3. **Verify build** if fixes were applied (`npx next build` or equivalent)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #23 (Privacy/Data Minimization) as the final review
2. Compile consolidated report:
   - Overall security posture score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-security-[date].md` — full report
- `data/audit-security-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | OWASP Top 10 | The ten most critical web application security risks — is the app defended against the attack classes that actually matter? | `01-owasp-top-10.md` |
| 2 | Injection Prevention | All data entering queries parameterized — is untrusted input ever interpreted as code? | `02-injection-prevention.md` |
| 3 | Cross-Site Scripting (XSS) Prevention | User content escaped in every rendering context — can an attacker execute scripts in another user’s browser? | `03-xss-prevention.md` |
| 4 | CSRF Protection | State-changing operations require anti-CSRF tokens — can an attacker trick a user’s browser into making unwanted requests? | `04-csrf-protection.md` |
| 5 | Authentication Security | Resists credential stuffing, brute force, and identity spoofing — can the application reliably prove who someone is? | `05-authentication-security.md` |
| 6 | Authorization / Broken Access Control | Every object access checks server-side permissions — can users reach resources or functions they shouldn’t? | `06-authorization-enforcement.md` |
| 7 | Sensitive Data Exposure | Encrypted at rest and in transit, no secrets in logs — is sensitive data protected throughout its lifecycle? | `07-sensitive-data-exposure.md` |
| 8 | Content Security Policy (CSP) | Strict CSP preventing inline scripts and unauthorized origins — does the browser enforce what code is allowed to run? | `08-content-security-policy.md` |
| 9 | Dependency Vulnerability Audit | Third-party CVEs and timely patching — are the application’s dependencies free of known exploitable vulnerabilities? | `09-dependency-vulnerabilities.md` |
| 10 | Security Headers Audit | HSTS, X-Content-Type-Options, and friends — do HTTP response headers harden the browser’s security posture? | `10-security-headers.md` |
| 11 | API Security / Broken Function-Level Authorization | Function-level authorization on every API endpoint — can callers invoke operations they shouldn’t have access to? | `11-api-security.md` |
| 12 | File Upload Security | Validated type, size, and content, stored safely — can an attacker weaponize the file upload feature? | `12-file-upload-security.md` |
| 13 | Session Management Security | Timeout, rotation, secure cookies, and invalidation — can an attacker hijack, fixate, or ride a user’s session? | `13-session-management.md` |
| 14 | Cryptographic Practices | Current algorithms, proper key lengths, and sound key management — is the application’s cryptography actually protecting what it claims to protect? | `14-cryptographic-practices.md` |
| 15 | SSRF Prevention | User-controlled URLs validated before server-side fetch — can an attacker make the server request internal resources? | `15-ssrf-prevention.md` |
| 16 | Mass Assignment / Over-Posting | Only whitelisted fields accepted on write operations — can an attacker modify fields they shouldn’t by including extra parameters? | `16-mass-assignment.md` |
| 17 | Business Logic Abuse | Business rules enforced server-side — can an attacker exploit the application’s intended functionality for unintended outcomes? | `17-business-logic-abuse.md` |
| 18 | DNS/Subdomain Security | No dangling CNAMEs, proper email authentication — is the DNS infrastructure defended against hijacking and spoofing? | `18-dns-subdomain-security.md` |
| 19 | Client-Side Storage Security | No tokens or PII in localStorage — is the client-side storage model defended against extraction, persistence, and cross-site access? | `19-client-storage-security.md` |
| 20 | Clickjacking Protection | Frame-ancestors CSP and X-Frame-Options — can an attacker trick users into clicking hidden elements by framing the application? | `20-clickjacking-protection.md` |
| 21 | Supply Chain Security | Build pipeline protected per SLSA — can an attacker inject malicious code through dependencies, build tools, or CI/CD infrastructure? | `21-supply-chain-security.md` |
| 22 | Secrets Rotation | Never in code, always auditable — are secrets managed with proper lifecycle controls, rotation, and zero-code-exposure guarantees? | `22-secrets-rotation.md` |
| 23 | Privacy/Data Minimization | Only necessary data collected and retained per GDPR Art. 5 — does the application collect the minimum personal data required and delete it when no longer needed? | `23-privacy-data-minimization.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + config** — code audits miss runtime configuration issues. Always audit deployed headers, CSP, and server config when possible.
- **Multi-round** — after all 23 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
