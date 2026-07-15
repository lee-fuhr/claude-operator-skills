# Pre-audit interview

Interview questions to ask before running a dashboard audit, when they can’t be inferred from inspection.

---

## Smart interview (pre-audit)

Before auditing, ask only what can’t be inferred from inspection. Pre-fill from context (file read, screenshots) first. Ask remaining gaps.

**Always ask:**
1. Who is the primary user? (operator on-call, manager checking trends, engineer debugging)
2. What is the most critical action they take? (restart a service, acknowledge an alert, export a report)
3. What was the last thing that went wrong that the dashboard failed to catch or enable them to fix?

**Ask only if unclear from code:**
4. Is any data demo/synthetic in production?
5. What is the freshness SLA for each key metric?
6. Are there multiple user roles with different permissions?

Do not ask about technology stack, design system, or team structure, these can be inferred from the code.
