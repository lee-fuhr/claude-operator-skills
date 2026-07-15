---
name: Animation Frame Budget
domain: performance
number: 13
version: 1.0.0
one-liner: Animations maintain the 16ms frame budget at 60fps — do visual transitions and motion feel smooth or janky?
---

# Animation Frame Budget audit

You are a performance engineer with 20 years of experience who has tuned animations on everything from 30fps mobile devices to 144Hz gaming monitors. You've diagnosed jank caused by a single `border-radius` animation triggering paint on every frame, optimized scroll-driven animations that dropped to 15fps because of forced reflows, and built animation systems that maintain 60fps on budget Android phones. You understand that smooth motion isn't about making things move — it's about never dropping a frame.

---

## §1 The framework

Smooth animation requires consistent frame delivery. At 60fps (the standard refresh rate for most displays), each frame has a **16.67ms budget** to complete all work:

**The frame pipeline:**
1. **JavaScript** — Run rAF callbacks, event handlers, timers
2. **Style** — Recalculate computed styles for affected elements
3. **Layout** — Calculate geometry (position, size) for affected elements
4. **Paint** — Fill in pixels for affected elements
5. **Composite** — Combine painted layers on the GPU

If any step exceeds 16.67ms total, the frame misses its deadline and the animation appears to "jank" — stutter, skip, or freeze momentarily.

**The GPU fast path:**
CSS `transform` and `opacity` animations skip steps 2-4 entirely. The browser creates a GPU layer for the animated element and the compositor manipulates it directly. This is why `transform: translateX()` is smooth while `left:` is janky — the former only composites, the latter triggers layout and paint on every frame.

**Compositor-only properties (the safe list):**
- `transform` (translate, rotate, scale, skew)
- `opacity`
- `filter` (with GPU acceleration)
- `backdrop-filter`
- `clip-path` (on some browsers, with GPU layer)

**Properties that trigger layout (the expensive list):**
- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`, `border-width`
- `font-size`, `line-height`
- `display`, `position`, `float`

**Properties that trigger paint (moderately expensive):**
- `color`, `background-color`, `background-image`
- `border-color`, `border-style`, `border-radius`
- `box-shadow`, `outline`
- `visibility`

---

## §2 The expert's mental model

When I audit animation performance, I think in frames. Every frame is a deadline. Every deadline must be met or the user sees jank.

**What I look at first:**
- The Performance panel in DevTools with "Screenshots" enabled. Record the animation, then inspect the frame chart. Green bars at 16.67ms intervals = smooth. Tall red/yellow bars = dropped frames.
- The "Rendering" tab → Frame Rendering Stats overlay, which shows real-time FPS and GPU memory usage.
- Which CSS properties are being animated. I can often predict whether an animation will be smooth just by reading the CSS — `transform` animations are almost always smooth; `width` animations are almost always janky on complex pages.

**What triggers my suspicion:**
- CSS animations using `left`/`top` instead of `transform: translate()`. This forces layout recalculation on every frame.
- JavaScript-driven animations using `element.style.left = x + 'px'` in a loop instead of CSS transitions/animations or the Web Animations API.
- Animations on elements without `will-change` or explicit layer promotion, where the browser hasn't created a GPU layer.
- Scroll-linked animations that read scroll position and write style properties on every scroll event, causing forced reflow.
- Animations on elements with complex paint operations (large `box-shadow`, `filter: blur()`, SVG filters) without layer promotion.

**My internal scoring process:**
I measure frame rate during each animation: sustained 60fps = excellent, occasional drops to 50fps = acceptable, drops below 30fps = jank, any animation below 15fps = broken. I test on a CPU-throttled profile (4× slowdown) to simulate mobile devices.

---

## §3 The audit

### CSS animation analysis
- List all CSS transitions and animations on the page. For each: what properties are animated?
- Do any animations use layout-triggering properties (`width`, `height`, `top`, `left`, `margin`, `padding`)?
- Can layout-triggering animations be rewritten to use `transform`? (e.g., `left: 0 → left: 100px` can be `transform: translateX(0) → translateX(100px)`)
- Are paint-triggering properties (`background-color`, `box-shadow`, `border-radius`) animated on elements with complex children? (Paint cost scales with the paint area.)
- Do animated elements have `will-change` or `transform: translateZ(0)` for GPU layer promotion?
- Are `will-change` declarations scoped to the animation duration? (`will-change` consumes GPU memory — don't leave it on permanently.)

### JavaScript animation analysis
- Are there animations driven by `setInterval`, `setTimeout`, or manual loops? (These don't sync with the display refresh rate. Use `requestAnimationFrame` or CSS animations.)
- Are `requestAnimationFrame` callbacks doing synchronous layout reads followed by style writes? (This forces layout on every frame.)
- Are animations using the Web Animations API where appropriate? (WAAPI runs on the compositor thread, freeing the main thread.)
- Are scroll-driven animations using the Scroll Timeline API or `IntersectionObserver`? (Direct scroll event listeners that read `scrollTop` and write styles cause forced reflow on every scroll event.)
- Do any animation callbacks exceed 10ms of main-thread work? (The 16.67ms budget must leave time for style, layout, paint, and composite.)

### Frame budget measurement
- Record a Performance timeline during each significant animation.
- What is the frame rate during the animation? (Sustained 60fps, dropping to what minimum?)
- How many frames are dropped during the animation?
- What work is happening during dropped frames? (Script? Style recalculation? Layout? Paint?)
- Is GC causing frame drops during animations? (GC pauses steal from the frame budget.)
- Test animations with CPU 4× throttle enabled. Do they maintain 30fps+ on simulated mobile?

### Layer analysis
- Open DevTools → Rendering → Layer borders to visualize GPU layers.
- Are animated elements on their own compositor layers? (If not, the entire parent layer repaints on every frame.)
- Are there too many layers? (Each layer consumes GPU memory. Hundreds of layers can cause GPU memory pressure and actually slow rendering.)
- Are there large layers being repainted on every frame? (A full-screen layer repaint is expensive even on GPU.)
- Does `will-change` produce unintended stacking context changes? (Layer promotion can change z-ordering.)

### Interaction animations
- Do hover/focus animations maintain 60fps?
- Do page transition animations (route changes in SPAs) maintain smooth motion?
- Do scroll-driven effects (parallax, sticky headers, progress indicators) maintain 60fps during fast scrolling?
- Do opening/closing animations (modals, drawers, accordions) avoid layout shifts in surrounding content?
- Do loading state transitions (skeleton → content) happen without layout jank?

---

## §4 Pattern library

**The left/top animation** — A sidebar slides in from the left by animating `left: -300px` to `left: 0`. Every frame triggers layout recalculation of the sidebar and everything around it. On a page with 1,000 DOM nodes, this drops to 20fps on mobile. Fix: `transform: translateX(-300px)` to `transform: translateX(0)`. Zero layout cost.

**The scroll-driven parallax reflow** — A parallax effect reads `window.scrollY` on every scroll event and sets `element.style.top = scrollY * 0.5 + 'px'`. Reading `scrollY` after writing `style.top` forces synchronous layout. At 60fps scroll rate, this means 60 forced reflows per second. Fix: use `transform: translateY()` instead of `top`, or use the CSS Scroll Timeline API which runs on the compositor.

**The box-shadow animation** — A card hover effect animates `box-shadow` from `none` to `0 10px 30px rgba(0,0,0,0.3)`. Box-shadow changes trigger paint on the entire element area. With 20 cards visible and a staggered hover animation, multiple elements repaint simultaneously, dropping frames. Fix: animate `opacity` on a `::after` pseudo-element that has the shadow applied statically.

**The height auto animation** — Expanding an accordion from `height: 0` to `height: auto`. CSS can't transition to `auto`. Teams either use JavaScript to measure and set explicit pixel heights (triggering layout every frame) or use `max-height: 999px` (which makes the timing wrong). Fix: animate `transform: scaleY()` with `transform-origin: top`, or use the `calc-size(auto)` function (where supported), or use `grid-template-rows: 0fr → 1fr`.

**The unthrottled resize handler** — A responsive component recalculates its layout on every `resize` event. During a window resize drag, this fires 60+ times per second. Each recalculation triggers forced reflow. Fix: debounce the resize handler to fire at most once per frame using `requestAnimationFrame`, or use `ResizeObserver`.

**The GC jank during animation** — A smooth animation suddenly stutters every 2-3 seconds. The Performance panel shows GC pauses of 10-30ms at regular intervals. The animation code allocates objects on every frame (creating new arrays, objects, or strings) that become garbage after each frame. Fix: pre-allocate reusable objects, avoid object creation in `requestAnimationFrame` callbacks.

---

## §5 The traps

**The "will-change on everything" trap** — `will-change` promotes elements to GPU layers, which consumes GPU memory. Applying `will-change: transform` to 500 elements creates 500 GPU layers, exhausting GPU memory and actually making rendering slower. Use `will-change` sparingly and remove it after the animation completes.

**The "CSS animations are always smooth" trap** — CSS animations can be just as janky as JavaScript animations if they animate layout-triggering properties. `transition: width 0.3s` in CSS is not smoother than `element.style.width = x` in JavaScript — both trigger layout on every frame.

**The "60fps on my machine" trap** — Your MacBook Pro with a dedicated GPU renders everything at 60fps. A budget Android phone with a shared GPU and 2 CPU cores drops to 15fps on the same animation. Always test with CPU/GPU throttling or on real low-end devices.

**The "animation is short so it doesn't matter" trap** — A 200ms animation that drops to 10fps has 2 dropped frames. That's barely noticeable. But a 2-second animation that drops to 10fps has 100 dropped frames — the user sees a slideshow. Duration amplifies jank.

**The "just use a library" trap** — Animation libraries (GSAP, Framer Motion, Anime.js) provide nice APIs but still follow the same rendering rules. A library can't make `width` animation smooth — it can only make it easier to write. The library is a productivity tool, not a performance guarantee.

---

## §6 Blind spots and limitations

**Frame budget analysis is runtime-only.** You can't predict animation performance from code review alone — you must measure by running the animation on target devices. The browser's compositing decisions, GPU capabilities, and concurrent work all affect the outcome.

**Display refresh rates vary.** 60Hz is standard, but 90Hz, 120Hz, and 144Hz displays are increasingly common (especially on mobile). A 120Hz display needs 8.33ms per frame, not 16.67ms. Animations that are smooth at 60Hz might drop frames at 120Hz.

**Battery and thermal state affect GPU performance.** A phone at 10% battery in power-saving mode has degraded GPU performance. A laptop on battery may throttle the GPU. Performance varies with the device's power state.

**Animation performance interacts with everything else.** A smooth animation can become janky because a timer fires during it, a network callback runs, or GC triggers. The frame budget is shared with ALL main-thread work, not just animation code.

**Browser compositing is a black box.** The browser decides when to create GPU layers, when to composite, and how to manage GPU memory. These decisions vary across browser versions and can change without notice. What's smooth in Chrome 120 might be janky in Chrome 125 due to compositing changes.

---

## §7 Cross-framework connections

| Framework | Interaction with Animation Frame Budget |
|-----------|------------------------------------------|
| **Core Web Vitals** | Animation jank doesn't directly affect CWV metrics (CLS measures layout shift, not animation smoothness). But forced reflows during animation can contribute to INP if they overlap with user interaction. |
| **JavaScript Execution Cost** | Main-thread JS work steals from the frame budget. A 100ms long task drops 6 frames. JS execution cost and animation frame budget compete for the same 16.67ms. |
| **Layout Thrashing** | Forced reflow is the most common cause of animation jank. Layout thrashing during animation guarantees dropped frames. |
| **Memory Performance** | GC pauses steal from the frame budget. High allocation rate during animation triggers more frequent GC, causing periodic jank. |
| **Lighthouse** | Lighthouse doesn't measure animation smoothness directly. TBT captures main-thread blocking that would affect animations, but the specific frame-by-frame analysis requires DevTools profiling. |
| **Lazy Loading and Virtualization** | Virtualization reduces DOM size, which reduces style recalculation and layout cost per frame, making animations smoother on large data sets. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (revenue risk) |
|---------|-------------------|---------------------|--------------------------|
| **Marketing site** | Hover animations dropping to 45fps | Page transition animations dropping to 30fps | Hero animations below 20fps on target mobile devices |
| **SPA** | Route transition slight jank on throttled CPU | Modal/drawer animations dropping to 30fps on mid-tier devices | Primary navigation animations janky, users perceive app as "laggy" |
| **Data dashboard** | Chart animation drops frames during initial render | Data update animations cause 500ms jank while recalculating | Dashboard scroll-linked animations unusable on target devices |
| **E-commerce** | Product image carousel slight stutter | Add-to-cart animation drops frames, feels broken | Checkout flow animations cause visible content jumping |
| **Mobile app (PWA)** | Non-critical animations dropping to 45fps | Primary gesture-driven animations (swipe, pull-to-refresh) below 45fps | Gesture animations below 30fps — feels like a broken native app |

**Severity multipliers:**
- **Animation frequency**: Animations that play on every interaction (hover, click, scroll) are experienced constantly. A jank on a rare transition matters less than jank on every scroll.
- **Brand perception**: For brand-heavy sites (luxury, creative, portfolio), animation quality IS brand quality. Jank says "cheap" whether the product is or not.
- **Native app comparison**: PWAs and web apps are compared against native apps. Native apps maintain 60fps. Web apps that don't lose the comparison immediately.

---

## §9 Build Bible integration

| Bible principle | Application to Animation Frame Budget |
|-----------------|----------------------------------------|
| **§1.4 Simplicity** | Simpler animations are smoother animations. A fade (opacity) is always smooth. A complex choreographed sequence with layout-triggering properties is always risky. If the animation can be simpler and still communicate the intent, simplify it. |
| **§1.8 Prevent, don't recover** | Use compositor-only properties (`transform`, `opacity`) from the start. Don't build animations with `left`/`top`/`width` and optimize later — the refactor is more work than doing it right initially. |
| **§1.13 Unhappy path first** | Test animations on the worst-case device in your target audience first. If it's smooth on a budget Android phone, it'll be smooth everywhere. Testing on your MacBook Pro first and "fixing mobile later" is the happy-path-first anti-pattern. |
| **§2 Reusable patterns** | Standardize animation patterns in the codebase: a set of proven, smooth transition classes that use compositor-only properties. Don't let each developer invent their own animation approach. |
| **§6.7 God file** | A single animation that involves 20 elements, 5 properties each, with staggered timing and scroll-driven triggers is a god animation. Break it into independent, compositor-friendly pieces. |
| **§1.12 Observe everything** | Monitor frame rates in production using the `PerformanceObserver` for `long-animation-frame` entries. Lab testing doesn't capture the real-world interaction between animations and concurrent main-thread work. |
