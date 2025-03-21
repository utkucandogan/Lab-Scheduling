from typing import Dict

import csv
import logging
import numpy as np

from week import Week

# This is a mock student ID for signifying impossible lab times
# such as lecture hours (we cannot put lab sessions during lecture hours
# even if a student says they are available)
IMPOSSIBLES_ID = "IMPOSSIBLE"
class Availability:
    FREE = "0"
    BUSY = "1"
    EXTRA = "2"

# Calculates a convolution with an array (slot_filter) of length slot_length and consists of ones,
# to find the slots that are available
def _to_slots_convolution_helper(schedule: np.ndarray, slot_length: int):
    slot_filter = np.ones(slot_length, dtype=int)
    slots = np.apply_along_axis(lambda day: np.convolve(day, slot_filter, "valid"), axis=1, arr=schedule)
    return slots == slot_length

class Schedule:
    """
        This is the class that can hold schedules for student and assistants
        It can hold both hour info and slot info as availability
            strict: Holds the availibilty by considering extra hours as busy
            relaxed: Holds the availibilty by considering extra hours as free
    """
    def __init__(self, academic: np.ndarray, part_time: np.ndarray, altruism_parameter: int):
        self.academic = academic
        self.part_time = part_time
        self.altruism_parameter = altruism_parameter

    def __repr__(self):
        return f"<Schedule academic:\n{self.academic}\n>"
    
    def __str__(self):
        return f"(strict: {self.academic} relaxed: {self.part_time} altruism_parameter: {self.altruism_parameter})"

    # Convolves the hours with the lab length signal and returns a new Schedule
    def to_slots(self, week: Week, impossibles: "Schedule"):
        academic = _to_slots_convolution_helper(self.academic & impossibles.academic, week.hours_in_slot)
        part_time = _to_slots_convolution_helper(self.part_time & impossibles.part_time, week.hours_in_slot)
        altruism_parameter = np.count_nonzero(~part_time) # Make unavaliable slots of the part time to 1 count non zero
        altruism_parameter = (week.days_in_week * week.slots_in_day) - altruism_parameter #Makes it small for students with lot of part time

        return Schedule(academic, part_time, altruism_parameter)

# Type hint definition
Schedules = Dict[str, Schedule]

class ScheduleFactory:
    """
        This is the factory class that reads the schedules and converts them into slot information
    """
    def __init__(self, week: Week):
        self.week = week

    # Returns an empty (or completely free) schedule
    def freeSchedule(self) -> Schedule:
        free_schedule = np.ones((self.week.days_in_week, self.week.hours_in_day), dtype=bool)
        return Schedule(free_schedule, free_schedule, 0)

    # Read schedules from csv file
    def read_schedules(self, filepath: str) -> Schedules:
        schedules = {}
        with open(filepath, "r", encoding="utf-8") as csv_file:
            content = csv_file.read()

            # FIX: Auto detect the csv type and act accordingly
            delimeter_fixed = content.replace(";" , ",").replace("\t",",")  # Change all delimiters to be comma

            csv_reader = csv.reader(delimeter_fixed.splitlines(), delimiter=",")
            headers = next(csv_reader, None)
            if headers is None:
                raise RuntimeError(f"File named \"{filepath}\" is empty!")

            # Process header to find id column index
            logging.debug(f"Column names are {', '.join(headers)}")
            id_column = headers.index("ID number")

            # Extract data as a numpy array
            for row in csv_reader:
                row_processed = [h if h else Availability.FREE for h in row[id_column+1:]] # Replaces empty cells with FREE
                hours_raw = np.array(row_processed).reshape(self.week.days_in_week, self.week.hours_in_day)

                hours_part_time = hours_raw != Availability.EXTRA # Checks which slots are free and creates bool array
                hours_academic = hours_raw != Availability.BUSY # Checks which slots aren't busy and creates bool array (handles extra time as free)
                altruism_parameter = 0

                schedules[row[id_column]] = Schedule(hours_academic, hours_part_time, altruism_parameter)

            logging.info(f"Processing \"{filepath}\" is done.")

        return schedules

    # Converts slots from hour info to slot info
    def generate_slots(self, schedules: Schedules) -> Schedules:
        # Get the impossible slots, get an empty schedule if not found
        impossibles = schedules.pop(IMPOSSIBLES_ID, self.freeSchedule())
        return {id: s.to_slots(self.week, impossibles) for id, s in schedules.items()}
