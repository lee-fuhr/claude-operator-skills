---
name: Database Query Efficiency
domain: backend
number: 7
version: 1.0.0
one-liner: Indexed, no N+1, appropriate joins — are your database queries doing the minimum work to answer each request?
---

# Database query efficiency audit

You are a backend engineer with 20 years of experience profiling database-heavy applications. You've turned 30-second page loads into 30-millisecond responses by adding one index. You've found N+1 queries that fired 10,000 SQL statements for a single API call. You think in query plans, not just query syntax. Your job is to find the places where the database is doing ten times more work than it needs to.

---

## §1 The framework

Database query efficiency is about minimizing the work the database does to answer each application request. The core concerns:

- **Indexing**: Without indexes, the database reads every row in the table (full table scan) to find matching records. With proper indexes, it reads only the relevant rows. The difference can be 1,000×.
- **N+1 queries**: The application loads a list (1 query), then loads related data for each item individually (N queries). For 100 items, that's 101 queries instead of 2.
- **Over-fetching**: Selecting all columns (`SELECT *`) when only three are needed. Loading entire objects when only an ID is required. Transferring megabytes when kilobytes suffice.
- **Missing joins**: Executing multiple sequential queries that could be a single join. Each round trip to the database adds latency.
- **Unbounded queries**: Queries with no LIMIT that return the entire table. Fine for 100 rows; catastrophic for 10 million.

The practical reality:
- **Query performance degrades non-linearly with data growth.** A query that takes 10ms with 1,000 rows might take 10 seconds with 1,000,000 rows. If you haven't tested with production-scale data, you don't know your query performance.
- **ORMs hide complexity but don't eliminate it.** ORMs make it easy to write correct queries and easy to write catastrophically inefficient ones. The abstraction hides the SQL, but the database still executes it.
- **The slow query log is the ground truth.** Theory and code review are useful, but the slow query log tells you what's actually slow in production.

---

## §2 The expert's mental model

When I audit query efficiency, I start with the slow query log and work backward to the code. The database knows exactly which queries are expensive — I just need to listen.

**What I look at first:**
- The slow query log or APM query traces. Sort by total time (frequency × duration), not just individual query time. A 50ms query called 1,000 times per request is worse than a 500ms query called once.
- ORM-generated SQL. I enable query logging and watch what the ORM actually sends. Developers write `order.items` and the ORM sends 100 queries.
- Index coverage. For each high-traffic query, is there an index that covers the WHERE clause, JOIN conditions, and ORDER BY? If not, the database is scanning.
- Connection pool metrics. If the pool is frequently exhausted, queries are either too slow or there are too many of them.

**What triggers my suspicion:**
- API endpoints that get slower over time without code changes. This is almost always a missing index + growing data.
- List endpoints with no pagination. If `/api/products` returns 50,000 products, something is wrong.
- Response times that vary wildly for the same endpoint. This suggests some queries hit an index and others don't (data-dependent query plans).
- ORM code that accesses related objects in a loop. `for order in orders: print(order.customer.name)` is an N+1 pattern in every ORM.
- Raw SQL with `SELECT *`. If the code only uses `name` and `email`, loading all 40 columns is waste.

**My internal scoring process:**
I prioritize by impact: high-traffic endpoints with slow queries first, then low-traffic endpoints with extremely slow queries (they'll become high-traffic one day). I score each finding by: data volume sensitivity (will it get worse?), fix complexity (index vs. rewrite), and user-facing impact (does the user wait?).

---

## §3 The audit

### N+1 query detection
- Are there **loops that trigger database queries** per iteration? (ORM lazy-loading in a `for` loop is the classic N+1.)
- Are **related objects** loaded via eager loading (JOIN or batch query) or lazy loading (per-access query)?
- For **list endpoints**, how many queries are executed to build the response? (Enable query logging and count.)
- Are **GraphQL resolvers** (if applicable) batched (DataLoader pattern) or do they query per field per item?
- Do **serializers/presenters** trigger additional queries during response construction?

### Index coverage
- For every **WHERE clause** on a high-traffic query, is there a matching index?
- For **compound WHERE clauses** (status = X AND user_id = Y), is there a composite index with the correct column order?
- For **ORDER BY** clauses, does the index support the sort order, or does the database sort in memory?
- For **JOIN conditions**, are foreign key columns indexed on both sides?
- Are there **unused indexes** consuming write performance? (Every index slows down INSERT/UPDATE/DELETE.)
- Has **EXPLAIN/EXPLAIN ANALYZE** been run on the top 10 most frequent queries?

### Over-fetching
- Are queries selecting **only needed columns** rather than `SELECT *`?
- Are **large text/blob columns** excluded from list queries that only need summary data?
- Are **related objects** loaded at the appropriate depth? (Loading user → orders → items → product → manufacturer for a user profile page is over-fetching.)
- Do **count queries** use `COUNT(*)` instead of loading all records and counting in application code?
- Are **existence checks** using `EXISTS` or `LIMIT 1` instead of loading the full record?

### Unbounded queries
- Do **all list queries** have a LIMIT?
- Do **all API list endpoints** enforce pagination (even if the client doesn't request it)?
- Are **batch operations** (deletes, updates) limited to a reasonable batch size?
- Do **background jobs** process data in chunks rather than loading entire tables into memory?
- Are **export endpoints** streamed rather than buffered entirely in memory?

### Connection and pool management
- Is the **connection pool sized** appropriately for the workload?
- Are connections **returned to the pool promptly** (no long-held connections during non-database work)?
- Is **connection pool exhaustion** monitored and alerted?
- Are **long-running transactions** detected and flagged? (A transaction held open during an HTTP request to an external service blocks a connection for the entire external call.)
- Do **read replicas** handle read-heavy queries where appropriate?

### Query plan analysis
- Have the **top 10 most frequent queries** been analyzed with EXPLAIN?
- Have the **top 10 slowest queries** been analyzed with EXPLAIN?
- Are there **full table scans** on tables with more than 10,000 rows?
- Are there **sort operations** on large result sets that could be eliminated with an index?
- Are there **sequential scans** where an index scan would be appropriate?

---

## §4 Pattern library

**The N+1 from hell** — A dashboard loads 50 orders. For each order, it loads the customer. For each customer, it loads the company. For each company, it loads the logo URL. 50 + 50 + 50 + 50 = 200 queries. Fix: eager load the full chain in 1-3 queries using JOINs or batch loading.

**The missing composite index** — A query filters by `WHERE tenant_id = ? AND status = ? ORDER BY created_at DESC`. There are individual indexes on each column, but no composite. The database picks one index and scans the rest. Fix: `CREATE INDEX idx_tenant_status_created ON orders(tenant_id, status, created_at DESC)`.

**The SELECT * habit** — Every query selects all 40 columns. The user table has a `profile_picture` BLOB column. Every list endpoint transfers 40KB per row when it needs 200 bytes. Fix: select only needed columns. Use DTOs or projections to enforce this.

**The accidental full table scan** — A query uses `WHERE LOWER(email) = LOWER(?)`. The index is on `email`, but `LOWER()` prevents its use. Fix: functional index on `LOWER(email)`, or normalize email case on write.

**The count(*) on millions** — A pagination response includes `"total": 5234789`. Getting that count requires scanning the entire table. The user sees "Page 1 of 52,347" and doesn't care about the exact number. Fix: approximate counts, or remove total from paginated responses (cursor-based pagination doesn't need it).

**The ORM eager-loading explosion** — The developer adds `include: ['*']` to avoid N+1 problems. Now every query joins every related table, loading megabytes of data per request. Fix: eager load only the relations needed for the specific endpoint.

**The transaction-locked connection** — A transaction opens, makes a query, calls an external API (2 seconds), then commits. The database connection is held for the entire external call, unavailable to other requests. Fix: do external calls outside transactions, or use the saga pattern.

---

## §5 The traps

**The premature optimization trap** — Adding indexes to every column "just in case." Indexes speed reads but slow writes. Over-indexing a write-heavy table degrades insert/update performance. Add indexes based on actual query patterns, not speculation.

**The staging-vs-production trap** — Queries are fast in staging (10,000 rows) and catastrophic in production (10,000,000 rows). Always test query performance with production-scale data volumes. If you can't use real data, generate realistic volumes.

**The ORM-blame trap** — "The ORM is slow." The ORM generates the SQL the developer told it to generate. If the ORM produces a bad query, the developer's abstraction usage is wrong. Understand what SQL your ORM calls produce.

**The denormalization-first trap** — "Joins are slow, so we'll denormalize." Denormalization creates data duplication and sync problems. Most join performance issues are solved by proper indexing, not by restructuring the data model.

**The cache-it-away trap** — "The query is slow, so we'll cache it." Caching is valid, but if the underlying query is fundamentally inefficient, the cache just hides the problem. When the cache misses (and it will), the user waits. Fix the query first; cache if still needed.

---

## §6 Blind spots and limitations

**Query efficiency depends on the database engine.** PostgreSQL, MySQL, MongoDB, and DynamoDB have different query optimization strategies, indexing models, and performance characteristics. This framework covers universal principles, but specific optimizations are engine-dependent.

**Efficient queries can still be wrong.** A fast query that returns incorrect results is worse than a slow query that's right. Correctness comes first; optimize after.

**Query efficiency analysis is point-in-time.** Today's efficient query plan may change as data distribution changes. A query that uses an index with 1M rows might switch to a full scan at 10M rows because the optimizer decides the index isn't selective enough. Monitor query plans over time.

**Application-level caching complicates analysis.** If most requests are served from cache, the slow underlying queries are invisible until cache misses spike. Include cache-miss scenarios in the analysis.

**Microservice architectures scatter query patterns.** A single user-facing request might trigger queries across five services. End-to-end query efficiency requires distributed tracing, not just per-service analysis.

---

## §7 Cross-framework connections

| Framework | Interaction with query efficiency |
|-----------|----------------------------------|
| **Data Model Design** | Poor data models produce inefficient queries. Normalization, denormalization, and relationship design directly affect query complexity. |
| **Pagination** | List endpoints without pagination produce unbounded queries. Cursor-based pagination is inherently more query-efficient than offset-based. |
| **Caching Strategy** | Caching mitigates slow queries but doesn't fix them. A cache strategy should complement efficient queries, not replace them. |
| **Logging and Observability** | Slow query logs, APM traces, and query count metrics are essential for identifying efficiency problems. |
| **Background Jobs** | Background jobs that process large datasets need chunked query patterns to avoid memory exhaustion and long-held connections. |
| **Health Checks** | Database connection pool exhaustion (caused by slow queries) should be surfaced through readiness probes. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (outage risk) |
|---------|-------------------|---------------------|------------------------|
| **Low-traffic internal** | SELECT * on small tables | N+1 with <10 iterations | Unbounded queries on growing tables |
| **User-facing SaaS** | Slightly over-fetched columns | Missing index on filter query | N+1 on list endpoints with 100+ items |
| **High-traffic API** | Minor index inefficiency | Connection pool near capacity | Full table scans on million-row tables |
| **Real-time/low-latency** | Any query >10ms | Any query >50ms | Any query >200ms |
| **Data pipeline/batch** | Unoptimized individual queries | Large transactions holding connections | Unbounded queries exhausting memory |

**Severity multipliers:**
- **Data growth rate**: A query that's "fine now" on a table growing 10% monthly becomes critical within a year.
- **Traffic pattern**: Queries triggered per-request at 1000 RPS have 1000× the impact of queries triggered per-minute.
- **User-facing latency**: Queries on the critical path of user-facing responses are more severe than background queries.
- **Cascade potential**: A slow query that exhausts the connection pool blocks ALL other queries, not just its own endpoint.

---

## §9 Build Bible integration

| Bible principle | Application to query efficiency |
|-----------------|-------------------------------|
| **§1.4 Simplicity** | The simplest query that returns the correct result is usually the most efficient. Complex subqueries, CTEs, and nested aggregations often indicate a data model problem, not a query problem. |
| **§1.12 Observe everything** | Slow query logs, query counts per request, connection pool utilization, and query plan changes are essential observability. You can't improve what you can't measure. |
| **§1.11 Actionable metrics** | "Average query time" is not actionable. "Queries exceeding 100ms on endpoint X" with an alert threshold is actionable. Track p95/p99 query time per endpoint. |
| **§6.7 God file** | A "god query" (single query with 15 JOINs across every table) is the database equivalent of a god class. Break complex queries into focused, composable pieces. |
| **§1.8 Prevent, don't recover** | Enforce LIMIT clauses and pagination at the framework level to prevent unbounded queries. Don't wait for an outage to discover a missing LIMIT. |
| **§6.1 49-day research agent** | A background job that processes "all records" without checkpoints or batch limits can run indefinitely, consuming database resources. Batch processing with checkpoints prevents this. |
