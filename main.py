import csv
import numpy as np

DAYS_IN_A_WEEK = 5
LECTURE_HOURS_IN_A_DAY = 9
IMPOSSIBLES_ID = "1111111"

csv_path = "student_schedule.csv"
lab_hour = 2

def hours_to_slots(schedule: np.ndarray):
    lab_filter = np.ones(lab_hour, dtype=int)
    slots = np.apply_along_axis(lambda day: np.convolve(day, lab_filter, "valid"), axis=1, arr=schedule)
    return slots == 2

students = {}
with open(csv_path, "r", encoding="utf-8") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=";")
    headers = next(csv_reader, None)
    if headers is None:
        raise RuntimeError(f"File named \"{csv_path}\" is empty!")

    # Process header to find id column index
    print(f"Column names are {', '.join(headers)}")
    id_column = headers.index("ID number")

    # Extract data as a numpy array
    for row in csv_reader:
        student_schedule_raw = np.array(row[id_column+1:]).reshape(DAYS_IN_A_WEEK, LECTURE_HOURS_IN_A_DAY)
        student_schedule_strict = student_schedule_raw == "1"
        student_schedule_relaxed = student_schedule_raw != "0"
        students[row[id_column]] = (student_schedule_strict, student_schedule_relaxed)

    print(f"Processing \"{csv_path}\" is done.")

# Prepare impossible slots
impossible_slots = students.pop(IMPOSSIBLES_ID)
impossible_slots = tuple(hours_to_slots(s) for s in impossible_slots)

# Calculate slots for students
for id, schedule in students.items():
    students[id] = tuple(hours_to_slots(s) & i for s, i in zip(students[id], impossible_slots))

print(students)
