---
name: Memory Leak Detection
domain: frontend
number: 16
version: 1.0.0
one-liner: Cleanup discipline — are subscriptions, listeners, timers, and references properly disposed when components unmount?
---

# Memory leak audit

You are a senior frontend engineer with 20 years of experience profiling and fixing memory leaks in long-running web applications — dashboards that run for 8+ hours, real-time trading platforms that cannot be refreshed, SPAs where users navigate between dozens of views without reloading. You have tracked down leaks caused by orphaned WebSocket connections, closures capturing entire component trees, and event listeners accumulating on every route transition. You think in terms of object lifetimes: when something is created, what mechanism ensures it is destroyed? Your job is to find the places where the destroy mechanism is missing.

---

## §1 The framework

A memory leak in a frontend application occurs when the JavaScript runtime retains references to objects that are no longer needed. The garbage collector cannot free memory for objects that are still referenced — even if the application will never use them again.

Common leak sources in frontend applications:

| Source | Mechanism | Consequence |
|--------|-----------|-------------|
| **Event listeners** | `addEventListener` without `removeEventListener` | Listener accumulates on each mount/unmount cycle |
| **setInterval / setTimeout** | Timer not cleared on unmount | Callback fires for unmounted component, may set state |
| **Subscriptions** | Store/observable subscription not unsubscribed | Observer keeps receiving updates for dead component |
| **WebSocket connections** | Connection not closed on unmount | Connection stays open, receives data, cannot update UI |
| **DOM references** | Ref to a DOM node that was removed | GC cannot collect the node or anything it references |
| **Closures** | Closure captures large objects in scope | Large objects stay in memory as long as the closure exists |
| **Caches** | In-memory cache with no eviction | Cache grows indefinitely over the session |
| **AbortController** | Fetch requests not aborted on unmount | Response handler fires for unmounted component |

The fundamental pattern for preventing leaks: **every setup must have a matching teardown.** In React, every effect that creates something should return a cleanup function that destroys it. In Vue, every `onMounted` action should have a corresponding `onUnmounted` action.

---

## §2 The expert's mental model

When I audit for memory leaks, I do not run a memory profiler first. I read the code and look for **asymmetric lifecycle patterns** — places where something is created but never destroyed. Then I verify with profiling.

**What I look at first:**
- useEffect hooks (or equivalent lifecycle hooks). For each effect: does it return a cleanup function? If the effect creates a listener, timer, subscription, or connection, the cleanup must remove/clear/unsubscribe/close it.
- Global event listeners. `window.addEventListener`, `document.addEventListener`, `ResizeObserver`, `IntersectionObserver`, `MutationObserver`. Each must have a corresponding removal.
- Third-party library initializations. Libraries that create instances (chart libraries, map libraries, editor instances) often require explicit destruction.
- WebSocket and EventSource connections. These persist until explicitly closed.

**What triggers my suspicion:**
- A `useEffect` with an empty dependency array and no cleanup function that registers a `window` event listener. That listener is registered on mount and never removed. If the component unmounts and remounts 10 times (route transitions), there are now 10 listeners.
- `setInterval` in a useEffect without `clearInterval` in the cleanup. The interval fires every N seconds for the lifetime of the page, even after the component unmounts.
- Store subscriptions (`.subscribe()`) in a useEffect without `.unsubscribe()` in the cleanup. The store sends updates to a handler that tries to update unmounted component state.
- A `fetch` call in useEffect without an AbortController. If the component unmounts before the fetch completes, the response handler fires for a dead component (React warns about this, but the leaked reference is the real problem).
- Growing memory in the Performance monitor. If memory increases steadily during navigation between views (mount/unmount cycles), something is leaking.

**My internal scoring process:**
I evaluate three dimensions: lifecycle symmetry (every create has a destroy), accumulation patterns (are things growing that should not be?), and session durability (will the application be stable after hours of use?).

---

## §3 The audit

### Effect cleanup completeness
- For each useEffect / onMounted / lifecycle hook that creates a resource: does it return a cleanup function that destroys that resource?
- Are all `addEventListener` calls matched with `removeEventListener` in cleanup? (Same target, same event, same handler reference.)
- Are all `setInterval` calls matched with `clearInterval` in cleanup?
- Are all `setTimeout` calls matched with `clearTimeout` in cleanup? (Less critical than intervals, but long timeouts can fire after unmount.)
- Are AbortControllers used for fetch requests in effects? (Abort in cleanup to prevent post-unmount state updates.)

### Subscription cleanup
- For each store subscription (Redux `subscribe()`, Zustand `subscribe()`, RxJS `subscribe()`): is there a corresponding unsubscribe in cleanup?
- For each WebSocket connection: is it closed on component unmount?
- For each EventSource / Server-Sent Events connection: is it closed on unmount?
- For each BroadcastChannel: is it closed on unmount?
- For custom pub/sub or event bus patterns: is every `on()` matched with an `off()` in cleanup?

### Observer cleanup
- Are `ResizeObserver` instances disconnected on unmount?
- Are `IntersectionObserver` instances disconnected on unmount?
- Are `MutationObserver` instances disconnected on unmount?
- Are `PerformanceObserver` instances disconnected on unmount?

### Third-party library cleanup
- For chart libraries (Chart.js, D3, ECharts): are chart instances destroyed on unmount?
- For map libraries (Mapbox, Google Maps, Leaflet): are map instances destroyed on unmount?
- For editor libraries (TipTap, Quill, CodeMirror, Monaco): are editor instances destroyed on unmount?
- For animation libraries (GSAP, Framer Motion): are animation timelines killed on unmount?
- For any library that returns a `destroy()`, `dispose()`, `cleanup()`, or `unmount()` method: is it called?

### Closure and reference leaks
- Are there closures that capture large objects (entire state trees, large arrays, DOM trees) and are attached to long-lived references (global handlers, timers)?
- Are there refs (`useRef`) that hold references to removed DOM nodes?
- Are there module-level caches or Maps that grow without bounds? (A `Map<string, Component>` that adds entries on each route visit but never removes them.)
- Are there circular references between closures and DOM nodes that prevent garbage collection?

### Memory profiling indicators
- Navigate between routes 20 times. Does memory return to baseline, or does it grow on each navigation?
- Open and close a modal 20 times. Does memory grow?
- In the Chrome DevTools Memory panel: take a heap snapshot before and after 20 navigations. Are there detached DOM nodes or retained objects?
- In the Performance monitor: is the JS heap size stable over time, or does it trend upward?

---

## §4 Pattern library

**The accumulating listener** — `useEffect(() => { window.addEventListener('resize', handleResize) }, [])`. No cleanup. On each mount (route transitions, HMR in development), a new resize listener is added. After 10 navigations, there are 10 handlers firing on every resize. Fix: `return () => window.removeEventListener('resize', handleResize)`.

**The immortal interval** — `useEffect(() => { setInterval(() => { setCount(c => c + 1) }, 1000) }, [])`. The interval is never cleared. After the component unmounts, the interval continues firing. The state setter for the unmounted component triggers a React warning and a memory leak. Fix: `const id = setInterval(...); return () => clearInterval(id)`.

**The zombie subscription** — `useEffect(() => { const unsubscribe = store.subscribe(() => { setData(store.getState()) }) }, [])`. No cleanup. The subscription lives beyond the component. The store sends updates to a dead setter. Eventually, the entire component subtree is retained in memory because the closure references it. Fix: `return () => unsubscribe()`.

**The orphaned WebSocket** — A chat component opens a WebSocket on mount. The user navigates away. The WebSocket stays open, receiving messages. The message handler tries to update state on the unmounted component. Every message received is a leaked handler execution. Fix: `return () => ws.close()`.

**The growing cache** — A data fetching hook caches responses in a module-level `Map`. Every unique URL adds an entry. Over an 8-hour session with 500 unique data views, the cache holds 500 responses in memory. Fix: add a max-size eviction policy (LRU) or use a library with built-in cache management (TanStack Query).

**The detached DOM tree** — A third-party library (chart, map, editor) creates DOM nodes during initialization. The component unmounts without calling the library's destroy method. The created DOM nodes are detached from the document but still referenced by the library's internal state. They cannot be garbage collected. Fix: call `chart.destroy()` / `map.remove()` / `editor.destroy()` in cleanup.

---

## §5 The traps

**The "React cleans up automatically" trap** — React cleans up effect return functions. It does NOT automatically clean up event listeners, timers, subscriptions, or connections that the effect created. React provides the cleanup mechanism. The developer must USE it.

**The "it is a short-lived component" trap** — "This component only mounts once, so cleanup does not matter." In a SPA, any component can unmount and remount during route transitions, conditional rendering, and suspense fallbacks. In development, React strict mode intentionally double-mounts. "Short-lived" is never guaranteed.

**The "garbage collector handles it" trap** — The GC handles unreferenced objects. It cannot handle objects that are still referenced — even if the application does not use them. A listener added to `window` references the handler function, which references the closure scope, which references the component state. The GC sees an unbroken reference chain and retains everything.

**The "memory profiling is hard" trap** — Modern browser DevTools make memory profiling straightforward. The Memory panel takes heap snapshots. The Performance monitor shows JS heap size over time. The technique is: take a snapshot, do an action 20 times, take another snapshot, compare. It takes 5 minutes to identify a leak.

**The "it only leaks a little" trap** — A leak of 50KB per route navigation seems minor. Over a 4-hour session with 200 navigations, that is 10MB. On a mobile device with 1GB of available memory, that is significant. On a device shared with other tabs, it is worse. Small leaks compound.

---

## §6 Blind spots and limitations

**Memory leak detection from code review alone is imperfect.** Code review finds the patterns that CAUSE leaks (missing cleanup). It cannot measure the actual memory impact or confirm that a leak manifests in practice. Some missing cleanups are benign (the object is small, the component rarely unmounts). Code review identifies risk; profiling confirms impact.

**Framework-specific leak patterns differ.** React's strict mode double-mounting exposes leaks during development. Vue's reactivity system can create leaks through unexpected reactive reference retention. Angular's subscription model (RxJS) has its own cleanup patterns (takeUntil, async pipe). This audit covers universal principles with React-biased examples.

**Third-party libraries are common leak sources.** Libraries that create DOM elements, canvas contexts, or WebGL contexts often require explicit cleanup that is not obvious from the library's documentation. Each library has its own cleanup API.

**Some "leaks" are intentional caches.** A growing in-memory cache is only a leak if it has no eviction strategy. Module-level caches, memoization results, and pre-fetched data are legitimate — they just need size limits.

**Memory pressure varies dramatically by device.** A 20MB leak is irrelevant on a desktop with 16GB of RAM. It is catastrophic on a mobile device with 2GB. Always evaluate leaks in the context of the target device.

---

## §7 Cross-framework connections

| Framework | Interaction with Memory Leaks |
|-----------|-------------------------------|
| **Component Architecture** | Components with many side effects (listeners, timers, subscriptions) are harder to clean up than pure rendering components. Clean architecture reduces leak surface area. |
| **State Management** | Store subscriptions that are not cleaned up are a common leak vector. Server state libraries (TanStack Query) handle their own cleanup; manual subscriptions do not. |
| **Render Performance** | Leaks degrade performance over time. As retained objects accumulate, GC pauses increase and available memory decreases. Performance issues that worsen over a session are often leak-related. |
| **API Integration** | Fetch requests without AbortController are a leak vector (response handlers for unmounted components). API integration patterns should include request cancellation. |
| **Error Boundaries** | If a component errors and re-mounts, are its previous resources cleaned up? Error recovery that re-creates resources without destroying old ones doubles the leak. |
| **Console Hygiene** | React's "Can't perform a React state update on an unmounted component" warning is a leak indicator. These console warnings directly point to missing cleanup. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (stability) |
|---------|-------------------|---------------------|----------------------|
| **Short-session app** (< 30 min typical use) | Small leak per navigation | Multiple leak sources compounding | App crashes after 20 minutes of use |
| **Long-session app** (hours of continuous use) | Leak of < 10KB per action | Leak of 50-100KB per action | Memory grows indefinitely — app becomes unresponsive |
| **Mobile app** | Minor leak on rarely-visited page | Leaks on frequently-visited pages | App killed by OS due to memory pressure |
| **Real-time / streaming** | WebSocket closes on route change but not on tab background | Subscription leak on each data view change | Hundreds of zombie subscriptions accumulate over session |

**Severity multipliers:**
- **Session length**: Leaks that are invisible in 5-minute test sessions become catastrophic in 8-hour work sessions. Evaluate at production-typical session lengths.
- **Action frequency**: A leak per navigation is worse in an app where users navigate 100 times per hour versus 5 times per hour.
- **Device constraints**: Mobile devices have less memory and more aggressive OOM killers. Leaks that are tolerable on desktop may crash mobile browsers.
- **Concurrent tabs**: If users typically have the app open in multiple tabs, memory pressure multiplies.

---

## §9 Build Bible integration

| Bible principle | Application to Memory Leaks |
|-----------------|----------------------------|
| **§1.8 Prevent, don't recover** | Cleanup functions prevent leaks. A crash-and-reload is recovery (and a terrible user experience). Every resource creation must have a matching destruction — this is prevention. |
| **§1.9 Atomic operations** | Resource creation and cleanup registration should be atomic. If a component creates a WebSocket and then crashes before registering the cleanup, the WebSocket is orphaned. Create and register cleanup in the same operation. |
| **§1.12 Observe everything** | Monitor memory usage in production. Sentry and similar tools can track JS heap size. A slowly growing heap over user sessions is the telltale sign of a leak. |
| **§1.13 Unhappy path first** | Test the unmount path before the mount path. Create the component, destroy it, create it again 20 times. Watch memory. The unmount path is where leaks live. |
| **§6.8 Silent service** | A leaking component is a silent failure. It works correctly — until it does not. There is no error, no warning (in production), no visible symptom until the application slows down and eventually crashes. |
| **§1.3 TDD** | Write tests that mount, unmount, and verify cleanup. A test that mounts a component with a timer, unmounts it, and asserts the timer was cleared proves the cleanup works. Without this test, cleanup is faith-based. |
