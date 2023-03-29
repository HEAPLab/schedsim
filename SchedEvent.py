# This module was based on SchedSim v1:
# https://github.com/HEAPLab/schedsim/blob/master/SchedEvent.py

from enum import Enum


class EventType(Enum):
    activation = 'A'
    deadline = 'D'
    worst_case_finish_time = 'W'
    start = 'S'
    finish = 'F'
    deadline_miss = 'M'


class ScheduleEvent:

    def __init__(self, timestamp, task, _type):
        self.timestamp = timestamp
        self.task = task
        self.job = 0
        self.processor = task.core
        self.type = _type
        self.extra = 0
        # HRRN facilities:
        self.response_ratio = 1
        self.init = self.timestamp
        # SRTF facilities:
        self.remaining_time = self.task.wcet
        self.executing_time = 0
        # EDF
        if _type == 'A':
            self.deadline_sort = timestamp + task.deadline
        else:
            self.deadline_sort = 0
        # Noises
        self.dynamic_wcet = task.wcet
        if _type == 'A':  # This if is to avoid noise generation when it isn't needed
            for noise in task.noises:
                self.dynamic_wcet = self.dynamic_wcet + noise.generate()

    def typeSet(self, _type):

        self.type = _type
