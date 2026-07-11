from datetime import datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, WEEKDAYS

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A daily pet care planner that turns your task list into a schedule, in priority order.")

with st.expander("How it works", expanded=False):
    st.markdown(
        """
Add your pet's care tasks below with a duration and priority. PawPal+ sorts them
**high → medium → low priority** (shorter tasks first as a tiebreaker), then fits as
many as it can into the time you have today. Anything that doesn't fit is listed
separately with the reason it was skipped.
"""
    )

st.divider()

st.subheader("Owner & Pet")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")

col3, col4 = st.columns(2)
with col3:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col4:
    breed = st.text_input("Breed (optional)", value="")

st.subheader("Today's Constraints")
col5, col6 = st.columns(2)
with col5:
    available_minutes = st.number_input("Time available today (minutes)", min_value=10, max_value=600, value=90)
with col6:
    start_time = st.text_input("Start time (HH:MM)", value="08:00")

weekday = st.selectbox("Day of week", WEEKDAYS, index=datetime.now().weekday())

st.divider()

st.subheader("Tasks")
st.caption("Add each care task once. Weekly tasks only show up on their chosen day; daily and one-off tasks show up every day.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col_a, col_b, col_c = st.columns(3)
with col_a:
    task_title = st.text_input("Task title", value="Morning walk")
with col_b:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col_c:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)

col_d, col_e = st.columns(2)
with col_d:
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"], index=0)
with col_e:
    day_of_week = st.selectbox("If weekly, which day?", WEEKDAYS, index=0, disabled=(recurrence != "weekly"))

if st.button("Add task"):
    try:
        task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            recurrence=recurrence,
            day_of_week=day_of_week if recurrence == "weekly" else None,
        )
        st.session_state.tasks.append(task)
    except ValueError as e:
        st.error(str(e))

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "recurrence": t.recurrence,
                "day_of_week": t.day_of_week or "-",
            }
            for t in st.session_state.tasks
        ]
    )
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task first.")
    else:
        pet = Pet(name=pet_name, species=species, breed=breed or None)
        plan = Scheduler.build_plan(
            pet=pet,
            tasks=st.session_state.tasks,
            available_minutes=int(available_minutes),
            start_time=start_time,
            weekday=weekday,
        )

        st.markdown(f"### Daily plan for {pet.name} ({pet.species}{f', {pet.breed}' if pet.breed else ''})")

        if plan.scheduled:
            for item in plan.scheduled:
                st.markdown(
                    f"**{item.start}–{item.end}** — {item.task.title} "
                    f"({item.task.duration_minutes} min) · _{item.reason}_"
                )
        else:
            st.info("Nothing was scheduled — check that your tasks are due today and fit your time budget.")

        st.caption(f"Used {plan.total_minutes_used} of {int(available_minutes)} minutes.")

        if plan.skipped:
            st.markdown("**Skipped today:**")
            for item in plan.skipped:
                st.markdown(f"- {item.task.title}: _{item.reason}_")
