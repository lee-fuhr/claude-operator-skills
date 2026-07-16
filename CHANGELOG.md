# Changelog

All notable changes to this repo’s skills are documented here. Releases are listed newest first.

## [1.1.0] - 2026-07-16

### Added

- **Add `qq-cap-resume`, a skill for resuming a live chat itself, visibly, after a usage cap, instead of falling back to a silent background worker.**
    - Complements the existing headless `ww-keepalive` LaunchAgent pattern for the opposite case: someone actively watching who wants the same thread to keep talking, not a background process reporting back later.
    - Documents a real failure mode found live: a scheduled wakeup that fires while still capped can’t produce output at all, so it silently fails to schedule its own next retry. The fix pairs the in-chat retry with a separate, dumb, outside-the-session timer.

### Changed

- **Fix the AFK skill family’s shared framing across the README and two `SKILL.md` files: three points on one spectrum, not an unexplained pair plus a third wheel.**
    - `qq-go-afk-ham`, `qq-go-afk-smart`, and `qq-go-afk-lean` were described as “the AFK pair” (ham and smart), leaving lean looking like an unrelated afterthought, even though all three answer the same question: how much to protect the token budget.
    - Each skill’s description and README section now states its place on that one spectrum (unbounded, adaptive middle, frugal) and links to both siblings, not just one.

## [1.0.0] - 2026-07-15

_First tracked release. Twenty-three skills already shipped before this changelog started; this entry marks the baseline rather than reconstructing prior history._
