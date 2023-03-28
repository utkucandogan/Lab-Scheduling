from typing import Dict, List, Tuple
from enum import Enum

import csv
import logging
import numpy as np

IMPOSSIBLES_ID = "IMPOSSIBLE"

class WeeklyConstants:
    DAYS_IN_A_WEEK = 5
    LECTURE_HOURS_IN_A_DAY = 9

    def get_slot_count(slot_length: int) -> int:
        return WeeklyConstants.DAYS_IN_A_WEEK * (WeeklyConstants.LECTURE_HOURS_IN_A_DAY - slot_length + 1)
    
    def get_overlapping_pairs(slot_length: int) -> List[Tuple[int, int]]:
        slots_in_a_day = WeeklyConstants.LECTURE_HOURS_IN_A_DAY - slot_length + 1
        list = []
        for day in range(WeeklyConstants.DAYS_IN_A_WEEK):
            for slot in range(slots_in_a_day - slot_length + 1):
                slot_index = day * slots_in_a_day + slot
                for hour in range(1, slot_length):
                    list.append((slot_index, slot_index + hour))
        return list

def _hours_to_slots(schedule: np.ndarray, slot_length: int):
    slot_filter = np.ones(slot_length, dtype=int)
    slots = np.apply_along_axis(lambda day: np.convolve(day, slot_filter, "valid"), axis=1, arr=schedule)
    return slots == slot_length

class Availability(Enum):
    FREE = "0"
    BUSY = "1"
    EXTRA = "2"

class Schedule:
    def __init__(self, strict: np.ndarray, relaxed: np.ndarray, extra_time: int):
        self.strict = strict
        self.relaxed = relaxed
        self.extra_time = extra_time

    def __repr__(self):
        return f"<Schedule strict:\n{self.strict}\n>"
    
    def __str__(self):
        return f"(strict: {self.strict} relaxed: {self.relaxed} extra_time: {self.extra_time})"
    
    def free() -> "Schedule":
        free_schedule = np.ones((WeeklyConstants.DAYS_IN_A_WEEK, WeeklyConstants.LECTURE_HOURS_IN_A_DAY), dtype=bool)
        return Schedule(free_schedule, free_schedule, 0)

    def read_schedules(filepath: str) -> Dict[str, "Schedule"]:
        schedules = {}
        with open(filepath, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            headers = next(csv_reader, None)
            if headers is None:
                raise RuntimeError(f"File named \"{filepath}\" is empty!")

            # Process header to find id column index
            logging.debug(f"Column names are {', '.join(headers)}")
            id_column = headers.index("ID number")

            # Extract data as a numpy array
            for row in csv_reader:
                row_processed = [h if h else Availability.FREE for h in row[id_column+1:]] # Replaces empty cells with FREE
                hours_raw = np.array(row_processed).reshape(WeeklyConstants.DAYS_IN_A_WEEK, WeeklyConstants.LECTURE_HOURS_IN_A_DAY)

                hours_strict = hours_raw == Availability.FREE
                hours_relaxed = hours_raw != Availability.BUSY
                extra_time = np.count_nonzero(hours_raw == Availability.EXTRA)

                schedules[row[id_column]] = Schedule(hours_strict, hours_relaxed, extra_time)

            logging.info(f"Processing \"{filepath}\" is done.")

        return schedules

    def to_slots(self, slot_length: int, impossibles: "Schedule"):
        strict = _hours_to_slots(self.strict & impossibles.strict, slot_length)
        relaxed = _hours_to_slots(self.relaxed & impossibles.relaxed, slot_length)

        return Schedule(strict, relaxed, self.extra_time)
    
    def generate_slots(schedules: Dict[str, "Schedule"], slot_length: int) -> Dict[str, "Schedule"]:
        impossibles = schedules.pop(IMPOSSIBLES_ID, Schedule.free())
        return {id: s.to_slots(slot_length, impossibles) for id, s in schedules.items()}
    