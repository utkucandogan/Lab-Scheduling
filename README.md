# Lab Scheduling

This is a program to choose fitting laboratory slots for multiple students and TAs.

Program takes student schedules (divided as academic, non-academic load and free time), TA schedules (busy, free time) as csv files and some parameters defined in `main.py` file.

# Requirements
- `numpy`
- `pulp`

## Workload Files

Workload files denote the workload and the free-time of both students and TAs in two csv files.

Each file contains a table with rows designate each person and columns designate the lecture hour availability for the person. Firts three columns represent name, surname and user ID respectively. After that each lecture hour will have their own column. First row is reserved for titles.

For each lecture hour, there can be three integer values.
- Value `0` represents a free slot
- Value `1` represents a busy/academic slot
- Value `2` represents a part-time slot (this value is not available for TAs)
If a cell is left empty, it is considered as value `0`.

## Program Parameters

There are some parameters in `main.py` file which is required for automatic assignments. These needs to be modified for different courses.

- `student_path`: Designates the workload csv file for the students
- `assistant_path`: Designates the workload csv file for the TAs
- `days_in_week`: Number of days available in a week, starts from Monday and is contigiuous (max `7`)
- `hours_in_day`: Number of hours available in a day, starts from the `first_hour`
    > Note: `days_in_week` and `hours_in_day` are used for calculating the number of columns in the csv files.
- `first_hour`: Designates the first lecture hour as tuple (e.g. `(8, 40)`)
- `hours_in_slot`: Number of hours a laboratory session takes
- `session_no`: Number of laboratory sessions in a week
- `lab_capacity`: Maximum number of students in a laboratory session
- `hours_between_sessions`: Minimum number of hours between consecutive laboratory sessions in a day
- `assistant_count_per_session`: Number of proctors in a laboratory session
- `max_assistant_work_deviation`: Injustice constants for TAs. This number represents maximum load imbalance between TAs in terms of laboratory session count
- `assistant_work_deviation_constant`: Weight of the TAs work deviation with respect to student part-time conflicts. This is related to the minimization problem. If you are uncertain of what its value should be, keep it as `1`
