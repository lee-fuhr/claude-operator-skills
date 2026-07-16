---
name: qq-cap-resume
description: Keep a live interactive chat session coming back to itself, visibly, after a usage/session cap interrupts it, never a silent background process. Invoke with /qq-cap-resume, or say “keep this session alive,” “resume yourself after the cap,” “don’t go dark on me,” any time a long interactive burn needs to survive a 5-hour session cap or ride out to a weekly reset without leaving you staring at a dead thread.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Keep a session visibly resuming itself through a cap

The gap this closes: a headless keepalive LaunchAgent (see `ww-keepalive` in this collection) is the right tool when nobody’s watching, it spawns a fresh `claude -p` elsewhere and reports back once it’s done. It is the wrong tool when you’re actively in this chat and want the conversation itself to pick back up here, in front of you, once the account can run again. Building a background lane when you asked for the chat to resume is the mistake this skill exists to prevent.

**The rule: if the ask is “keep going” inside a live conversation, the fix lives in this session, using `ScheduleWakeup`, not in a new LaunchAgent.**

## When to use

- A tool call in this session just failed with a cap/rate-limit signature (`usage limit`, `rate limit`, `5-hour`, `session limit`, `resets`, `try again later`, `too many requests`).
- You say some version of “keep this session alive,” “don’t die on me,” “come back and keep going,” or ask for exactly this ability ahead of a long burn.
- A long autonomous stretch is starting (you expect hours of work) and the session is likely to outlive a single 5-hour cap window.

## When NOT to use

- Nobody’s watching this chat and the work should survive you closing your laptop, that’s the headless LaunchAgent pattern (`ww-keepalive` in this collection), a different tool for a different job.
- The interruption isn’t a cap. A real error, a tool failure, a genuine blocker gets fixed or surfaced normally, not papered over with a reschedule.

## Protocol

### 1. Confirm it’s actually a cap, not a real failure

Match the error text against the cap signature list above. A generic error, a permission denial, or a tool bug is not this. Fix or surface it instead of rescheduling blindly.

### 2. Call `ScheduleWakeup` with a resume prompt, not a status check

```
ScheduleWakeup({
  delaySeconds: 3600,              // max allowed per call; chain multiple hops for longer waits
  reason: "session cap hit mid-<task>, resuming in 1h to retry",
  prompt: "<<autonomous-loop-dynamic>>"   // or a specific resume prompt naming the interrupted work
})
```

The `reason` field is what you see, make it specific (“watching for the 5h cap to clear on the build” beats “waiting”). The `prompt` is what fires when the wakeup lands: either a dynamic-loop sentinel if you’re running one, or a short, self-contained instruction naming exactly what was interrupted and what to try next.

### 3. On wakeup, retry, and reschedule again if still capped

When the scheduled prompt fires, attempt the interrupted work again. Two outcomes:

- **Tool calls succeed** → the cap cleared. Continue the real work, visibly, in this same thread. Report what resumed and why, in one line.
- **Tool calls fail with the same cap signature** → not clear yet. Call `ScheduleWakeup` again with the same pattern. A 5-hour session cap needs roughly five hops at the 3600s ceiling; a weekly cap needs however many hops reach the stated reset time. Never silently give up: either it resolves, or you see an explicit chain of “still waiting” turns.

### 4. Every hop is a visible turn

This is the entire point versus the LaunchAgent alternative. Each `ScheduleWakeup` firing is a new turn in the same conversation you’re reading, you can see the session is alive and waiting, not wonder if it died. Don’t suppress this into silence; a short “still capped, checking again at X” is the correct amount of narration, not spam and not nothing.

## Known failure mode (confirmed live, read this before trusting the pattern alone)

**A wakeup that fires while still capped kills the whole retry chain, silently.** Producing any response, even a one-line “still capped, rescheduling,” requires the same blocked capacity the cap is blocking. If a scheduled wakeup lands during a window where the account is still capped, that turn cannot generate output, which means it also cannot call `ScheduleWakeup` again to set the next retry. Nothing announces the failure. The chain just stops. This actually happened overnight: a fallback fired mid-cap, produced no visible turn, and no further wakeups ever fired. You’d find the session dead the next morning with zero explanation in between.

**The fix: don’t rely on self-chaining alone for anything that has to survive a real multi-hour cap.** Pair this skill with an external, dumb timer that doesn’t depend on this session successfully producing output. A LaunchAgent-style ping (see `ww-keepalive` in this collection) is the right tool for that specific job, even though it’s the pattern this skill otherwise explicitly avoids for the “keep it visible in-chat” case. The two aren’t actually in tension: use in-chat `ScheduleWakeup` for the visible narration when it lands after the cap has cleared (the common case, works fine), and a separate outside-clock fallback specifically to guarantee some retry eventually fires even if one self-chained hop dies mid-cap. Neither alone is fully robust. Together they are.

## Relationship to the headless keepalive pattern

Both solve “survive a cap,” but for different audiences:

| | `qq-cap-resume` (this skill) | Headless LaunchAgent keepalive |
|---|---|---|
| Where it resumes | This exact chat, visibly | A separate background process |
| Who sees each retry | You, in the thread, live | Nobody, unless it reports out |
| Right for | You’re actively watching, want the conversation to keep going | You’re stepping away, want unattended progress reported later |
| Mechanism | `ScheduleWakeup` inside the session | `claude -p` fired by `launchd` on a timer |

If you’re genuinely unsure which one to use, ask. The cost of building the wrong one is a background lane you never see, or a chat that goes dark when you expected it to keep talking to you.
