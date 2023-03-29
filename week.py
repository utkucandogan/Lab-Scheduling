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
    
    def get_overlapping_slot_pairs(self) -> List[Tuple[int, int]]:
        list = []
        for day in range(self.days_in_week):
            for slot in range(self.slots_in_day - self.hours_in_slot + 1):
                slot_index = day * self.slots_in_day + slot
                for hour in range(1, self.hours_in_slot):
                    list.append((slot_index, slot_index + hour))
        return list
    
    # Converts the flat slot index to readable string
    def slot_index_to_string(self, index: int):
        day, slot = divmod(index, self.slots_in_day)
        return f"{Week.DAYS[day]}-{self.first_hour[0]+slot:02d}:{self.first_hour[1]:02d}"
