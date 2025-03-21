import logging

from week import Week
from schedule import ScheduleFactory
from slotter import Slotter

# Logging configuration
logging.basicConfig(filename="debug.log", encoding="utf-8", level=logging.DEBUG)

# Constants
student_path = "test-data/student_schedule.csv"
assistant_path = "test-data/assistant_schedule.csv"
days_in_week = 5
hours_in_day = 9
first_hour = (8, 40)
hours_in_slot = 2
session_no = 5
lab_capacity = 15
hours_between_sessions = 1
assistant_count_per_session = 1
max_assistant_work_deviation = 3
assistant_work_deviation_constant = 1

# Helper classes and factories
week = Week(days_in_week, hours_in_day, hours_in_slot, first_hour)
scheduler = ScheduleFactory(week)

# Create the schedules
student_hours = scheduler.read_schedules(student_path)
assistant_hours = scheduler.read_schedules(assistant_path)

student_slots = scheduler.generate_slots(student_hours)
assistant_slots = scheduler.generate_slots(assistant_hours)

logging.debug(student_slots)

slotter = Slotter(week, "Lab-Schedule", lab_capacity, assistant_count_per_session,
                  max_assistant_work_deviation, assistant_work_deviation_constant, student_slots,
                  assistant_slots, session_no, hours_between_sessions)

slotter.assign_constraints()
result, conflicts = slotter.find_slots()
if result is not None:
    for session, (assistants, student_list) in result.items():
        print(f"🟢 {session} 🎓 {assistants}: 🤓 {student_list}")
    print()
    print(f"⚠️ Conflicts ({len(conflicts)}): {conflicts}")
else:
    print("❌ Couldn't find the solution! ❌")
