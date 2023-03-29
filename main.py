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
hours_in_slot = 2
session_no = 5
lab_capacity = 16
assistant_count_per_session = 2
max_assistant_work_deviation = 3
assistant_work_deviation_constant = 1

# Helper classes and factories
week = Week(days_in_week, hours_in_day, hours_in_slot)
scheduler = ScheduleFactory(week)

# Create the schedules
student_hours = scheduler.read_schedules(student_path)
assistant_hours = scheduler.read_schedules(assistant_path)

student_slots = scheduler.generate_slots(student_hours)
assistant_slots = scheduler.generate_slots(assistant_hours)

logging.debug(student_slots)

slotter = Slotter(week, "Lab-Schedule", lab_capacity, assistant_count_per_session,
                  max_assistant_work_deviation, assistant_work_deviation_constant, student_slots, assistant_slots,session_no)

slotter.assign_constraints()
result = slotter.find_slots()
for session, list in result.items():
    print(session, list)
