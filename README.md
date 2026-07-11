# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Daily plan for Biscuit (Golden Retriever):
  08:00 - 08:05 — Medication (5 min) [priority: high]
      reason: high priority, fits in remaining 75 min
  08:05 - 08:15 — Feeding (10 min) [priority: high]
      reason: high priority, fits in remaining 70 min
  08:15 - 08:45 — Morning walk (30 min) [priority: high]
      reason: high priority, fits in remaining 60 min
  08:45 - 09:10 — Fetch in the yard (25 min) [priority: medium]
      reason: medium priority, fits in remaining 30 min
  Used 70/75 min
  Skipped:
    - Brushing: needs 15 min but only 5 min left
```

This came from a 75-minute time budget with six tasks queued (three high-priority,
one medium, two low). Note that `Medication` and `Feeding` jump ahead of the longer
`Morning walk` even though all three are "high" priority — same-priority tasks are
ordered shortest-first so more of them fit in the available time.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest -v
```

Sample test output:

```
collected 12 items

tests/test_scheduler.py::test_higher_priority_scheduled_before_lower PASSED
tests/test_scheduler.py::test_ties_broken_by_shorter_duration_first PASSED
tests/test_scheduler.py::test_tasks_skipped_when_time_runs_out PASSED
tests/test_scheduler.py::test_scheduled_tasks_never_overlap PASSED
tests/test_scheduler.py::test_weekly_task_only_scheduled_on_its_day PASSED
tests/test_scheduler.py::test_daily_and_one_off_tasks_always_due PASSED
tests/test_scheduler.py::test_total_minutes_used PASSED
tests/test_scheduler.py::test_invalid_task_fields_raise[kwargs0] PASSED
tests/test_scheduler.py::test_invalid_task_fields_raise[kwargs1] PASSED
tests/test_scheduler.py::test_invalid_task_fields_raise[kwargs2] PASSED
tests/test_scheduler.py::test_invalid_task_fields_raise[kwargs3] PASSED
tests/test_scheduler.py::test_weekly_task_requires_day_of_week PASSED

============================== 12 passed in 0.01s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.build_plan` | Sorts by priority (`high` → `medium` → `low`) first, then by duration ascending so short tasks aren't starved out by one long one at the same priority. |
| Filtering | `Scheduler.build_plan` | Walks the sorted list against a running `remaining` minute counter; anything that doesn't fit is dropped into `plan.skipped` with a reason instead of silently disappearing. |
| Conflict handling | `Scheduler.build_plan` | Tasks are scheduled back-to-back off one clock (`clock += timedelta(...)`), so overlapping time slots aren't possible by construction — there's no separate conflict-detection step needed. |
| Recurring tasks | `Task.is_due`, `Scheduler.build_plan(weekday=...)` | `recurrence="daily"` and `"none"` tasks are due every day; `recurrence="weekly"` tasks only pass `is_due` on their stored `day_of_week`. The scheduler filters on this before sorting. |

## 📸 Demo Walkthrough

1. Fill in the owner's name and the pet's name, species, and (optional) breed.
2. Set today's time budget in minutes and a start time (e.g. `90` minutes starting at `08:00`).
3. Add each care task with a duration and priority; optionally mark it `daily` or `weekly` (pick a day) instead of a one-off.
4. Repeat step 3 for every task — they collect in a table below so you can review them before generating a plan.
5. Click **Generate schedule**. PawPal+ sorts the due tasks by priority, fills your time budget back-to-back from the start time, and shows each scheduled task's time slot with the reason it was placed there.
6. Anything that didn't fit shows up under **Skipped today** along with why (e.g. "needs 15 min but only 5 min left"), so nothing just quietly vanishes.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
