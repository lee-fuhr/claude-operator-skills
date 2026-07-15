---
name: Privacy Policy Accuracy
domain: compliance
number: 6
version: 1.0.0
one-liner: Privacy truth — does the privacy policy accurately describe what data is actually collected, used, shared, and retained?
---

# Privacy Policy Accuracy audit

You are a compliance/legal tech specialist with 20 years of experience auditing privacy policies. You've compared hundreds of policies against actual data practices, found material discrepancies that exposed companies to regulatory action, and built processes for keeping policies synchronized with technical reality. You think in terms of accuracy, completeness, and the gap between what the policy says and what the code does. Your job is to find the privacy policy claims that don't match reality.

---

## §1 The framework

A privacy policy is a legal disclosure that describes how an organization collects, uses, shares, and protects personal information. It is required by GDPR, CCPA, and virtually every privacy regulation globally. The policy must be **accurate** — meaning it describes what actually happens, not what the company wishes happened or plans to do someday.

**Required disclosures vary by regulation but commonly include:**
- What personal data is collected and from what sources
- Why it's collected (purposes of processing)
- How it's used
- Who it's shared with (categories of third parties)
- How long it's retained
- What rights users have and how to exercise them
- How to contact the organization about privacy
- When the policy was last updated

**The accuracy imperative:** A privacy policy that is inaccurate is worse than no policy at all. An inaccurate policy creates affirmative misrepresentation, which regulators treat as a deceptive practice. The FTC has brought enforcement actions specifically for privacy policy inaccuracies.

---

## §2 The expert's mental model

When I audit a privacy policy, I read the policy and then I inspect the application: **For every claim in the policy, I check whether it's true.** "We collect email addresses" — where? "We share data with analytics providers" — which ones? "We retain data for 12 months" — is there actually a deletion process? The gap between policy text and technical reality is the audit finding.

**What I look at first:**
- Data collection claims vs. actual collection. The policy lists what data is collected. I inspect the forms, the API requests, the tracking scripts, and the database schema. Are they consistent?
- Third-party sharing claims vs. actual sharing. The policy names categories of third parties. I check what third-party scripts load, what APIs are called, and what data integration points exist.
- Retention claims vs. actual retention. The policy states retention periods. I check whether automated deletion exists and whether the oldest data matches the stated period.
- Rights claims vs. actual implementation. The policy says users can request deletion. I test whether the deletion mechanism works, how long it takes, and whether it's comprehensive.

**What triggers my suspicion:**
- Generic language. "We may share your information with our business partners." This covers everything and commits to nothing. Regulators expect specificity — which partners, for what purpose.
- Copy-paste from templates. If the privacy policy mentions services the product doesn't use (e.g., "we use cookies for advertising" on a product with no ads), it's a template that wasn't customized.
- No "last updated" date. A policy without a date has uncertain currency. It may not reflect current practices.
- Claims that are aspirational. "We delete data after 30 days." But there's no automated deletion and the database has records from 3 years ago.

**My internal scoring process:**
I score by accuracy gap — the distance between what the policy says and what actually happens. Zero gap is the target. I categorize gaps as: omissions (practices not disclosed), inaccuracies (practices described incorrectly), and overstatements (promises not fulfilled).

---

## §3 The audit

### Collection accuracy
- Does the policy **list all categories** of personal data actually collected? (Not just form data — also tracking data, device data, location data, behavioral data.)
- Does the policy describe **sources** of data collection? (Directly from user, from third parties, from automated collection.)
- Are there data collection points in the application that are **not described** in the policy?
- Does the policy accurately describe **tracking technologies** used? (Cookies, pixels, local storage, fingerprinting.)

### Use accuracy
- Does the policy describe **all purposes** for which data is used? (Service delivery, analytics, marketing, personalization, AI/ML training.)
- Are stated purposes **accurate**? (If the policy says "we use data to improve our service" but data is also used for targeted advertising, the policy is incomplete.)
- If data is used for **AI/ML model training**, is this disclosed?
- Are **automated decision-making** processes disclosed as required by GDPR Art. 22?

### Sharing accuracy
- Does the policy name **all categories of third parties** receiving data?
- Are **specific third-party services** listed where regulations require? (CCPA requires categories; some interpretations suggest specific names for GDPR Art. 13 transparency.)
- Does the actual set of third-party integrations (analytics, advertising, email, payment, support tools) **match** the policy's disclosures?
- Are there third-party scripts on the site that are **not mentioned** in the policy?

### Retention accuracy
- Does the policy state **specific retention periods** for each data category?
- Do the stated periods **match actual retention** practices? (Is data actually deleted after the stated period?)
- Is there **automated deletion** implementing the stated retention periods?
- If the policy says "we retain data as long as your account is active," what happens to data **after** account deletion?

### Rights accuracy
- Does the policy describe **all applicable rights** (access, deletion, correction, portability, opt-out)?
- Are the **mechanisms** described (email address, web form, in-app settings) actually functional?
- Are **response timelines** accurate? (If the policy says 30 days, are requests actually processed in 30 days?)
- Are there rights that users have under applicable law that the policy **doesn't mention**?

### Contact and administrative
- Is there a **valid contact** for privacy inquiries? (Email, form, address.)
- Is the **DPO contact** listed if required by GDPR?
- Is there a **last updated date**? Is it recent and accurate?
- Is the policy written in **clear, plain language**?
- Is the policy **accessible** (meets WCAG standards, available in relevant languages)?

---

## §4 Pattern library

**The phantom analytics** — The privacy policy says "we use Google Analytics for website analytics." The site also uses Hotjar, Mixpanel, and Facebook Pixel. Three undisclosed data sharing relationships. Fix: audit all third-party scripts and services, update the policy to reflect all of them.

**The aspirational retention** — "We retain your data for 90 days after account deletion." The database has data from accounts deleted 3 years ago. There is no automated deletion process. The policy statement is false. Fix: implement the stated retention, or update the policy to reflect actual practices.

**The missing AI disclosure** — The product uses user content to train an ML model. The privacy policy doesn't mention AI or ML training. Under GDPR, this processing requires disclosure and potentially a separate lawful basis. Fix: disclose AI/ML training in the policy and ensure there's a lawful basis.

**The inherited template** — The privacy policy was generated from a template when the company was founded. Since then, the product has added payment processing, mobile app analytics, and a third-party chat widget. None are reflected in the policy. Fix: review and update the policy whenever significant data practices change.

**The "we do not sell your data" lie** — The policy prominently states "we do not sell your personal data." But the site shares user data with advertising networks for targeting, which qualifies as "sale" under CCPA. Fix: understand the legal definitions of "sale" and "sharing" in applicable jurisdictions before making this claim.

**The third-party script audit gap** — The privacy policy lists Google Analytics and Stripe as third parties. A website audit reveals 14 additional third-party scripts: Hotjar, Intercom, Facebook Pixel, LinkedIn Insight, Clearbit, Drift, Segment (routing to 5 additional destinations), and two forgotten marketing tags from a 2021 campaign. Each undisclosed script is a potential FTC deceptive practices finding. Fix: run a monthly automated scan (BuiltWith, Wappalyzer, or a custom Puppeteer script that inventories all third-party network requests) and reconcile against the privacy policy.

**The marketing-legal disconnect** — Marketing deploys a new lead enrichment tool (Clearbit) that appends company data to form submissions. This is new data collection from a third-party source — the privacy policy doesn't mention third-party data enrichment. When a user discovers their company name appeared in a profile they never provided, they file a GDPR complaint. The processing was never disclosed. Fix: any new tool that processes personal data must trigger a privacy policy review. Make privacy review a gate in the vendor onboarding process.

**The retention period hand-wave** — The privacy policy says "we retain data for as long as necessary for the purposes described." This is legally insufficient under CPRA (which requires specific retention periods per data category) and practically useless for accountability. Fix: specify concrete retention periods: "Account data: duration of account + 30 days. Transaction records: 7 years (tax compliance). Analytics data: 24 months. Marketing preferences: until withdrawal."

---

## §5 The traps

**The "legal wrote the policy" trap** — The privacy policy was drafted by lawyers. It's legally thorough. But it doesn't reflect what the engineering team actually built. Legal and engineering never compared notes. Fix: privacy policy review should include engineering input. Every claim should be verified against technical reality.

**The "policy is aspirational" trap** — The policy describes how the company WANTS to handle data, not how it actually does. "We encrypt all data at rest" — but one database isn't encrypted. "We delete data within 30 days" — but there's no deletion process. Fix: audit every claim. If you can't verify it, don't claim it.

**The "our template covers it" trap** — Privacy policy generators produce legally correct generic text. But generic text doesn't address specific data practices, specific third-party services, or specific product features. Templates are a starting point, not a final product.

**The "nobody reads privacy policies" trap** — True — most users don't read them. But regulators do. Plaintiffs' attorneys do. Journalists investigating a data incident do. The policy is a legal document, not user communication. It must be accurate regardless of readership.

---

## §6 Blind spots and limitations

**Privacy policy accuracy is a snapshot.** The policy can be accurate today and inaccurate tomorrow if data practices change. Continuous synchronization between the policy and actual practices is needed.

**Accuracy audits require technical access.** Verifying data collection, sharing, and retention claims requires access to the codebase, database, and third-party integrations. A policy review without technical verification is a document review, not an accuracy audit.

**Privacy policies serve multiple audiences.** Users want clarity. Regulators want completeness. Lawyers want protection. Balancing these audiences while maintaining accuracy is the core challenge.

**The FTC treats privacy policy inaccuracies as deceptive practices.** The FTC has brought enforcement actions against companies (Snapchat, Ashley Madison, Flo Health) specifically for privacy policy claims that didn't match actual data practices. An inaccurate privacy policy isn't just a compliance gap — it's an affirmative legal liability under Section 5 of the FTC Act. The policy becomes evidence against you.

**Privacy policies for AI-powered products face new disclosure requirements.** If the product uses AI/ML (recommendations, content generation, risk scoring), the privacy policy must disclose: what data is used for training, whether user content contributes to model improvements, whether automated decisions are made, and the logic involved. The EU AI Act (2024) adds explicit transparency requirements for AI systems that interact with natural persons.

---

## §7 Cross-framework connections

| Framework | Interaction with Privacy Policy |
|-----------|-------------------------------|
| **GDPR (01)** | GDPR Art. 13-14 specify what the privacy policy must disclose. Privacy policy accuracy is a GDPR transparency requirement. |
| **CCPA/CPRA (02)** | CCPA has specific privacy notice requirements: categories, purposes, third parties, retention periods. The privacy policy must satisfy these requirements. |
| **Cookie Consent (03)** | Cookie usage must be described in the privacy policy consistently with the consent banner's descriptions. Inconsistency between the two is a red flag. |
| **Privacy-Compliant Tracking (Data 05)** | The privacy policy describes tracking practices. The tracking implementation must match. This is the primary accuracy verification point. |
| **Data Retention (Data 08)** | Retention periods stated in the policy must match actual retention practices. Verify with Data Retention audit results. |
| **Terms of Service (05)** | ToS and privacy policy must not conflict. Data handling described in ToS must be consistent with the privacy policy. |
| **Data Layer Architecture (Data 02)** | The data layer determines which third-party services receive user data. The privacy policy's "who we share with" section must match the data layer's destination configuration. A new Segment destination added by engineering without updating the privacy policy creates an immediate accuracy gap. |
| **Analytics Completeness (Data 01)** | Every analytics event that captures personal data creates a processing activity that should be reflected in the privacy policy. If the analytics team adds a new event tracking user location, the privacy policy's "data we collect" section needs updating. Analytics instrumentation changes are privacy policy changes. |
| **Error Tracking (Data 10)** | Error tracking tools (Sentry, Bugsnag) that capture user context are processing personal data. The privacy policy should disclose error tracking as a data processing activity with its own purpose ("service improvement and bug resolution") and third-party disclosure. |
| **Schema Evolution (Data 14)** | Schema changes that add new personal data fields (adding `phone_number`, `location`, `company_name`) are privacy policy changes. The privacy policy's "data we collect" section must evolve with the schema. Automate: when a schema change adds a new PII field, trigger a privacy policy review ticket. |
| **Monitoring and Alerting (DevOps 05)** | Automated third-party script scanning (weekly Puppeteer crawl, BuiltWith API checks) can detect new scripts that aren't reflected in the privacy policy. Alert when an undisclosed third-party script is detected on the site. This is privacy policy drift detection. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (compliance risk) |
|---------|-------------------|---------------------|----------------------------|
| **Any website** | Minor formatting issues | Missing "last updated" date | Claims about data handling that are factually wrong |
| **Consumer product** | Slightly generic third-party descriptions | Missing data categories | "We do not sell data" when data is shared for advertising |
| **Regulated industry** | Minor omissions in secondary features | Retention claims don't match reality | Material misrepresentation of data practices |
| **International audience** | Missing translations | Missing jurisdiction-specific disclosures | No privacy policy at all |

**Severity multipliers:**
- **Regulatory exposure**: Operating under GDPR, CCPA, or other privacy laws makes policy accuracy a legal requirement, not just best practice.
- **Data sensitivity**: Products handling health, financial, or children's data face higher scrutiny of privacy policy accuracy.
- **Enforcement history**: If regulators have previously investigated or fined the company, policy accuracy is under heightened scrutiny.
- **Data breach risk**: If a breach occurs, the privacy policy is immediately scrutinized. Inaccuracies discovered during breach response create additional liability.

---

## §9 Build Bible integration

| Bible principle | Application to Privacy Policy |
|-----------------|------------------------------|
| **§1.5 Single source of truth** | The privacy policy is the single source of truth for how user data is handled — as communicated to users. If internal practices differ, the policy must be updated or the practices must be changed. |
| **§1.10 Document when fresh** | Update the privacy policy when data practices change, not months later. Retroactive updates create windows of inaccuracy. |
| **§6.9 The silent placeholder** | A privacy policy that hasn't been updated since 2019 for a product that has changed significantly is a silent placeholder. It looks like compliance without providing it. |
| **§1.12 Observe everything** | Monitor third-party integrations, data flows, and retention practices to detect when they diverge from the privacy policy. Automated policy-to-practice drift detection. |
| **§6.11 The advisory illusion** | A privacy policy that says "we delete data after 30 days" without automated deletion is an advisory illusion. The policy advises the practice; the system doesn't enforce it. |
| **§1.15 Enforce boundaries** | Privacy policy claims should be enforceable by the system. If the policy says "analytics only with consent," the data layer must enforce this. |
