from typing import List, Tuple

concecutive_block = True
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
    
    def get_overlapping_slot_pairs(self) -> List[Tuple[int, int]]:
        list = []
        if (concecutive_block):
            hours_in_slot = self.hours_in_slot + 1 # Disable consecutive lab sessions
        else:
            hours_in_slot = self.hours_in_slot 
        for day in range(self.days_in_week):
            for slot in range(self.slots_in_day - hours_in_slot + 1): # Each slot calculates index
                slot_index = day * self.slots_in_day + slot
                for hour in range(1, hours_in_slot): # Look forward to slots for overlaps
                    list.append((slot_index, slot_index + hour))
        return list
    
    # Converts the flat slot index to readable string
    def slot_index_to_string(self, index: int):
        day, slot = divmod(index, self.slots_in_day)
        return f"{Week.DAYS[day]}-{self.first_hour[0]+slot:02d}:{self.first_hour[1]:02d}"
