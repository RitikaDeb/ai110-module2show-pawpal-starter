import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def biscuit():
    return Pet(name="Biscuit", species="dog", breed="Golden Retriever")


def test_higher_priority_scheduled_before_lower(biscuit):
    tasks = [
        Task("Nail trim", duration_minutes=10, priority="low"),
        Task("Morning walk", duration_minutes=30, priority="high"),
        Task("Feeding", duration_minutes=10, priority="medium"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60)

    titles = [item.task.title for item in plan.scheduled]
    assert titles == ["Morning walk", "Feeding", "Nail trim"]


def test_ties_broken_by_shorter_duration_first(biscuit):
    tasks = [
        Task("Long play session", duration_minutes=45, priority="medium"),
        Task("Quick feeding", duration_minutes=10, priority="medium"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60)

    titles = [item.task.title for item in plan.scheduled]
    assert titles == ["Quick feeding", "Long play session"]


def test_tasks_skipped_when_time_runs_out(biscuit):
    tasks = [
        Task("Morning walk", duration_minutes=40, priority="high"),
        Task("Enrichment play", duration_minutes=40, priority="high"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60)

    assert len(plan.scheduled) == 1
    assert len(plan.skipped) == 1
    assert "40 min" in plan.skipped[0].reason
    assert "20 min left" in plan.skipped[0].reason


def test_scheduled_tasks_never_overlap(biscuit):
    tasks = [
        Task("Morning walk", duration_minutes=30, priority="high"),
        Task("Feeding", duration_minutes=10, priority="high"),
        Task("Meds", duration_minutes=5, priority="high"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60, start_time="08:00")

    for earlier, later in zip(plan.scheduled, plan.scheduled[1:]):
        assert earlier.end == later.start


def test_weekly_task_only_scheduled_on_its_day(biscuit):
    tasks = [
        Task("Grooming", duration_minutes=30, priority="medium", recurrence="weekly", day_of_week="Saturday"),
    ]

    on_day = Scheduler.build_plan(biscuit, tasks, available_minutes=60, weekday="Saturday")
    off_day = Scheduler.build_plan(biscuit, tasks, available_minutes=60, weekday="Monday")

    assert len(on_day.scheduled) == 1
    assert len(off_day.scheduled) == 0


def test_daily_and_one_off_tasks_always_due(biscuit):
    tasks = [
        Task("Feeding", duration_minutes=10, priority="high", recurrence="daily"),
        Task("Vet visit", duration_minutes=20, priority="high", recurrence="none"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60, weekday="Tuesday")

    assert len(plan.scheduled) == 2


def test_total_minutes_used(biscuit):
    tasks = [
        Task("Morning walk", duration_minutes=30, priority="high"),
        Task("Feeding", duration_minutes=10, priority="high"),
    ]
    plan = Scheduler.build_plan(biscuit, tasks, available_minutes=60)

    assert plan.total_minutes_used == 40


@pytest.mark.parametrize(
    "kwargs",
    [
        {"duration_minutes": 0},
        {"duration_minutes": -5},
        {"priority": "urgent"},
        {"recurrence": "monthly"},
    ],
)
def test_invalid_task_fields_raise(kwargs):
    base = {"title": "Walk", "duration_minutes": 10, "priority": "medium"}
    base.update(kwargs)
    with pytest.raises(ValueError):
        Task(**base)


def test_weekly_task_requires_day_of_week():
    with pytest.raises(ValueError):
        Task("Grooming", duration_minutes=30, priority="medium", recurrence="weekly")
