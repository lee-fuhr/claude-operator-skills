# Data visualization, temporal, and provenance patterns

Detailed patterns and anti-patterns for chart selection, timestamp/freshness display, and data provenance.

## Data visualization patterns

### Chart selection guide

| Data type | Correct chart | Incorrect alternatives |
|-----------|--------------|----------------------|
| Time-series (trend) | Line chart, area chart | Bar chart (implies value, not trend) |
| Part-to-whole | Stacked bar, 100% stacked bar | Pie chart (humans cannot compare arc lengths) |
| Category comparison (single value) | Column chart, bar chart | Donut chart, spider chart |
| Distribution | Histogram, box plot | Line chart (implies continuity) |
| Correlation | Scatter plot | Line chart (implies causation) |
| Status (discrete states) | Badge, dot with label | Any quantitative chart |

### Pattern: dual encoding for status

Never encode status in color alone. Use color + shape + text label in combination. See Iron Law 2.

### Pattern: density calibration by view level

- **Overview:** sparklines (tiny time-series) showing range + current value. No axes, no labels.
- **Section:** bar charts or line charts with labeled axes, last-value annotation.
- **Item:** full time-series with all data points, zoomed range selector.
- **Raw:** table view with sortable columns.

### Pattern: stale data indicator

Data older than 5 minutes must show age. Data older than 1 hour must show visual differentiation (reduced opacity or “stale” badge) plus age. See Iron Law 3.

### Anti-pattern: misleading zero-baseline suppression

Starting a y-axis at a non-zero value to make a small change look large. Always start at zero for absolute values. Use indexed or percentage change for relative comparisons.

### Anti-pattern: unlabeled aggregate

A single number with no indication of what aggregation produced it. “Requests: 4,231”, is this per second? Per minute? Total today? Always label the unit and period.

---

## Temporal patterns

### Pattern: timestamp proximity to metric

The timestamp for a metric must appear adjacent to the metric value, not in a footer or “last updated” section shared across all metrics. When metrics have different freshness, each must show its own age.

### Pattern: delta with direction and context

“↑ 10%” means nothing without context. Required format:

```
↑ 10% (latency worse, was 200ms, now 220ms)
↓ 5%  (error rate better, was 2.1%, now 2.0%)
```

Direction arrow + percentage + plain-language label that answers “is this good or bad?”

### Pattern: state age vs. refresh age

These are different and both must be visible:
- **State age:** how old is the underlying data? (“Data from 2 hours ago”)
- **Refresh age:** when did the dashboard last check for new data? (“Checked 10 seconds ago”)

Refreshing a stale cache does not make the data fresh. The dashboard may be actively polling stale data.

---

## Data provenance patterns

### Pattern: real vs. demo data differentiation

Demo or synthetic data in a production dashboard must carry a visible watermark: “DEMO” text at 10% opacity, rotated 45°, behind all content. Never indistinguishable from real data.

**Enforcement:** `data-source="demo"` attribute on any demo data element. Design system renders the watermark automatically for this attribute. Automated build check: no `demo` data in production builds without a watermark.

### Pattern: real-time vs. batch distinction

Real-time data (WebSocket, SSE, under 30 second latency): show a “Live” badge.
Batch data (hourly, daily job): show “as of [timestamp]” with the batch job’s last run time.

Never show batch data next to a “Live” badge or without an “as of” label. The freshness guarantee is different and the user must know.

### Pattern: aggregate constituent visibility

Health scores and composite metrics must expose their components. “System health: 87%” must link to (or expand to show) the constituent values: CPU 90%, Memory 85%, Disk 80%, Network 90%.

Components must be **sortable by severity** (not alphabetical). The worst component appears first. Average-up aggregates that hide degraded subsystems are anti-patterns.

### Anti-pattern: demo data indistinguishable from live

The dashboard looks the same in demo and production mode. New users cannot tell if they’re looking at real data.

### Anti-pattern: weighted health score hiding corruption

“System health: 95%”: everything looks fine. But disk is at 15% free and filling at 500MB/day. The weighted average masks the one metric about to cause an outage.
