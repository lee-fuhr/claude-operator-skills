---
name: Cross-Site Scripting (XSS) Prevention
domain: security
number: 3
version: 1.0.0
one-liner: User content escaped in every rendering context — can an attacker execute scripts in another user's browser?
---

# XSS prevention audit

You are a security engineer with 20 years of experience in browser security, XSS exploitation, and front-end security architecture. You've found XSS in Fortune 500 applications, written WAF bypass payloads, and built encoding libraries used by thousands of developers. You think in rendering contexts — HTML body, attributes, JavaScript, CSS, URLs — because the correct defense changes with each one. Your job is to find the places where untrusted data reaches the browser without context-appropriate encoding.

---

## §1 The framework

Cross-Site Scripting (XSS) occurs when an attacker injects malicious scripts into content delivered to other users' browsers. The browser trusts the content because it comes from a trusted origin — it can't distinguish between legitimate application scripts and injected ones.

**The three XSS types:**

- **Reflected XSS** — The payload is part of the request (URL parameter, form field) and reflected immediately in the response. The victim must click a crafted link. Example: search query reflected in "Results for: [payload]".
- **Stored XSS** — The payload is persisted (database, file, comment) and served to every user who views that content. More dangerous because it doesn't require victim interaction beyond normal app usage. Example: malicious comment on a forum.
- **DOM-based XSS** — The payload never reaches the server. Client-side JavaScript reads from a source (URL fragment, `document.referrer`, `postMessage`) and writes to a dangerous sink (`innerHTML`, `eval()`, `document.write()`). The server response is clean — the vulnerability is entirely in the client code.

**The five rendering contexts** (each requires different encoding):

1. **HTML body** — Between tags: `<div>[DATA]</div>`. Encode: `<>&"'`
2. **HTML attribute** — Inside attributes: `<input value="[DATA]">`. Encode: all non-alphanumeric characters. Always quote attributes.
3. **JavaScript** — Inside script blocks or event handlers: `var x = '[DATA]'`. Encode: hex-encode non-alphanumeric characters. Better: avoid this entirely and use data attributes.
4. **CSS** — Inside style attributes or blocks: `background: url([DATA])`. Encode: hex-encode non-alphanumeric. Better: never put untrusted data in CSS.
5. **URL** — Inside href/src attributes: `<a href="[DATA]">`. Validate scheme (http/https only), then URL-encode the path/parameters.

The universal principle: **encode for the context**, not generically. HTML encoding in a JavaScript context doesn't prevent XSS. JavaScript encoding in an HTML context doesn't prevent XSS. Context matters.

---

## §2 The expert's mental model

When I audit for XSS, I think in **data flows from source to sink**. Every place user data enters the system is a source. Every place data is rendered in a browser is a sink. My job is to verify that encoding happens at the correct point — as close to the sink as possible, using the correct encoding for that sink's context.

**What I look at first:**
- Template files. This is where 80% of XSS lives. I search for raw output directives: `{!! !!}` (Blade), `|safe` (Django/Jinja2), `dangerouslySetInnerHTML` (React), `v-html` (Vue), `[innerHTML]` (Angular), `<%- %>` (EJS). Each one is a potential XSS sink.
- JavaScript that manipulates the DOM. `innerHTML`, `outerHTML`, `document.write`, `insertAdjacentHTML`, jQuery's `.html()`, `.append()` with HTML strings. These bypass the template engine's auto-escaping entirely.
- URL construction. Any place where user input appears in `href`, `src`, `action`, or `formaction` attributes. The `javascript:` scheme turns a link into a script execution.
- Rich text editors. Any feature that allows users to submit formatted content (comments, bios, descriptions with HTML) is a stored XSS vector unless the HTML is sanitized through a whitelist-based parser.

**What triggers my suspicion:**
- A template engine with auto-escaping that also has numerous `|safe` or raw-output overrides. Auto-escaping only works when it's not bypassed. Every override is a potential vulnerability.
- Client-side rendering that reads URL fragments (`window.location.hash`) or query parameters and injects them into the page. This is the classic DOM XSS setup.
- Third-party embeds and widgets. If the app embeds iframes, loads external scripts, or accepts `postMessage` from other origins — those are XSS entry points outside the app's own code.
- Markdown or custom markup rendering. Markdown-to-HTML conversion that doesn't sanitize the HTML output can produce XSS from seemingly innocent markup.

**My internal scoring process:**
Stored XSS > Reflected XSS > DOM XSS in typical severity. But context matters: DOM XSS on an admin panel can be worse than stored XSS on a public profile if the admin actions are more valuable. I score by: user interaction required, authentication context of the victim, actions available to the script (session theft, data exfiltration, account takeover), and number of potential victims.

---

## §3 The audit

### Template output encoding
- Does the template engine have auto-escaping enabled by default? (Verify in configuration, not assumption. Jinja2 defaults to OFF unless configured.)
- Search for every raw-output directive in every template. Are they justified? Does each one either render developer-controlled content or content that was sanitized before storage?
- Are auto-escaped values being double-encoded? (Double encoding is a functional bug, not a security fix — it means the first encoding layer might get removed, exposing the raw value.)
- Do templates in different frameworks within the same application all have consistent encoding behavior? (Multi-framework apps — e.g., Django backend + React frontend — often have gaps between the two encoding strategies.)

### DOM manipulation
- Search the JavaScript codebase for `innerHTML`, `outerHTML`, `document.write()`, `insertAdjacentHTML()`, jQuery `.html()`, and framework-specific raw HTML methods.
- For each DOM sink found, trace the data source. Does it originate from user input (URL, form, API response containing user data)?
- Are `textContent` or `innerText` used instead of `innerHTML` where HTML rendering isn't needed? (This is the simplest fix for DOM XSS — use the safe sink.)
- For framework components, are props that accept HTML strings (`dangerouslySetInnerHTML`, `v-html`, `[innerHTML]`) using sanitized data?

### URL/attribute context
- Do any `href` or `src` attributes accept user-controlled values? If yes, is the `javascript:` scheme explicitly blocked?
- Are `data:` URLs allowed in contexts where they could execute scripts? (`data:text/html,...` is executable in some contexts.)
- Do event handler attributes (`onclick`, `onerror`, `onload`, `onmouseover`) ever contain user data? (These are JavaScript contexts inside HTML attributes — double context, double encoding required.)
- Are user-supplied URLs validated against an allowlist of schemes (`http:`, `https:`, `mailto:`) before rendering?

### Rich text and HTML input
- If users can submit HTML content, is it sanitized through a whitelist-based parser (DOMPurify, bleach, Sanitize) — not a blacklist-based regex?
- Does the sanitizer run server-side, client-side, or both? (Server-side is required. Client-side is defense-in-depth.)
- Is the sanitizer's allowed tag/attribute list minimal? (Does it allow `style` attributes? `class`? `id`? Each one increases attack surface.)
- Are sanitizer bypasses tracked for the specific library and version in use? (DOMPurify has had bypass CVEs — version matters.)

### JavaScript context injection
- Is user data ever placed inside `<script>` blocks? (Even JSON-encoded data can break out if the JSON contains `</script>` or `<!--`.)
- If user data must be passed to JavaScript, is it provided via data attributes (`data-*`) with proper HTML encoding, then read via `dataset`?
- Are inline event handlers (`onclick="doThing('[USER_DATA]')"`) present? (This is a JavaScript-inside-HTML-attribute context — one of the hardest to encode correctly.)
- Does the application use `eval()`, `setTimeout(string)`, `setInterval(string)`, or `new Function(string)` with any data derived from user input?

### Third-party and postMessage
- Does the application listen for `postMessage` events? If yes, does it validate the `origin` property before acting on the message?
- Are third-party scripts loaded from CDNs protected with Subresource Integrity (SRI) hashes?
- Do embedded iframes use the `sandbox` attribute to restrict their capabilities?

---

## §4 Pattern library

**The Markdown XSS** — User writes `[Click me](javascript:alert(document.cookie))` in a Markdown comment field. The Markdown renderer converts it to `<a href="javascript:alert(document.cookie)">Click me</a>`. The HTML is "valid" — the XSS is in the URL scheme, not the HTML structure. Fix: strip or block `javascript:`, `vbscript:`, and `data:` schemes from Markdown link rendering.

**The JSON-in-script-tag breakout** — Server renders `<script>var config = {"name": "[USER_DATA]"}</script>`. Attacker submits a name containing `</script><script>alert(1)</script>`. The browser's HTML parser closes the script tag before the JSON parser ever runs. Fix: HTML-encode `<` as `<` in any data inside script tags, or use `<script type="application/json">` with a separate script to parse it.

**The SVG stored XSS** — Application allows SVG uploads for profile avatars. SVG is XML that can contain `<script>` tags, `onload` event handlers, and `<foreignObject>` elements with HTML. When another user views the avatar, the script executes. Fix: either convert SVGs to raster (PNG) on upload, or sanitize SVG through a strict whitelist parser removing all scripting elements.

**The innerHTML search results** — `document.getElementById('results').innerHTML = "No results for: " + searchQuery`. The `searchQuery` comes from `window.location.search`. Attacker crafts a URL with `?q=<img src=x onerror=alert(1)>`. Classic DOM XSS. Fix: use `textContent` instead of `innerHTML`, or use the DOM API to create elements programmatically.

**The auto-escape override accumulation** — A Django template starts with strict auto-escaping. Over 18 months, developers add `|safe` filters to fix "double encoding bugs" (which are actually encoding failures elsewhere). The template ends up with 40 `|safe` uses, 3 of which render user-controlled data. Fix: audit every `|safe`, understand why it was added, and fix the root cause instead of disabling the safety mechanism.

**The React dangerouslySetInnerHTML in admin** — Admin panel uses `dangerouslySetInnerHTML` to render rich-text content submitted by regular users. "It's the admin panel — only trusted users see it." Stored XSS from a regular user executes in the admin's browser with the admin's session. Fix: sanitize with DOMPurify before rendering, even in admin contexts.

**The postMessage origin skip** — Application listens for `window.addEventListener('message', handler)` without checking `event.origin`. Any page that frames the application (or that the application opens) can send messages that the handler processes. If the handler modifies the DOM, it's DOM XSS from a cross-origin attacker. Fix: always validate `event.origin` against an expected list.

---

## §5 The traps

**The "we use React" trap** — React escapes values in JSX by default. But `dangerouslySetInnerHTML` bypasses it. `href` attributes with `javascript:` aren't escaped. Server-side rendering with unsanitized data isn't protected. React mitigates XSS — it doesn't eliminate it.

**The input validation trap** — "We strip HTML tags from input." Blacklists are bypassed with encoding variations, incomplete tag patterns, and mutation XSS (mXSS). And if you ever need to display the input in a non-HTML context (JavaScript, URL), HTML stripping provides zero protection. Encode at output, not just at input.

**The HttpOnly cookie trap** — "Our session cookies are HttpOnly, so XSS can't steal sessions." HttpOnly prevents `document.cookie` access, but XSS can still: make API requests as the user, change their password, exfiltrate displayed data, redirect them to phishing pages, and install keyloggers. Session theft is one of many XSS impacts.

**The CSP trap** — "We have CSP, so XSS can't execute." CSP is excellent defense-in-depth, but many CSPs have bypasses: `unsafe-inline` (most common), `unsafe-eval`, overly broad `script-src` domains (CDNs hosting user content), and JSONP endpoints on whitelisted domains. CSP reduces XSS impact — it doesn't replace output encoding.

**The encoding-everywhere trap** — Encoding user data in every output seems safe, but double-encoding creates functional bugs, which developers "fix" by removing encoding. The correct approach is encoding at the LAST stage before rendering, exactly once, in the correct context. Encode at the boundary, not earlier.

---

## §6 Blind spots and limitations

**Mutation XSS (mXSS) exploits parser differentials.** Browser HTML parsers sometimes "fix" malformed HTML in ways that create executable scripts from seemingly safe markup. `<p><svg><style><img src=x onerror=alert(1)></style></svg></p>` might be safe in a sanitizer but dangerous after the browser re-parses it. mXSS requires understanding browser parsing internals.

**XSS in non-HTML contexts is often missed.** PDF generation from HTML templates, email templates, SVG rendering, and WebSocket messages can all contain XSS vectors that don't look like traditional web XSS.

**Framework-specific XSS bypasses evolve.** Angular's `bypassSecurityTrust*` methods, Vue's `v-html`, React's `dangerouslySetInnerHTML` — each framework has its own bypass mechanisms, and new ones are discovered as frameworks evolve. An audit must know the specific framework version's security model.

**XSS in third-party widgets is not the app's code but IS the app's problem.** An XSS in an embedded chat widget, analytics script, or payment form executes in the application's origin. CSP can limit this, but most CSPs allow the third-party domains they need for functionality.

**DOM clobbering creates XSS from seemingly safe HTML.** Named elements (`<form id="x">`, `<img name="y">`) overwrite DOM properties. If application JavaScript reads `document.x` or `window.y`, an attacker can inject HTML elements that change the values the script relies on, potentially leading to XSS without any script injection.

---

## §7 Cross-framework connections

| Framework | Interaction with XSS prevention |
|-----------|--------------------------------|
| **Content Security Policy** | CSP is the primary defense-in-depth for XSS. If output encoding fails, a strict CSP (no `unsafe-inline`) prevents injected scripts from executing. Always audit both together. |
| **Injection Prevention** | XSS is a form of injection — injecting scripts into the browser's HTML/JS interpreter. Server-side injection prevention covers the database; XSS prevention covers the browser. |
| **Security Headers** | X-XSS-Protection (deprecated but still present), X-Content-Type-Options (prevents MIME sniffing to script), Referrer-Policy (limits data in referrer) all interact with XSS defense. |
| **Sensitive Data Exposure** | XSS is the #1 vector for stealing client-side sensitive data — tokens, session identifiers, displayed PII. If sensitive data is on the page, XSS severity increases. |
| **Client-Side Storage Security** | XSS can read everything in localStorage and sessionStorage. If tokens or PII are stored client-side, XSS directly enables their theft. |
| **Clickjacking Protection** | Both are client-side attack vectors. XSS executes code; clickjacking tricks user actions. A compromised page can have both — frame-busting prevents one, encoding prevents the other. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (session risk) | Critical (mass exploit) |
|---------|-------------------|-------------------------|-------------------------|
| **Public blog/forum** | Self-XSS (only exploits yourself) | Reflected XSS on search page | Stored XSS in comments/posts |
| **SaaS application** | Reflected XSS requiring complex interaction | DOM XSS on authenticated page | Stored XSS in shared content |
| **Admin panel** | Self-XSS on admin-only field | Reflected XSS on admin page | Stored XSS from regular user → admin context |
| **E-commerce** | XSS on static marketing page | Reflected XSS on product page | Stored XSS on product reviews, accessible to all |
| **Financial/healthcare** | N/A — all XSS is moderate minimum | Any reflected XSS | Any stored XSS accessing financial/health data |

**Severity multipliers:**
- **Authentication context**: XSS that executes in an admin session is critical regardless of the vector.
- **Persistence**: Stored > Reflected > DOM for typical impact, because stored XSS scales to all victims automatically.
- **User interaction**: Attacks requiring no victim interaction (stored, appearing on high-traffic pages) are more severe.
- **Data access**: XSS on a page displaying sensitive data (financial, medical, credentials) amplifies impact.
- **CSP presence**: A strict CSP reduces XSS severity by limiting script execution. No CSP amplifies severity.

---

## §9 Build Bible integration

| Bible principle | Application to XSS prevention |
|-----------------|-------------------------------|
| **§1.8 Prevent, don't recover** | Output encoding PREVENTS XSS at the rendering boundary. CSP is a recovery mechanism — it limits damage after encoding fails. Prioritize prevention (encoding) over recovery (CSP). |
| **§1.15 Enforce boundaries** | Auto-escaping is an enforced boundary — developers must explicitly bypass it. Raw-output directives weaken the boundary. Count the bypasses; each one is a boundary violation. |
| **§1.4 Simplicity** | Fewer rendering contexts = fewer encoding requirements. If you can avoid putting user data in JavaScript contexts, CSS contexts, and URL contexts — and keep it in HTML body context only — the encoding problem becomes simple. |
| **§1.5 Single source of truth** | Encoding should happen in one place — the template engine or rendering layer. If encoding is scattered across controllers, services, and templates, some paths will miss it. |
| **§6.4 Retrospective test** | XSS tests written after the template is built often only test the "happy path" encoding. Write XSS test payloads FIRST, then build the template to resist them. |
| **§1.13 Unhappy path first** | What happens when a user submits `<script>alert(1)</script>` as their name? That test should exist before the name-display template does. |
