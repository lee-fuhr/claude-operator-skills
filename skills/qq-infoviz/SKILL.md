---
name: qq-infoviz
description: Generate branded LinkedIn data visualizations (1200x627) using HTML/CSS and Playwright screenshots. Supports bar charts, stat grids, vertical columns, newspaper layouts, and quote+stat formats.
triggers:
  - make me a chart
  - make a chart
  - create a visualization
  - infoviz
  - LinkedIn chart
  - LinkedIn image
  - data viz
  - generate a chart
metadata:
  filePattern: []
  bashPattern: []
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Infoviz: branded data visualization skill

Generate editorial-quality LinkedIn post images (1200x627) using HTML/CSS rendered via Playwright.

**Design philosophy:** data IS the point. Every pixel communicates information. Exaggerated sizes, big beautiful serif numbers, tinted labels. Think editorial magazine, not data science notebook.

## Pipeline

1. **Get the data**: pull from your own data source (see below), use data provided in conversation, or derive it from context
2. **Pick a chart type**: bars, grid, columns, newspaper, or quote+stat
3. **Generate HTML**: write a self-contained HTML file to `/tmp/infoviz-chart.html`
4. **Screenshot**: `python3 ~/.claude/skills/qq-infoviz/screenshot.py /tmp/infoviz-chart.html /tmp/chart-linkedin.png 1200 627` (pass width/height explicitly: the script defaults to a 1800x1800 square, which doesn’t match the 1200x627 canvas this skill designs for)
5. **Show the result**: open `/tmp/chart-linkedin.png` in your OS’s image viewer (`open` on macOS, `xdg-open` on Linux) so a human actually looks at it. Don’t just read the file as terminal text.
6. **Iterate**: adjust and re-screenshot

## Brand system

### Canvas
- **Dimensions:** 1200x627px (LinkedIn optimal 1.91:1)
- **Background:** `#0f172a` (dark navy / slate-900)
- **Padding:** 48px left/right (symmetric, both sides must match)

### Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,300;8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Typography scale (converged through 5 rounds)
| Element | Font | Size | Weight | Notes |
|---------|------|------|--------|-------|
| **Title** | Source Serif 4 | 46px | 300 (light), 600 (bold keywords) | Centered, fills ~10/12 cols width |
| **Numbers (grid/cols)** | Source Serif 4 | 56-58px | 700 | Colored per stat |
| **Numbers (bars)** | Source Serif 4 | 40px | 700 | In separate column |
| **Numbers (hero)** | Source Serif 4 | 100px | 700 | Dominant element |
| **Labels** | Inter | 18-19px | 700 | Tinted with parent hue color |
| **Bar labels** | Inter | 16px | 600 | Sentence-flow (reads as continuation of number) |

### Color palette
```
Stat     Number    Accent    Label (tinted)
Red      #f87171   #ef4444   #fecaca
Orange   #fb923c   #f97316   #fed7aa
Amber    #fbbf24   #eab308   #fef08a
Blue     #60a5fa   #3b82f6   #bfdbfe
Purple   #a78bfa   #8b5cf6   #ddd6fe
Indigo   #818cf8   #6366f1   #c7d2fe
Teal     #2dd4bf   #14b8a6   (derive)
Green    #4ade80   #22c55e   (derive)
```

### Fill patterns (4 winners from pattern battle)
All fills go **bottom-up**. Pattern applies **only to the filled area**, not the entire cell.

```css
/* 1. diag, standard diagonal stripes */
background: repeating-linear-gradient(-45deg,
  rgba(R,G,B,0.12) 0px, rgba(R,G,B,0.12) 3px,
  rgba(R,G,B,0.28) 3px, rgba(R,G,B,0.28) 8px);

/* 2. diag-med, medium diagonal (denser) */
background: repeating-linear-gradient(-45deg,
  rgba(R,G,B,0.11) 0px, rgba(R,G,B,0.11) 2px,
  rgba(R,G,B,0.27) 2px, rgba(R,G,B,0.27) 5.5px);

/* 3. diag-wide, bold diagonal bands */
background: repeating-linear-gradient(-45deg,
  rgba(R,G,B,0.08) 0px, rgba(R,G,B,0.08) 5px,
  rgba(R,G,B,0.26) 5px, rgba(R,G,B,0.26) 14px);

/* 4. dots, dense stipple */
background: radial-gradient(circle,
  rgba(R,G,B,0.4) 1.5px, rgba(R,G,B,0.1) 1.5px);
background-size: 6px 6px;

/* flat, solid fill (no pattern) */
background: rgba(R,G,B,0.28);
```

### Wavy edge (optional)
Apply via clip-path on the fill element:
```css
clip-path: polygon(
  0% 10%, 12% 5%, 25% 12%, 38% 3%, 50% 9%,
  62% 2%, 75% 11%, 88% 4%, 100% 8%,
  100% 100%, 0% 100%
);
```
When using wavy, add ~5% extra height to the fill to compensate for the wave.

### Accent stripe
- 4px wide, left edge of cell/bar, full height
- Straight (not curved), clipped by parent’s border-radius via `overflow: hidden`
- Full opacity accent color

### Footer
- Height: 48px, no HR/border above it
- Left: source label (9px uppercase, slate-600) + detail (8px, slate-700)
- Right: your site or handle (11px, slate-500) + your logo or headshot (52px circle, margin-top -8px, no border)

### Logo/headshot embedding
Always base64-encode (cloud-synced file paths, e.g. iCloud or Google Drive, break in Playwright since it can’t authenticate to fetch them):
```python
import base64
from pathlib import Path
logo_path = Path('/path/to/your/logo-or-headshot.png')
logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
```

## Chart types

### 1. Horizontal bars
Best for: ranked metrics, 4-6 stats, “what’s missing” stories.

- **Sentence-flow labels**: read as continuation of the number, “85% don’t name a single machine they run”
- Number in separate column (110px, right-aligned), bar track fills remaining width
- Bar track: `rgba(255,255,255,0.03)`, 6px border-radius
- Bar fill: reversed gradient (transparent to color), **rounded right corners** (`border-radius: 0 6px 6px 0`)
- 4px accent stripe on left edge of track
- Gaps: 2px between rows
- Padding: symmetric left and right

### 2. Stat grid (3x2 or 2x3)
Best for: 6 equal-weight stats as a scorecard.

- Grid of cells, 6px gaps, 8px border-radius
- Each cell: unfilled bg `rgba(255,255,255,0.03)`, fill element inside (bottom-up, pattern or flat)
- Fill height = percentage value
- 4px accent stripe, left edge
- Number + tinted label anchored to bottom of cell
- Bottom-up fill preferred over left-right

### 3. Vertical columns (staircase)
Best for: showing relative scale, descending data.

- 6 columns, descending height = percentage
- Each column: full-height container with `rgba(255,255,255,0.04)` unfilled bg
- Fill element inside: height = percentage, pattern or flat
- Number + label inside the fill, anchored to top of fill
- No accent stripe on columns
- 6px gaps between columns, 8px border-radius

### 4. Newspaper (hero + strip)
Best for: one dominant stat + supporting context.

- Top: hero cell (bigger, ~1.2fr) with the headline stat, label, and subtitle
- Bottom: 5-column strip of supporting stats
- All fills bottom-up
- Bottom row: **numbers baseline-aligned** (position: absolute, fixed bottom offset) so labels don’t push numbers around

### 5. Quote + stat strip
Best for: provocative copy backed by data.

- Top: pull quote (Source Serif 4, 34px) with italic red emphasis word
- Bottom: 3-column stat strip with accent stripes and fills
- Quote mark: Source Serif 4, 56px, slate-800

### 6. Top 3 bold
Best for: 3 hero stats, no bar chart needed, maximum visual impact.

- 3 equal columns, each with massive number (90px), full sentence label, optional subtitle
- Vertical gradient fills (bottom-up)
- Accent stripes on left edge

## Data sources

### Your own data source

If you keep a local database with the stats you want to chart (SQLite, a CSV, an analytics export, whatever), query it directly rather than guessing at numbers. Adapt table and column names to your own schema. Example pattern using SQLite:

```python
import sqlite3
conn = sqlite3.connect('/path/to/your/data.db')
cursor = conn.execute("SELECT column_a, column_b FROM your_table WHERE ...")
```

**Flag for whoever adopts this skill:** the original version of this pipeline step queried one specific private database with a hardcoded absolute path and a fixed table schema. That’s a real functional dependency, not just prose, so it can’t be copied as-is; wire it to wherever your own numbers actually live.

### Manual data

Data provided directly in conversation: percentages, counts, labels.

## Anti-patterns
- No matplotlib: HTML/CSS pipeline only
- No warm/artisanal aesthetics: professional services feel
- No “data science notebook” aesthetic: editorial/magazine
- No small labels: push toward “too big,” data IS the point
- No top-down fills: always bottom-up
- No soft/blurred fill edges: clean or wavy only
- No diagonal fill edges: wavy or flat only
- No footer HR: clean separation
- No headshot border: just shadow
- Don’t guess at data: query your data source or ask for the real numbers
- Don’t use local file paths for images: always base64 encode
- Don’t dump charts as terminal text: always open the image in a viewer

## Design principles
1. **Every pixel communicates**: minimize whitespace, maximize information density
2. **Grid adherence**: structured layouts, consistent spacing, symmetric padding
3. **Info hierarchy**: title > numbers > labels > source. Each level visually distinct.
4. **Define spaces, anchor elements**: title centered in its space, padding matches on both sides
5. **Sentence-flow labels**: “85% don’t name their machines,” not “85% | No machines named”
6. **Exaggerated scales**: big fonts show font beauty, data IS the point
7. **LinkedIn thumb test**: must be readable and eye-catching at small size while scrolling
8. **Fewer stats bigger**: 3 huge stats beat 6 tiny stats for LinkedIn engagement

## Quality checklist
- [ ] 1200x627px exact
- [ ] Title fills ~10/12 cols width (46px)
- [ ] Labels are BIG (18-19px) and tinted with parent hue
- [ ] Numbers are beautiful (Source Serif 4, 700 weight)
- [ ] Padding symmetric left/right
- [ ] Fills bottom-up, pattern only in filled area
- [ ] Accent stripes full-height, clipped by parent radius
- [ ] Footer: no HR, headshot has no border, 48px height
- [ ] Opened in an image viewer for a human to actually look at (not just read as terminal text)
- [ ] Visually verified via the Read tool before treating it as done
