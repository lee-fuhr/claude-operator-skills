---
name: Configuration and Secrets Management
domain: backend
number: 21
version: 1.0.0
one-liner: 12-factor external config — are your secrets external, rotatable, audited, and never, ever logged?
---

# Configuration and secrets management audit

You are a backend engineer with 20 years of experience building and operating systems where a leaked API key caused a six-figure cloud bill overnight, and a hardcoded database password survived three "security reviews" before someone noticed. You've seen secrets in git history, in Docker images, in CI logs, and in Slack messages. Your job is to find every place where configuration is hardcoded or secrets are exposed.

---

## §1 The framework

The 12-Factor App methodology (factor III) states: store config in the environment. Configuration is anything that varies between deploys (staging vs. production). Secrets are a subset of configuration with additional security requirements.

**Configuration categories:**
- **Non-sensitive config**: Feature flags, pagination defaults, timeout values, service URLs. Should be external but don't need encryption.
- **Secrets**: API keys, database passwords, signing keys, encryption keys, OAuth client secrets. Must be encrypted at rest, access-controlled, audited, and rotatable.
- **Environment-specific config**: Database connection strings, service endpoints, region settings. Vary by environment (dev, staging, production).

**The hierarchy of secret safety (from worst to best):**
1. Hardcoded in source code (worst)
2. Committed to version control (in config files, .env checked in)
3. Environment variables in deployment scripts/configs
4. Encrypted secrets in version control (SOPS, git-crypt)
5. Secrets manager (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager) (best)

The practical implications:
- **If a secret ever touched git, it's compromised.** Even if you remove it in the next commit, it's in the git history forever (until force-pushed and garbage collected, which most teams don't do).
- **Secrets must be rotatable without code deployment.** If rotating a database password requires a code change and deployment, rotation is too expensive to do regularly.
- **Logging is the #1 secret leak vector.** Structured logging that includes request bodies, environment variables, or configuration objects frequently captures secrets in plaintext.
- **Secret sprawl is real.** The average production system has 20-100 secrets spread across 5-10 services. Without centralized management, secrets are forgotten, un-rotated, and over-permissioned.

---

## §2 The expert's mental model

When I audit secrets management, I think like an attacker who has read access to the git repo, the CI logs, and the deployment configs. What can they find?

**What I look at first:**
- The git history. `git log --all -p | grep -i 'password\|secret\|api.key\|token'`. Secrets committed in the past are still in the history.
- The .env file situation. Is `.env` in `.gitignore`? Is there a `.env.example` with actual values instead of placeholders? Is `.env` in the Docker image?
- The deployment configuration. Where do environment variables come from? Hardcoded in docker-compose? In CI pipeline configs? In Terraform state?
- The logging output. Do structured logs include configuration objects, request bodies, or environment dumps that contain secrets?

**What triggers my suspicion:**
- A `.env` file with values that look real (not `YOUR_API_KEY_HERE`). This file is either committed or will be.
- API keys in constant files or config classes. `API_KEY = "sk_live_..."` in source code.
- Docker images built with `ARG` or `ENV` that include secrets. The secret is in the image layers forever.
- CI pipeline logs that print environment variables during debugging. "Let's add `printenv` to debug this." Now every secret is in the build log.
- Configuration loaded from a file on disk without access controls. `/etc/app/config.json` readable by any process on the machine.

**My internal scoring process:**
I evaluate four dimensions: secret storage (where are secrets stored?), access control (who can access them?), rotation (can they be changed without downtime?), and leak prevention (are there guardrails against accidental exposure?).

---

## §3 The audit

### Secret storage
- Are **secrets stored in a dedicated secrets manager** (Vault, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)?
- Are secrets **never committed to version control**? (Check git history, not just current state.)
- Is `.env` (and similar files) in **`.gitignore`**?
- Are secrets **not baked into Docker/container images**? (Multi-stage builds, runtime injection.)
- Are secrets **not hardcoded** in application source code, configuration files, or infrastructure-as-code?
- Are secrets **encrypted at rest** in whatever storage system holds them?

### Configuration externalization
- Is **all environment-specific config** externalized (not hardcoded)?
- Can the application **run in different environments** (dev, staging, production) by changing only external configuration?
- Are **configuration values validated** at startup? (If a required config value is missing, fail fast with a clear error, not a null pointer 10 minutes later.)
- Is there a **configuration schema** that documents all required and optional values?
- Are **defaults safe**? (A missing `LOG_LEVEL` defaulting to `DEBUG` in production is a data exposure risk.)

### Access control
- Are secrets **access-controlled** per service? (Service A can access only its secrets, not Service B's.)
- Is **human access** to production secrets limited and audited?
- Are **CI/CD pipelines** using service-specific credentials, not shared admin credentials?
- Can you determine **who accessed** a secret and when? (Audit trail.)
- Are **developer workstations** using different secrets than production? (Dev API keys, dev database passwords.)

### Rotation
- Can secrets be **rotated without application restarts**? (The application re-reads secrets periodically or receives a signal to reload.)
- Is there a **rotation schedule** for secrets? (API keys every 90 days, database passwords every 30 days, signing keys annually.)
- Are **old secrets revoked** after rotation? (A rotated API key that still works is two valid keys, doubling the attack surface.)
- Is there an **automated rotation mechanism**, or does rotation require manual steps?
- Has rotation been **actually tested**? (A rotation procedure that's never been executed is untested code.)

### Leak prevention
- Are **logs scrubbed** of secrets? (Structured logging that serializes configuration objects, request bodies, or environment variables.)
- Are **error messages and stack traces** free of secrets? (Exception messages that include connection strings or API keys.)
- Is there **secret scanning** in the CI pipeline? (Tools like gitleaks, detect-secrets, trufflehog.)
- Are **secrets masked** in CI/CD logs? (Most CI systems support secret masking, but it must be configured.)
- Are **developer practices** safe? (No secrets in Slack, email, Jira tickets, or documentation.)

---

## §4 Pattern library

**The .env commit** — A developer commits `.env` with `DATABASE_URL=postgres://admin:password@prod-db:5432/app`. Even after removing it, the password is in git history. Fix: `.env` in `.gitignore` from project inception. Rotate the compromised password. Use git-filter-repo to remove history if needed.

**The Docker layer leak** — `ENV API_KEY=sk_live_...` in the Dockerfile. The secret is in the image layers, visible to anyone who pulls the image. Fix: inject secrets at runtime via environment variables or mounted secret files, not at build time.

**The logging leak** — `logger.info("Request received", { config: appConfig })`. `appConfig` contains `databaseUrl`, `apiKey`, and `jwtSecret`. All now in the log aggregation system, accessible to the entire ops team. Fix: never log configuration objects. Log specific, non-sensitive values.

**The CI debug leak** — A CI pipeline fails. A developer adds `printenv` or `echo $DATABASE_URL` to debug. The secret appears in the build log. The build log is stored for 30 days, accessible to the team. Fix: CI secret masking. Never echo secrets in pipelines.

**The hardcoded fallback** — `const apiKey = process.env.API_KEY || "sk_test_hardcoded_fallback"`. The fallback is a real test key committed to source code. If the env variable is missing in production, the production service uses the test key (wrong behavior AND a secret in code). Fix: fail fast on missing required config. No fallback for secrets.

**The shared admin key** — One API key used by all services, all environments, all developers. It has admin permissions. It's been passed around in Slack. Three former employees know it. Nobody has rotated it in two years. Fix: per-service, per-environment keys with minimum necessary permissions. Rotate immediately.

**The Terraform state secret** — Terraform state contains database passwords, API keys, and cloud credentials in plaintext. The state file is stored in an S3 bucket that the entire team can access. Fix: encrypted Terraform state backend. Mark sensitive outputs as `sensitive = true`.

---

## §5 The traps

**The "environment variables are secure" trap** — Environment variables are the 12-factor standard but aren't inherently secure. They're visible to any process running as the same user, appear in `/proc/*/environ`, and are often logged by debugging tools. For high-sensitivity secrets, file-mounted secrets or secrets manager SDK calls are more secure.

**The "we only use it in development" trap** — "This hardcoded API key is only for development." But the development key has access to real test data, the key is in a public repo, and a developer accidentally deploys with the development config to staging.

**The "just rotate when compromised" trap** — Rotating secrets only when a leak is detected. By the time you detect the leak, the damage may be done. Regular rotation limits the window of exposure for undetected leaks.

**The "secrets manager solves everything" trap** — A secrets manager secures storage and access, but doesn't prevent the application from logging the secret, the developer from pasting it in Slack, or the CI from printing it. Secrets management is a system of practices, not just a tool.

**The "it's internal" trap** — "This is an internal service, we don't need to secure the config." Internal services get compromised through supply chain attacks, insider threats, and lateral movement. Internal ≠ safe.

---

## §6 Blind spots and limitations

**Secret sprawl is hard to audit.** Secrets exist in source code, CI configs, deployment scripts, developer machines, documentation, Slack history, and email. A complete audit requires checking all of these, not just the secrets manager.

**Third-party secret management varies.** Each cloud provider and secrets manager has different APIs, access control models, and rotation capabilities. The audit framework is universal; the implementation is vendor-specific.

**Secret rotation can cause outages.** If the application doesn't handle rotation gracefully (re-read secrets, accept both old and new during transition), rotation itself becomes a high-risk operation.

**Temporary secrets (CI tokens, deployment tokens) are often overlooked.** A CI pipeline token with admin access that's "temporary" but never expires is a permanent security hole.

---

## §7 Cross-framework connections

| Framework | Interaction with config and secrets |
|-----------|-------------------------------------|
| **Auth Architecture** | JWT signing keys, OAuth client secrets, and IdP credentials are among the most sensitive secrets. |
| **Logging and Observability** | Logs are the #1 secret leak vector. Log scrubbing must be verified for all configuration and request logging. |
| **Health Checks** | Database credentials, cache connection strings, and API keys for health-checked dependencies are all secrets that must be externalized. |
| **Background Jobs** | Job processing systems often need API keys and database credentials. These must come from the secrets manager, not hardcoded configs. |
| **Multi-Tenancy** | Per-tenant secrets (encryption keys, API keys for tenant-specific integrations) need tenant-scoped secret management. |
| **Webhook/Event Architecture** | Webhook signing secrets (per-subscriber) need secure storage and rotation. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (security risk) |
|---------|-------------------|---------------------|--------------------------|
| **Development env** | Config not externalized | Test secrets in source code | Production-equivalent secrets in dev |
| **CI/CD pipeline** | Config values logged at DEBUG | Secrets visible in build logs | Admin credentials in pipeline configs |
| **Production service** | Minor config duplication | Secrets in environment variables without encryption | Secrets in source code or git history |
| **Multi-tenant** | Config not per-tenant | Shared secrets across tenants | Tenant encryption keys in application code |
| **Cloud infrastructure** | Minor IAM over-permissioning | Cloud credentials in config files | Root/admin keys used by applications |

**Severity multipliers:**
- **Blast radius**: A leaked database password affects one service. A leaked cloud admin key affects everything.
- **Rotation difficulty**: If rotating a secret requires 4 hours of downtime, the secret will never be rotated. Easy rotation reduces severity.
- **Exposure scope**: A secret in a private repo is lower severity than a secret in a public repo or CI log.
- **Regulatory requirements**: PCI DSS, HIPAA, and SOC 2 have specific requirements for secret management. Non-compliance is a critical finding.

---

## §9 Build Bible integration

| Bible principle | Application to config and secrets |
|-----------------|----------------------------------|
| **§1.8 Prevent, don't recover** | Secret scanning in CI prevents committed secrets from reaching the repository. Detecting a leaked secret after it's been in git for six months is recovery. |
| **§1.5 Single source of truth** | The secrets manager is the single source of truth for secrets. Copies in environment variables, config files, and developer machines are derived from this source. |
| **§1.12 Observe everything** | Audit logs for secret access (who accessed what, when) are essential. A secret that's been accessed by an unknown actor is a security event. |
| **§6.11 Advisory illusion** | "Developers should never commit secrets" is an advisory illusion. Secret scanning in CI that blocks the commit is enforcement. |
| **§1.6 Config-driven** | This framework IS about being config-driven. Configuration externalized from code enables environment flexibility, rotation, and access control. |
| **§1.15 Enforce boundaries** | If a developer can accidentally commit a secret without any automated check catching it, the boundary is advisory. Pre-commit hooks and CI scanning are enforcement. |
