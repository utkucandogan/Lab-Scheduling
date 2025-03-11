from typing import List, Tuple

class Week:
    """
        This class holds the information about the work week
    """

    DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

    def __init__(self, days_in_week: int, hours_in_day: int, hours_in_slot: int, first_hour: Tuple[int, int] = (8, 40)):
        self.days_in_week = days_in_week
        self.hours_in_day = hours_in_day
        self.hours_in_slot = hours_in_slot
        self.first_hour = first_hour

        self.slots_in_day = hours_in_day - hours_in_slot + 1
        self.slots_in_week = days_in_week * self.slots_in_day
    
    def get_overlapping_slot_pairs(self, hours_between_slots: int) -> List[Tuple[int, int]]:
        list = []

        # used for blocking overlapping slots.
        # First parameter is the real overlap, second one is for creating breaks between slots
        overlapping_hour_amount = self.hours_in_slot + hours_between_slots

        for day in range(self.days_in_week):
            # Calculate the slot index for each day, last few are removed for preventing overflow
            for slot in range(self.slots_in_day - self.hours_in_slot + 1): # Each slot calculates index
                slot_index = day * self.slots_in_day + slot
                for hour in range(1, overlapping_hour_amount): # Look forward to slots for overlaps
                    if slot + hour >= self.slots_in_day:
                        break
                    list.append((slot_index, slot_index + hour))
        return list
    
    # Converts the flat slot index to readable string
    def slot_index_to_string(self, index: int):
        day, slot = divmod(index, self.slots_in_day)
        return f"{Week.DAYS[day]}-{self.first_hour[0]+slot:02d}:{self.first_hour[1]:02d}"
