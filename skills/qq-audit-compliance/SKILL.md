---
name: qq-audit-compliance
description: Serialized compliance audit using 15 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "compliance audit"
  - "legal audit"
  - "gdpr audit"
  - "privacy audit"
  - "accessibility compliance"
  - "run compliance audit"
---

# Audit compliance with expert personas

Audit compliance by running 15 expert personas in serial, fixing critical issues per framework before verifying.

15 compliance frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Is it legally sound? Would legal counsel approve?

Supersedes: ad-hoc privacy reviews, one-off accessibility checks.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-compliance`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-compliance GDPR`, "just run cookie consent on the marketing site", "check ADA compliance", etc.

Match the framework name fuzzily — "gdpr", "eu privacy", "data protection" should all match GDPR Compliance. "ada", "508", "accessibility law" should all match ADA/Section 508 Compliance. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Jurisdictions:** [US / EU / both — inferred from audience and hosting]
> - **User data collected:** [PII types — inferred from forms, auth, analytics]
> - **Known compliance concerns:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full compliance / specific regulation / specific feature]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell whether the product serves EU users, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

**Important caveat:** This audit identifies compliance gaps and recommends fixes, but is NOT a substitute for legal counsel. Flag anything that requires legal interpretation with a "LEGAL REVIEW NEEDED" marker.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s privacy policy, terms of service, cookie implementation, and data flows to understand scope
3. Map the compliance surface: data collected, processors used, jurisdictions served, consent mechanisms

### Phase 2: Serial framework execution

For each framework (in order 1-15):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-compliance/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."
   - "Mark anything requiring legal interpretation with LEGAL REVIEW NEEDED."

2. **Collect the agent’s output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks
   - Items flagged for legal review

3. **Verify build** if fixes were applied (`npx next build` or equivalent)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #15 (Record of Processing Activities) as the final documentation review
2. Compile consolidated report:
   - Overall compliance posture score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Items requiring legal review (collected across all frameworks)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-compliance-[date].md` — full report
- `data/audit-compliance-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | GDPR Compliance | EU data protection — is personal data processed lawfully, with clear purpose, minimal collection, and enforceable data subject rights? | `01-gdpr.md` |
| 2 | CCPA/CPRA Compliance | California privacy — do users have clear opt-out rights, data access, and an honest privacy notice about what’s collected and sold? | `02-ccpa.md` |
| 3 | Cookie Consent Implementation | Cookie law compliance — does the consent banner offer genuine choice, fire no cookies before consent, and respect withdrawal? | `03-cookie-consent.md` |
| 4 | ADA/Section 508 Compliance | Legal accessibility — does the site meet ADA and Section 508 requirements to avoid lawsuits and serve users with disabilities? | `04-ada-508.md` |
| 5 | Terms of Service Completeness | Legal protection — do your terms cover liability, disputes, acceptable use, and termination in an enforceable way? | `05-terms-of-service.md` |
| 6 | Privacy Policy Accuracy | Privacy truth — does the privacy policy accurately describe what data is actually collected, used, shared, and retained? | `06-privacy-policy.md` |
| 7 | Children’s Privacy (COPPA) | Children’s protection — are age gates, parental consent, and data protections in place for users under 13? | `07-coppa.md` |
| 8 | Open Source License Compliance | License obligations — are all open source components identified, licenses compatible, and attribution requirements met? | `08-oss-license.md` |
| 9 | Data Processing Agreement Coverage | Processor contracts — do all third-party processors have valid DPAs with required GDPR Art. 28 terms? | `09-dpa-coverage.md` |
| 10 | Right to Deletion Implementation | Erasure execution — when a user requests deletion, is data actually removed from all systems including backups and third-party processors? | `10-right-to-deletion.md` |
| 11 | Data Breach Notification Readiness | Breach response — can you detect, assess, and notify regulators within 72 hours and affected individuals without undue delay? | `11-breach-notification.md` |
| 12 | International Data Transfer | Cross-border legality — is there a valid legal basis for every transfer of personal data outside the EEA, especially EU-to-US? | `12-international-transfer.md` |
| 13 | Accessibility Statement | Published commitment — is there a public accessibility statement disclosing compliance level, known issues, and a contact for reporting barriers? | `13-accessibility-statement.md` |
| 14 | Automated Decision-Making Transparency | Algorithmic accountability — are users informed about automated decisions that affect them and given the right to human review? | `14-automated-decisions.md` |
| 15 | Record of Processing Activities (ROPA) | Processing documentation — is there a current, complete ROPA maintained that would satisfy a regulator’s request? | `15-processing-records.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + policy** — code audits miss policy gaps. Always check actual privacy policies, terms, and consent flows against what the code does.
- **Multi-round** — after all 15 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
- **Not legal advice** — flag anything needing legal interpretation with LEGAL REVIEW NEEDED. This audit finds gaps, it doesn’t provide legal opinions.
