# __CAMPAIGN__: queue (priority order)

THE TASKLIST STANDARD. This is the durable, session-independent backlog. `open .../queue.md` works
in any session and survives caps, session death, and reboots. The worker picks the highest-priority
unfinished item each cycle and reconciles against done.md FIRST (never redo a finished unit).

Replace the lines below with the real backlog, priority-ordered. Each item should carry a clear
**Done test** so the worker (and a QC pass) can tell finished from unfinished without judgment.

## P1: <first priority>
<what + why>. **Done test:** <observable acceptance criterion>.

## P2: <second priority>
<what + why>. **Done test:** <observable acceptance criterion>.

## Parallel / only-if-blocked
<work that's safe to pick up if the priority items are blocked on a peer or the human>.

## Surfaced for the human
<anything the worker needs the human to decide; also mirror to the dashboard / build-status>.
