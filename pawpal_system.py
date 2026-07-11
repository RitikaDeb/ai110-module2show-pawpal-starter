"""Core domain models and scheduling logic for PawPal+."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}
VALID_PRIORITIES = set(PRIORITY_WEIGHT)
VALID_RECURRENCES = {"none", "daily", "weekly"}
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]


@dataclass
class Pet:
    name: str
    species: str
    breed: Optional[str] = None


@dataclass
class Owner:
    name: str
    available_minutes: int = 120
    start_time: str = "08:00"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str = "medium"
    recurrence: str = "none"
    day_of_week: Optional[str] = None  # only used when recurrence == "weekly"

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {self.duration_minutes}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(VALID_PRIORITIES)}, got {self.priority!r}")
        if self.recurrence not in VALID_RECURRENCES:
            raise ValueError(f"recurrence must be one of {sorted(VALID_RECURRENCES)}, got {self.recurrence!r}")
        if self.recurrence == "weekly" and self.day_of_week not in WEEKDAYS:
            raise ValueError(f"weekly tasks need a day_of_week in {WEEKDAYS}")

    def is_due(self, weekday: str) -> bool:
        """"none" (one-off) and "daily" tasks are due every day; "weekly" only on their day."""
        if self.recurrence == "weekly":
            return self.day_of_week == weekday
        return True


@dataclass
class ScheduledTask:
    task: Task
    start: str
    end: str
    reason: str


@dataclass
class SkippedTask:
    task: Task
    reason: str


@dataclass
class DailyPlan:
    pet: Pet
    scheduled: List[ScheduledTask] = field(default_factory=list)
    skipped: List[SkippedTask] = field(default_factory=list)

    @property
    def total_minutes_used(self) -> int:
        return sum(item.task.duration_minutes for item in self.scheduled)


class Scheduler:
    """Builds a single day's plan from a task list and time/priority constraints."""

    @staticmethod
    def build_plan(
        pet: Pet,
        tasks: List[Task],
        available_minutes: int,
        start_time: str = "08:00",
        weekday: Optional[str] = None,
    ) -> DailyPlan:
        due_tasks = [t for t in tasks if weekday is None or t.is_due(weekday)]

        # Highest priority first; among equal priority, shorter tasks first so more of them fit.
        ordered = sorted(
            due_tasks,
            key=lambda t: (-PRIORITY_WEIGHT[t.priority], t.duration_minutes, t.title),
        )

        plan = DailyPlan(pet=pet)
        clock = datetime.strptime(start_time, "%H:%M")
        remaining = available_minutes

        for task in ordered:
            if task.duration_minutes <= remaining:
                end = clock + timedelta(minutes=task.duration_minutes)
                plan.scheduled.append(
                    ScheduledTask(
                        task=task,
                        start=clock.strftime("%H:%M"),
                        end=end.strftime("%H:%M"),
                        reason=f"{task.priority} priority, fits in remaining {remaining} min",
                    )
                )
                clock = end
                remaining -= task.duration_minutes
            else:
                plan.skipped.append(
                    SkippedTask(
                        task=task,
                        reason=f"needs {task.duration_minutes} min but only {remaining} min left",
                    )
                )

        return plan
