# This Python file uses the following encoding: utf-8
from enum import Enum


class EventType(Enum):
    activation = 'A'
    deadline = 'D'
    wfinish = 'W'
    start = 'S'
    finish = 'F'
    deadlineMiss = 'M'
    preemption = 'P'


class SchedEvent:
    def __init__(self, timestamp, task, type):
        self.timestamp = timestamp
        self.task = task
        self.job = 0
        self.processor = 0
        self.type = type
        self.extra = 0
