# __CAMPAIGN__ — done log (verified units only)

THE TASKLIST STANDARD (companion to queue.md). Append-only. The worker reads this on every resume
and SKIPS anything recorded here. Only log a unit after it is actually produced AND verified on disk
(read the file / run the test / check the real value) — never on an agent's self-report.

`open .../done.md` works in any session and survives caps. This is the relay's memory of what is
already finished; without it, a stateless worker would redo completed work every cycle.

## --- worker entries below this line ---
