# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The UML settled on six classes: `Owner`, `Pet`, `Task`, `Scheduler`, and two small result
types, `ScheduledTask` and `SkippedTask`, wrapped by a `DailyPlan`. `Task` carries a
`title`, `duration_minutes`, `priority`, and a `recurrence` (`none` / `daily` / `weekly`,
with an optional `day_of_week`). `Scheduler.build_plan()` is the only method that does
real work — it takes a pet, a task list, a time budget, a start time, and today's
weekday, and returns a `DailyPlan`.

**b. Design changes**

The biggest change from the first sketch was splitting the plan's output into
`ScheduledTask` and `SkippedTask` instead of one list with a boolean flag. A flag would
have meant every display path had to branch on it; two explicit lists mean the UI (and
the tests) can just ask "what got scheduled" and "what got skipped and why" directly.
The `reason` string on both types was added for the same reason the scenario asks for
it — a plan nobody can explain isn't much better than no plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three things: the owner's available time (`available_minutes`),
each task's `priority`, and — for recurring tasks — whether the task is due `today`
(`Task.is_due(weekday)`). Priority is the primary sort key because a missed high-priority
task (medication, a walk) matters more than a missed low-priority one (a nail trim);
duration is only a tiebreaker.

**b. Tradeoffs**

The scheduler is a **greedy, priority-first fill**, not an optimizer: it never looks
ahead to ask "would skipping this high-priority task let three lower-priority ones fit
instead?" That's a deliberate simplification. An optimal knapsack-style solver would
maximize either total tasks completed or total priority-weighted value, but it would
also be harder to explain to a pet owner glancing at their phone — "high priority tasks
go first, ties go to whichever is shorter" is a rule a person can predict and trust.
For a small number of daily pet-care tasks (rarely more than 8–10), the two approaches
rarely diverge in a way that matters.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code to design the class model from the scenario, implement
`pawpal_system.py`, write the test suite, and wire `app.py` to the real scheduler. The
most useful prompts were the ones that asked for *behavior*, not code — e.g., "what
should happen when two tasks have the same priority?" and "what happens to a task that
doesn't fit?" — because the answers to those directly became the tie-break rule and the
`SkippedTask` type, respectively.

**b. Judgment and verification**

One thing worth double-checking before treating this as finished: the "shorter task
wins the tie" rule was an AI-proposed default, not a spec requirement — the scenario
only asks for priority and duration to be considered, not how ties should resolve. It's
verified in `test_ties_broken_by_shorter_duration_first` and reads reasonably (it fits
more tasks into the same slot), but it's a judgment call, and it's worth deciding
whether it actually matches how *you* want PawPal+ to behave — for example, an owner
might reasonably prefer ties broken by whichever task was added first instead.

---

## 4. Testing and Verification

**a. What you tested**

`tests/test_scheduler.py` covers: priority ordering, the duration tiebreaker, tasks
being skipped (with the correct reason) when time runs out, that scheduled tasks never
overlap, that weekly tasks only appear on their matching day, that daily/one-off tasks
appear every day, the `total_minutes_used` accounting, and validation errors for bad
`duration_minutes` / `priority` / `recurrence` values. These map directly onto the
"Smarter Scheduling" table in the README — each row there has at least one test behind
it.

**b. Confidence**

The core sort-then-fill logic is well covered — 12 tests pass, including the no-overlap
invariant, which is the property most likely to silently break under a future refactor.
What's *not* yet tested: multi-pet households (the model only plans for one pet at a
time), and what happens with a start time that crosses midnight. Both are edge cases
worth adding tests for before relying on this beyond a single pet, single day use case.

**c. Edge cases to test next**

- Two pets sharing one owner's time budget (currently each `DailyPlan` is single-pet).
- A `start_time` + total scheduled duration that rolls past `23:59`.
- A weekly task whose `day_of_week` is never passed as the current `weekday` (dead task,
  never surfaces — should probably warn the owner).

---

## 5. Reflection

**a. What went well**

The reason-string design (`ScheduledTask.reason` / `SkippedTask.reason`) paid off
immediately in the UI — being able to show *why* a task landed where it did (or didn't
make the cut) turned the schedule from a plain list into something that explains itself,
which was the actual point of the scenario.

**b. What you would improve**

The scheduler doesn't yet support multiple pets per owner or partially-fixed time slots
(e.g., "the vet appointment is at 2pm no matter what"). Both would require moving from
a single running clock to something closer to interval scheduling with fixed anchors.

**c. Key takeaway**

Deciding *what happens when things don't fit* turned out to matter as much as the
happy-path sorting logic — a scheduler that silently drops tasks is much less useful
than one that tells you what it dropped and why, even though "why" wasn't explicitly
in the original requirements.
