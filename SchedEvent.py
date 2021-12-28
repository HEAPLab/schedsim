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
