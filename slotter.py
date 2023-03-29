from week import Week
from schedule import Schedules

import pulp
import numpy as np

import logging

class Slotter:
    def __init__(self, week: Week, name: str, lab_capacity: int,
                 assistant_count_per_session: int, max_assistant_work_deviation: int, assistant_work_deviation_constant: int,
                 student_available_slots: Schedules, assistant_available_slots: Schedules):
        self.week = week
        self.name = name
        self.lab_capacity = lab_capacity

        self.assistant_count_per_session = assistant_count_per_session
        self.max_assistant_work_deviation = max_assistant_work_deviation
        self.assistant_work_deviation_constant = assistant_work_deviation_constant

        self.student_available_slots = student_available_slots
        self.assistant_available_slots = assistant_available_slots

        self.student_list = self.student_available_slots.keys()
        self.assistant_list = self.assistant_available_slots.keys()

        # Get the number of sessions
        self.sessions = range(self.week.slots_in_week)

        # Create decision variables
        self.session_decision = pulp.LpVariable.dicts("Session", self.sessions, lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.student_session_decision = pulp.LpVariable.dicts("Student-Session", (self.sessions, self.student_list),
                                                              lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.assistant_session_decision = pulp.LpVariable.dicts("Assistant-Session", (self.sessions, self.assistant_list),
                                                                lowBound=0, upBound=1, cat=pulp.LpInteger)
        self.assistant_work_deviation = pulp.LpVariable("Assistant-Deviation", lowBound=0, upBound=self.max_assistant_work_deviation, cat=pulp.LpInteger)

        # Create the problem
        self.problem = pulp.LpProblem("Lab-Scheduling", pulp.LpMinimize)

        # Set the solver for the problem
        solver = pulp.PULP_CBC_CMD(msg = False) # Default solver with logging closed
        self.problem.setSolver(solver)

        # Create the objective of minimizing lab session count and assistant workload
        self.problem  += pulp.lpSum([self.session_decision[session] for session in self.sessions]) + self.assistant_work_deviation * self.assistant_work_deviation_constant

    def assign_constraints(self):
        # Create the constraint of a student only attending 1 lab session
        for student in self.student_list:
            self.problem += pulp.lpSum([self.student_session_decision[session][student] for session in self.sessions]) == 1

        # Constraint for attending students not exceeding lab capacity
        for session in self.sessions:
            self.problem += pulp.lpSum(
                    [self.student_session_decision[session][student] for student in self.student_list]
                ) <= self.lab_capacity * self.session_decision[session]
            
        # Make a constraint for the overlapping sessions so they are impossible
        for overlapping_pair in self.week.get_overlapping_slot_pairs():
            self.problem += (self.session_decision[overlapping_pair[0]] + self.session_decision[overlapping_pair[1]]) <= 1

        # Make student busy sessions impossible for them to attend
        for student in self.student_list:
            busy_indices = np.nonzero(~self.student_available_slots[student].strict.flatten())
            for session in busy_indices[0]:
                self.problem += self.student_session_decision[session][student] == 0

        # Make assistant busy sessions impossible for them to attend
        for assistant in self.assistant_list:
            busy_indices = np.nonzero(~self.assistant_available_slots[assistant].strict.flatten())
            for session in busy_indices[0]:
                self.problem += self.assistant_session_decision[session][assistant] == 0

        # Constraint for number of assistants per session
        for session in self.sessions:
            self.problem += pulp.lpSum(
                    [self.assistant_session_decision[session][assistant] for assistant in self.assistant_list]
                ) == self.assistant_count_per_session * self.session_decision[session]
            
        # Constraint for assistant workload balance
        for assitant_1 in self.assistant_list:
            for assitant_2 in self.assistant_list:
                    self.problem += pulp.lpSum(
                            [(self.assistant_session_decision[session][assitant_1] - self.assistant_session_decision[session][assitant_2])
                                for session in self.sessions
                            ]
                        ) <= self.assistant_work_deviation
    
    def find_slots(self):
        logging.info("Starting the solution")
        status = self.problem.solve()
        if status != 1:
            # Solution failed
            logging.error(f"Couldn't find the solution: {pulp.LpStatus[status]}")
            return None

        logging.info("Found the solution")
        sessions = {}
        for session in self.sessions:
            # Skip unselected sessions
            if not pulp.value(self.session_decision[session]):
                continue

            # Add the selected assistants and students into a list
            assistants = [assistant for assistant in self.assistant_list if pulp.value(self.assistant_session_decision[session][assistant])]
            students = [student for student in self.student_list if pulp.value(self.student_session_decision[session][student])]

            sessions[self.week.slot_index_to_string(session)] = (assistants, students)

        logging.debug(sessions)
        return sessions
