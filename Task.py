# This Python file uses the following encoding: utf-8


class Task:
    def __init__(self, id, wcet, period, deadline):
        self.id = id
        self.wcet = wcet
        self.period = period
        self.deadline = deadline
