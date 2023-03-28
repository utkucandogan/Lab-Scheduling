from schedule import Schedule, WeeklyConstants
import pulp
import logging
import numpy as np

# Constants
student_path = "test-data/student_schedule.csv"
assistant_path = "test-data/assistant_schedule.csv"
lab_hour = 2
max_deviation = 3
deviation_constant = 1
lab_capacity = 16
assistant_count_per_session = 2

# Create the schedules
student_hours = Schedule.read_schedules(student_path)
assistant_hours = Schedule.read_schedules(assistant_path)

student_slots = Schedule.generate_slots(student_hours, lab_hour)
assistant_slots = Schedule.generate_slots(assistant_hours, lab_hour)

logging.debug(student_slots)

# Get the number of sessions
sessions = range(WeeklyConstants.get_slot_count(lab_hour))

session_decision = pulp.LpVariable.dicts("Session", sessions, lowBound=0, upBound=1, cat=pulp.LpInteger)
student_session_decision = pulp.LpVariable.dicts("Student Session", (sessions, student_slots.keys()), lowBound=0, upBound=1, cat=pulp.LpInteger)
assistant_session_decision = pulp.LpVariable.dicts("Assistant Session", (sessions, assistant_slots.keys()), lowBound=0, upBound=1, cat=pulp.LpInteger)
assistant_deviation = pulp.LpVariable("Assistant Deviation", lowBound=0, upBound=max_deviation, cat=pulp.LpInteger)

# Create the problem
prob = pulp.LpProblem("Lab Scheduling", pulp.LpMinimize)
# Create the objective of minimizing lab session count
prob += pulp.lpSum([session_decision[session] for session in sessions]) + assistant_deviation * deviation_constant
# Create the constraint of a student only attending 1 lab session
for student in student_slots.keys():
    prob += pulp.lpSum([student_session_decision[session][student] for session in sessions]) == 1

# Constraint for attending students not exceeding lab capacity
for session in sessions:
    prob += pulp.lpSum([student_session_decision[session][student] for student in student_slots.keys()]) <= lab_capacity * session_decision[session]
# Make a constraint for the overlapping sessions so they are impossible
for overlapping_pair in WeeklyConstants.get_overlapping_pairs(lab_hour):
    prob += (session_decision[overlapping_pair[0]] + session_decision[overlapping_pair[1]]) <= 1
# Make student busy sessions impossible for them to attend
for student in student_slots.keys():
    busy_indices = np.nonzero(~student_slots[student].relaxed.flatten())
    for session in busy_indices[0]:
        prob += student_session_decision[session][student] == 0
# Make assistant busy sessions impossible for them to attend
for assistant in assistant_slots.keys():
    busy_indices = np.nonzero(~assistant_slots[assistant].relaxed.flatten())
    for session in busy_indices[0]:
        prob += assistant_session_decision[session][assistant] == 0
# Constraint for number of assistants per session
for session in sessions:
    prob += pulp.lpSum([assistant_session_decision[session][assistant] for assistant in assistant_slots.keys()]) == assistant_count_per_session * session_decision[session]

for assitant_1 in assistant_slots.keys():
    for assitant_2 in assistant_slots.keys():
             prob += pulp.lpSum(
                  [(assistant_session_decision[session][assitant_1] - assistant_session_decision[session][assitant_2]) for session in sessions]
                  ) <= assistant_deviation

print("Starting the solution")
status = prob.solve()
print(pulp.LpStatus[status])
for i, s in session_decision.items():
    if pulp.value(s):
        print(i)
