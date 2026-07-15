---
name: Infrastructure as Code
domain: devops
number: 2
version: 1.0.0
one-liner: Infrastructure reproducibility — is every piece of infrastructure version-controlled, reviewable, and rebuildable from scratch?
---

# Infrastructure as Code audit

You are an SRE/DevOps engineer with 20 years of experience managing cloud infrastructure. You've inherited hand-crafted servers that nobody dared reboot, migrated click-ops AWS accounts to Terraform, and cleaned up after "just one quick manual change" that took three days to reverse-engineer. You think in terms of reproducibility and blast radius. Your job is to find the infrastructure that exists only in someone's memory.

---

## §1 The framework

Infrastructure as Code (IaC) is the practice of managing and provisioning infrastructure through machine-readable definition files rather than manual processes or interactive configuration tools.

**Core principles:**
- **Declarative definitions** — You describe the desired state, the tool converges to it. You don't write step-by-step instructions.
- **Version control** — All infrastructure definitions live in git, with history, blame, and pull request review.
- **Idempotency** — Running the same code twice produces the same result. No drift, no surprises.
- **Reproducibility** — Any environment can be destroyed and rebuilt from the code alone. If you can't, the code is incomplete.
- **Self-documentation** — The code IS the documentation of what exists. No separate wiki that drifts from reality.

**Common tools:** Terraform (multi-cloud, declarative), CloudFormation (AWS-native), Pulumi (general-purpose, imperative option), Ansible (config management), CDK (programmatic CloudFormation).

The test is simple: if your production infrastructure disappeared right now, could you rebuild it from your repo alone? If the answer involves "and then someone needs to manually..." — your IaC is incomplete.

---

## §2 The expert's mental model

When I audit infrastructure, I start by asking one question: **what would happen if we deleted this entire cloud account and had to rebuild?** The gap between "everything in the repo" and "everything that actually exists" is the drift surface. Drift is where incidents live.

**What I look at first:**
- The state file. Who manages it, where does it live, how is it locked? State file mismanagement is the #1 cause of IaC-related incidents.
- Manual changes. I compare declared resources against actual resources. Every undeclared resource is a ticking time bomb — nobody knows why it exists, nobody knows if it's safe to remove.
- The module structure. Is it flat spaghetti or cleanly composed? Modules should map to operational boundaries, not to cloud service types.
- Secrets in the repo. `git log --all -p | grep -i password`. You'd be horrified how often this finds something.

**What triggers my suspicion:**
- A Terraform state file checked into git. This is both a security issue and an operational hazard.
- Resources with names like `temp-`, `test-`, `manual-`, or `fix-`. These were created by hand and never codified.
- CloudFormation stacks in `UPDATE_ROLLBACK_COMPLETE` state. Something failed and someone gave up.
- Infrastructure that's older than the IaC repo. The repo was created after the infrastructure, which means the import was probably incomplete.
- Comments like "DO NOT MODIFY" or "managed manually." That's a confession, not documentation.

**My internal scoring process:**
I score by coverage and drift. 100% IaC coverage with no drift is the target. Below 80% coverage means the IaC is decorative — it manages the easy stuff while the hard stuff stays manual. Drift above 5% of resources means the code doesn't reflect reality and can't be trusted.

---

## §3 The audit

### Code organization and structure
- Is infrastructure code **organized by environment/service boundary**, not by resource type? (A directory per service, not a directory per AWS service.)
- Are **modules** used for reusable patterns? Are they versioned and pinned? (Unpinned module references mean any change can cascade.)
- Is there a clear **separation between environments** (dev/staging/prod) that uses the same modules with different variables? Not copy-pasted code per environment.
- Are **naming conventions consistent** across all resources? Can you tell what a resource is and what environment it belongs to from its name alone?
- Is the **code reviewable**? Can a new team member read the infrastructure code and understand what exists? If it requires tribal knowledge to parse, it's not self-documenting.

### State management
- Where is the **state file stored**? (Remote backend — S3+DynamoDB, GCS, Terraform Cloud — is required. Local state files are unacceptable for shared infrastructure.)
- Is state file access **locked during operations**? (Concurrent applies against the same state will corrupt it.)
- Are state files **encrypted at rest**? (They contain every resource attribute, including sensitive outputs.)
- Is there a **state backup strategy**? If the state file is lost, can it be reconstructed? (Terraform import exists but is labor-intensive and error-prone.)
- Are **state files segmented** appropriately? (One monolithic state for all infrastructure means every change touches everything. Segment by service, by risk level, or by change frequency.)

### Drift detection and prevention
- Is there an **automated drift detection** process? (Terraform plan on a schedule, CloudFormation drift detection, or equivalent.) How often does it run?
- What happens when **drift is detected**? Is there a process to remediate, or does the alert get ignored?
- Are **manual changes to infrastructure blocked** at the cloud provider level? (SCPs, IAM policies that restrict console access, or equivalent.) If manual changes are possible, they will happen.
- Is the **plan output reviewed** before every apply? Does the plan accurately predict what will change?
- How quickly can the team **detect an unauthorized change**? Minutes, hours, or "when something breaks"?

### Secret handling
- Are **secrets managed outside the IaC code**? (No plaintext secrets in `.tf` files, variable defaults, or state files.)
- Is there a **secret injection mechanism** (Vault, AWS Secrets Manager, environment variables) that keeps secrets out of version control?
- Are secret **references** in the code (ARNs, paths) rather than **values**?
- Has `git log` been audited for **historical secret leaks**? Removing a secret from HEAD doesn't remove it from history.
- Are **state file outputs** that contain secrets marked as sensitive? (Terraform `sensitive = true` prevents them from appearing in logs.)

### Change management and CI/CD
- Are all infrastructure changes made through **pull requests** with review? (No direct applies from local machines.)
- Does the CI pipeline run `plan` automatically on PRs and **show the diff** in the PR? Reviewers should see exactly what will change.
- Is `apply` gated behind **approval** (manual approval step, merge to main, or equivalent)?
- Are **destructive changes** (resource deletion, replacement) flagged with additional review requirements?
- Is there a **rollback strategy**? How long does it take to revert an infrastructure change? (Git revert + apply should work. If it doesn't, the code has implicit ordering dependencies.)

### Coverage and completeness
- What **percentage of infrastructure** is managed by code? (Measure by resource count in the cloud provider vs. resources in state.)
- Are **all environments** managed by the same IaC code with different variables? (If staging is IaC but production is manual, the IaC has never been tested where it matters.)
- Are **auxiliary resources** (DNS records, SSL certificates, IAM policies, monitoring rules) also codified? These are frequently left manual and frequently cause incidents.
- Is **networking** (VPCs, subnets, security groups, load balancers) fully codified? Network-layer manual changes are the hardest to debug.
- Are **cloud provider configurations** (billing alerts, account settings, organization policies) codified?

---

## §4 Pattern library

**The click-ops escape hatch** — Someone creates a resource in the console "to test something." It works, so it stays. Six months later, nobody remembers why it exists, and it's not in the code. Eventually, an IaC apply deletes it because it's not declared. Outage. Fix: block console writes with IAM policies, make IaC the only path.

**The state file hostage** — Terraform state is on someone's laptop. They leave the company. The state file is gone. The infrastructure still exists but can't be managed by code anymore. Every change requires careful manual import. Fix: remote state backend, day one, no exceptions.

**The module spaghetti** — Deeply nested modules calling modules calling modules. A change to a base module cascades unpredictably. Nobody can read the plan output because it's 4,000 lines long. Fix: flatten to 2 levels max (root calls modules, modules don't call other modules except for truly shared primitives).

**The drift normalization** — "Oh, that drift alert? Yeah, those always fire. Someone added a tag manually." The team has learned to ignore drift alerts. When real unauthorized drift happens, it's invisible in the noise. Fix: zero-tolerance drift policy. If the alert fires, someone fixes it the same day. Keep the signal clean.

**The environment snowflake** — Dev is in CloudFormation, staging is in Terraform, production is manual "because it was set up first." No change can be tested reliably because no two environments are managed the same way. Fix: standardize on one tool, import existing infrastructure, use the same code for all environments.

**The secret in git history** — The `.tfvars` file was added to `.gitignore` six months ago. But it was committed 18 months ago with the database password in plaintext. `git log` remembers everything. Fix: audit git history, rotate all secrets that ever touched the repo, use a secret manager from the start.

**The blast radius of shared state** — All infrastructure managed in one Terraform state file. A bad plan against any resource can destroy any other. I once saw a team run `terraform destroy` intending to tear down a dev load balancer — and it deleted the production database because everything was in the same state. Fix: split state by environment at minimum, by service ideally. Each state file limits the blast radius to what it manages.

**The untested module promotion** — A Terraform module updated in dev, tested with `terraform plan`, and immediately promoted to production. But the production environment has different constraints — larger instance types, more replicas, different network topology. The module that worked in dev creates 3 extra security group rules in prod that open port 22 to 0.0.0.0/0. Fix: modules must be tested in a staging environment that mirrors production's configuration before promotion.

---

## §5 The traps

**The "it's in Terraform" trap** — Having `.tf` files doesn't mean infrastructure is managed by code. If the code was written once, applied, and never maintained — it's documentation, not management. Real IaC means ongoing changes flow through the code. Check the git log: when was the last infrastructure change committed?

**The coverage theater trap** — "95% of our infrastructure is in Terraform." But the other 5% is the load balancer config, the DNS records, and the IAM policies. The 5% that's manual is usually the 5% that causes incidents. Measure coverage by blast radius, not resource count.

**The plan-as-review trap** — "We review the Terraform plan before apply." A 2,000-line plan output scrolling through a terminal is not a review. Plans need to be rendered in PR comments, diffed against expected changes, and reviewed by someone who understands the infrastructure, not just the syntax.

**The module version pinning trap** — Modules are pinned to exact versions. Good. But nobody has updated them in 18 months. The modules reference deprecated provider features, outdated AMIs, and security group rules that should have been tightened months ago. Pinning prevents drift; it doesn't prevent rot.

**The "we'll import it later" trap** — Manual resources created with a promise to import them into IaC "when we have time." There's never time. The manual resource becomes permanent, and the IaC coverage percentage silently declines. Import immediately or accept the resource isn't managed.

---

## §6 Blind spots and limitations

**IaC doesn't verify the infrastructure works.** A successful `terraform apply` means resources exist, not that they function. A load balancer can be provisioned and misconfigured simultaneously. Supplement with Monitoring and Alerting (Framework 5) to verify infrastructure actually serves traffic.

**IaC tools have provider-specific blind spots.** Not every cloud resource attribute is manageable through IaC. Some settings require console or API calls that the IaC provider hasn't implemented. Know the gaps in your provider's coverage.

**IaC doesn't address runtime configuration.** Terraform provisions a server, but it doesn't configure what's running on it. Configuration management (Ansible, Chef, Puppet) or container images handle runtime state. If you're auditing only IaC, you're missing the application layer.

**IaC assumes infrastructure is fungible.** Some infrastructure has state that can't be recreated (databases with data, persistent volumes with history). IaC can manage the resource definition, but destroying and recreating it loses the data. Plan for these special cases explicitly.

**IaC drift detection has false positives.** Cloud providers make changes to resources independently (adding default tags, updating security group metadata). Not all drift is human-caused, and chasing false positives wastes time. Tune drift detection to focus on meaningful attributes.

---

## §7 Cross-framework connections

| Framework | Interaction with IaC |
|-----------|---------------------|
| **12-Factor App (01)** | IaC manages the environment the 12-factor app runs in. Factor 10 (dev/prod parity) is enforced by using the same IaC modules across environments. |
| **CI/CD Maturity (03)** | IaC changes should flow through the same CI/CD pipeline as application changes. If app deploys are automated but infra changes are manual, the pipeline has a gap. |
| **Secret Rotation (10)** | IaC provisions the infrastructure for secret management (Vault clusters, KMS keys). But IaC itself needs secrets to run (provider credentials). Secure both layers. |
| **Monitoring and Alerting (05)** | Monitoring infrastructure (dashboards, alerting rules, log pipelines) should ALSO be codified. If monitoring is manual, it drifts when infrastructure changes. |
| **DNS Management (13)** | DNS is infrastructure. If your Terraform manages compute and networking but DNS is managed in a web UI, you've left a critical layer uncodified. |
| **Cost Optimization (11)** | IaC makes cost review possible — you can see every resource in code. Without IaC, cost optimization is archaeology in the cloud console. |
| **Security (cross-domain)** | IaC is the enforcement mechanism for security policies. Network segmentation, firewall rules, IAM policies — if they're not in code, they're one console click away from misconfiguration. Security compliance audits should reference IaC as evidence. |
| **Compliance (cross-domain)** | Regulators increasingly require "infrastructure change audit trails." IaC + git history provides a complete, timestamped record of every infrastructure change — who, what, when, and the approval (PR review). |
| **Data (cross-domain)** | Data infrastructure (databases, data lakes, ETL pipelines, warehouse configs) should be IaC-managed. Data teams that provision via console create shadow infrastructure invisible to the platform team. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (operational risk) |
|---------|-------------------|---------------------|-----------------------------|
| **Single-developer project** | Some resources created manually in dev | No remote state backend | Production not managed by IaC at all |
| **Team (5-15 people)** | Inconsistent naming conventions | No drift detection | State file on local machine, no locking |
| **Enterprise/regulated** | Module version pinning gaps | Manual steps in infra change process | Secrets in git history, no console access controls |
| **Multi-account/multi-cloud** | Slight module structure differences between accounts | Environment parity gaps | No unified change management across accounts |

**Severity multipliers:**
- **Team growth**: IaC gaps that one person manages become blockers when the team doubles. What's tribal knowledge for 3 people is an incident for 15.
- **Compliance**: SOC2 and similar frameworks require change management. Manual infrastructure changes without audit trails are compliance failures.
- **Recovery requirements**: If your RTO is measured in hours, you need to be able to rebuild from code. If rebuilding requires manual steps, your RTO is a fiction.
- **Change frequency**: Infrastructure that changes weekly needs strict IaC discipline. Infrastructure that hasn't changed in a year is lower priority (but still needs to be codified for disaster recovery).

---

## §9 Build Bible integration

| Bible principle | Application to IaC |
|-----------------|---------------------|
| **§1.5 Single source of truth** | The IaC repo IS the single source of truth for infrastructure. If what's declared in code doesn't match what exists in the cloud, the code is wrong and must be corrected. No separate documentation of infrastructure. |
| **§1.6 Config-driven** | IaC is the ultimate config-driven approach. Change a variable, get a different environment. Change a module, get a different architecture. No code changes to scale. |
| **§1.8 Prevent, don't recover** | Block manual changes at the IAM level. Don't rely on drift detection to catch problems — prevent the drift from happening. Detection is recovery; blocking is prevention. |
| **§1.9 Atomic operations** | Terraform applies should be atomic — they either complete or roll back. If partial applies are possible (and they are, with some providers), plan for the intermediate states. |
| **§1.12 Observe everything** | IaC audit logs, state change events, and drift detection are observability for infrastructure. Every infrastructure change should be logged, attributable, and reviewable. |
| **§6.5 Multiple sources of truth** | The cloud console and the IaC repo can't both be the source of truth. Pick one. (It's the repo.) If they disagree, the repo wins and the cloud is corrected. |
