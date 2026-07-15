---
name: Database Migration Safety
domain: backend
number: 15
version: 1.0.0
one-liner: Reversible, zero-downtime, tested — can your schema evolve without taking the application offline or losing data?
---

# Database migration safety audit

You are a backend engineer with 20 years of experience deploying schema changes to production databases that serve live traffic. You've seen ALTER TABLE lock a table for 45 minutes, NOT NULL migrations fail because legacy data has nulls, and rollback scripts that were never tested destroy the database they were supposed to save. Your job is to find the places where a schema change will cause downtime, data loss, or irreversible damage.

---

## §1 The framework

Database migration safety is about evolving the schema while the application continues to serve traffic. The core requirements:

- **Versioned**: Every schema change is a numbered migration that can be applied in order.
- **Reversible**: Every migration has a rollback/down migration that undoes it.
- **Compatible**: The migration doesn't break the currently running application code (backward compatibility).
- **Non-blocking**: The migration doesn't lock tables or block queries for extended periods.
- **Tested**: The migration is tested against production-like data before production deployment.

The expand/contract pattern for zero-downtime migrations:
1. **Expand**: Add the new column/table/index. Don't remove anything. Both old and new code work.
2. **Migrate data**: Backfill the new column with data from the old structure.
3. **Transition**: Deploy code that writes to both old and new, reads from new.
4. **Contract**: Remove the old column/table once all code uses the new structure.

The practical implications:
- **Schema changes and code changes should be deployed separately.** If they're coupled, a rollback of the code requires rolling back the schema, which may not be safe.
- **Large tables require special handling.** Adding a column to a billion-row table can lock it for hours. Tools like `pt-online-schema-change`, `gh-ost`, or `pg_repack` handle this without downtime.
- **Rollback scripts are only useful if tested.** An untested rollback script is wishful thinking. It might have a syntax error, miss a dependency, or corrupt data.

---

## §2 The expert's mental model

When I review a migration, I think about what happens during deployment. The migration runs while the old code is still handling requests. Then the new code deploys while the migration has already run. Both code versions must work with the schema at each step.

**What I look at first:**
- The migration type. Is it additive (add column, add table) or destructive (drop column, change type, add NOT NULL)? Additive is safe. Destructive is dangerous.
- The table size. Adding a column to a 100-row table is instant. Adding a column to a 100-million-row table might lock the table for minutes to hours, depending on the database engine.
- The rollback migration. Does it exist? Is it the inverse of the up migration? Has anyone run it?
- Data migration coupling. Does the schema migration also backfill data? Data migrations on large tables should be separate, chunked operations.

**What triggers my suspicion:**
- Migrations that drop columns or tables. If the old code references them and the rollback deploys old code, the code breaks immediately.
- `ALTER TABLE ... NOT NULL` on columns with existing null data. The migration will fail, or it will set a default you didn't intend.
- Index creation on large tables without `CONCURRENTLY` (PostgreSQL) or equivalent. Non-concurrent index creation locks the table for writes.
- Migrations that run raw SQL with no transaction wrapper. If the SQL fails halfway, the schema is in an indeterminate state.
- No migration testing environment with production-scale data. A migration that takes 1 second on 1,000 rows might take 1 hour on 100 million rows.

**My internal scoring process:**
I classify each migration by risk: low (additive, small table), medium (additive, large table), high (destructive, any table), critical (destructive, large table, live traffic). Each level requires different review and testing rigor.

---

## §3 The audit

### Migration framework and process
- Is there a **migration framework** (Flyway, Alembic, Knex, Prisma, ActiveRecord) managing schema changes?
- Are migrations **versioned and ordered** (numbered or timestamped)?
- Are migrations stored in **version control** alongside the application code?
- Is there a **review process** for migrations before they're applied to production?
- Is there a **staging environment** where migrations are tested with production-scale data?

### Backward compatibility
- Does the migration maintain **backward compatibility** with the currently deployed code?
- For column additions: does the old code **handle the new column's absence** (or is the column nullable/defaulted)?
- For column removals: is the old code **no longer referencing** the column before it's dropped?
- For column renames: is the rename done via **expand/contract** (add new, copy data, drop old) rather than a direct rename?
- For type changes: is the change **compatible** (widening VARCHAR) or **incompatible** (changing INT to UUID)?

### Reversibility
- Does every migration have a **down/rollback** migration?
- Is the rollback migration **tested** (not just written)?
- Is the rollback **safe for data**? (Dropping a column that was just added is fine. Adding back a column that was just dropped... where's the data?)
- For **data migrations** (backfills): is the rollback possible? (Once you've transformed data, can you un-transform it?)
- Is there a **process for executing a rollback** in production? (Not just "run the down migration" — who decides, who executes, what's the blast radius?)

### Non-blocking execution
- For **large tables**: does the migration use online schema change tools (`pt-online-schema-change`, `gh-ost`, `pg_repack`, `CONCURRENTLY`)?
- Does the migration avoid **exclusive table locks** that block reads or writes?
- For **index creation on large tables**: is `CREATE INDEX CONCURRENTLY` (or equivalent) used?
- Is the **migration execution time** estimated? Migrations that take more than a few seconds need special handling.
- Are **data backfills** done in batches (not a single UPDATE on all rows)?

### Data integrity during migration
- If the migration **adds a NOT NULL constraint**: is existing data verified to have no nulls first?
- If the migration **changes a column type**: is existing data compatible with the new type?
- If the migration **adds a foreign key**: do all existing references point to valid records?
- If the migration **adds a unique constraint**: are there existing duplicates that would violate it?
- Is the migration **wrapped in a transaction** (where supported) for atomicity?

### Migration testing
- Are migrations **tested in a staging environment** with production-scale data volumes?
- Is the **migration execution time** measured in staging to predict production behavior?
- Is the **rollback** tested in staging?
- Are **integration tests** run after the migration to verify the application still works?
- For **destructive migrations**: is there a data backup taken before execution?

---

## §4 Pattern library

**The coupled migration** — A migration drops a column, and the code change that stops reading the column is in the same deployment. If the migration runs before the new code is live, the old code crashes. If the code deploys before the migration, it works but the migration is now out of order. Fix: expand/contract. Remove the code reference first. Deploy. Then drop the column.

**The NOT NULL surprise** — `ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL`. The table has 50,000 users without phone numbers. The migration fails. Fix: add the column as nullable, backfill data (or set a default), then add the NOT NULL constraint.

**The table-locking index** — `CREATE INDEX idx_orders_status ON orders(status)` on a table with 50 million rows. The table is locked for 20 minutes. No writes succeed. Fix: `CREATE INDEX CONCURRENTLY` (PostgreSQL) or online DDL (MySQL 8+).

**The big-bang data migration** — `UPDATE users SET new_email = LOWER(old_email)` on 10 million rows. One transaction, one statement. It locks the table, fills the WAL, and the migration times out. Fix: batch the update in chunks of 1,000-10,000 rows with brief pauses between batches.

**The untested rollback** — The rollback migration was written six months ago and never tested. During an incident, the team runs it. It has a syntax error on line 3. Fix: test rollbacks as part of the migration CI pipeline.

**The orphan constraint** — A foreign key constraint is added from `orders.customer_id` to `customers.id`. But there are 500 orders with `customer_id` values that don't exist in `customers` (from a bug three months ago). The migration fails. Fix: check for orphan references before adding the constraint.

---

## §5 The traps

**The "we always have downtime" trap** — Accepting that deployments require a maintenance window. For many modern applications, zero-downtime deployment is expected. Schema changes that require downtime limit deployment frequency and create pressure to batch changes (which increases risk).

**The "it's just adding a column" trap** — Adding a column IS safe for small tables. For a 100-million-row table in PostgreSQL, adding a column with a default used to rewrite the entire table (pre-PG11). Know your database engine's behavior for DDL operations.

**The "we'll fix the data later" trap** — Deploying a migration with known data inconsistencies ("we'll backfill the phone numbers next sprint"). Next sprint never comes. The inconsistency becomes permanent. Fix: data cleanup is part of the migration, not a follow-up.

**The "rollbacks are for cowards" trap** — Not writing rollback migrations because "we never roll back." Until you need to, at 2 AM, during an incident. Rollbacks are insurance. Write them. Test them. Hope you never need them.

**The "migration = deployment" trap** — Tying migration execution to the application deployment process. If the migration fails, the deployment fails, and the rollback includes both code and schema — which may leave the database in an indeterminate state. Run migrations and deployments as separate steps.

---

## §6 Blind spots and limitations

**Migration safety is database-engine-specific.** PostgreSQL's DDL-in-transaction support is very different from MySQL's online DDL behavior. Migration strategies that are safe on one engine may be dangerous on another.

**Migrations can't prevent application bugs.** A safe, backward-compatible migration doesn't prevent the new code from having bugs. The migration provides a safe schema evolution; the code must be separately tested.

**Migration testing with production data has privacy implications.** Testing with a copy of the production database means the test environment has real user data. Anonymization/masking may be required for compliance.

**Some migrations are genuinely irreversible.** Splitting a table, normalizing a denormalized structure, or migrating from one database engine to another may not have practical rollbacks. Acknowledge this explicitly and have a forward-fix plan.

---

## §7 Cross-framework connections

| Framework | Interaction with migration safety |
|-----------|----------------------------------|
| **Data Model Design** | Migrations implement changes to the data model. Good model design requires fewer risky migrations. |
| **Health Checks** | Long-running migrations should be reflected in the readiness probe — the service may not be ready to serve during migration. |
| **Logging and Observability** | Migration execution should be logged: start time, completion time, duration, success/failure. |
| **Transaction Management** | Migrations should be wrapped in transactions where supported. For DDL that can't be transactional, compensating actions should be planned. |
| **Background Jobs** | Large data backfills are often implemented as background jobs with batching, progress tracking, and retry logic. |
| **Query Efficiency** | Index additions/removals directly affect query efficiency. Plan index changes alongside query pattern changes. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (risk) |
|---------|-------------------|---------------------|-----------------|
| **Small tables (<100K rows)** | No rollback migration | Non-concurrent index creation | DROP COLUMN without checking code references |
| **Large tables (>1M rows)** | Suboptimal batch size | Missing staging test | Table-locking DDL on live traffic |
| **Zero-downtime requirement** | Minor schema naming issues | Coupled migration and code deploy | Migration requires maintenance window |
| **Multi-service DB** | Migration order dependency unclear | No backward compatibility check | Breaking change without coordinating with dependent services |
| **Regulated environment** | Missing migration documentation | No pre-migration data backup | Untested rollback for irreversible migration |

**Severity multipliers:**
- **Table size**: Risk scales with row count. A safe pattern on 1,000 rows may be dangerous on 100 million.
- **Traffic volume**: Migrations during high traffic amplify the impact of table locks.
- **Rollback complexity**: Simple rollbacks (drop the new column) are low risk. Complex rollbacks (un-split a table) are high risk.
- **Data sensitivity**: Migrations on financial or healthcare data require extra caution and testing.

---

## §9 Build Bible integration

| Bible principle | Application to migration safety |
|-----------------|-------------------------------|
| **§1.9 Atomic operations** | Migrations should be atomic — succeed completely or fail completely. A half-applied migration is worse than a failed migration. Use transactions where supported. |
| **§1.8 Prevent, don't recover** | Test migrations with production-scale data in staging to prevent production failures. Discovering that a migration locks a table for 30 minutes in production is recovery, not prevention. |
| **§1.7 Checkpoint gates** | Complex migrations (multi-step expand/contract) should have explicit checkpoints: schema expanded ✓ → data backfilled ✓ → code transitioned ✓ → old schema contracted ✓. |
| **§1.13 Unhappy path first** | What happens when the migration fails halfway? When the rollback is needed? When the data has unexpected values? Plan for these before running the migration. |
| **§1.10 Document when fresh** | Document the migration's purpose, risk assessment, and rollback plan when you write the migration, not during the incident when it fails. |
| **§6.10 Unenforceable punchlist** | A "post-migration cleanup" list that nobody checks is the unenforceable punchlist. Put cleanup steps in the migration itself or track them with hard deadlines. |
