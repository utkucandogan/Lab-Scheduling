# Lab Scheduling
This is a program to choose fitting laboratory slots for multiple students and TAs.

The program takes student schedules (divided as academic, non-academic load, and free time), and TA schedules (busy, free time) as CSV files and some parameters defined in the `main.py` file.

## Requirements
- `numpy`
- `pulp`

## Workload Files

Workload files denote the workload and the free time of both students and TAs in two CSV files.

Each file contains a table with rows that designate each person and columns that designate the lecture hour availability for the person. The first three columns represent name, surname, and user ID. After that, each lecture hour will have its own column. The first row is reserved for titles.

For each lecture hour, there can be three integer values.
- Value `0` represents a free slot
- Value `1` represents a busy/academic slot
- Value `2` represents a part-time slot (this value is not available for TAs)
If a cell is left empty, it is considered as value `0`.

## Program Parameters

There are some parameters in the `main.py` file which is required for automatic assignments. These need to be modified for different courses.

- `student_path`: Designates the workload CSV file for the students
- `assistant_path`: Designates the workload CSV file for the TAs
- `days_in_week`: Number of days available in a week, starting from Monday and is contiguous (max `7`)
- `hours_in_day`: Number of hours available in a day, starting from the `first_hour`
    > Note: `days_in_week` and `hours_in_day` are used for calculating the number of columns in the CSV files.
- `first_hour`: Designates the first lecture hour as a tuple (e.g., `(8, 40)`)
- `hours_in_slot`: Number of hours a laboratory session takes
- `session_no`: Number of laboratory sessions in a week
- `lab_capacity`: Maximum number of students in a laboratory session
- `hours_between_sessions`: Minimum number of hours between consecutive laboratory sessions in a day
- `assistant_count_per_session`: Number of proctors in a laboratory session
- `max_assistant_work_deviation`: Injustice constants for TAs. This number represents the maximum load imbalance between TAs in terms of laboratory session count
- `assistant_work_deviation_constant`: Weight of the TA's work deviation with respect to student part-time conflicts. This is related to the minimization problem. If you are uncertain of what its value should be, keep it as `1`

## Usage Considerations
If your TAs won’t be assigned the same session each week, we recommend using a single, unified schedule entry for all of them—i.e., populate only one row in the TA CSV. By doing so, any time slots marked with a `1` will be universally blocked, ensuring no sessions can be scheduled during those hours. This approach lets you block out inconvenient time slots—such as a specific day of the week (e.g., Monday) or particular hours (e.g., the first period of the morning).
