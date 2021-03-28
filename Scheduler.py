# This Python file uses the following encoding: utf-8
from abc import *
import SchedIo
import SchedEvent
import numpy as np


class Scheduler:
    def __init__(self):
        pass

    name = 'GenericScheduler'
    deadlineNeeded = True

    @abstractmethod
    def onTick(self):
        pass

    def execute(self):
        pass

    @abstractmethod
    def isFeasible(self, tasks):
        return NotImplementedError


class RateMonotonic(Scheduler):
    name = 'Rate Monotonic'
    deadlineNeeded = False

    def __init__(self, tasks):
        self.minorCycle = tasks[0].period
        period = []
        #map=[]
        for task in tasks:
            if task.period < self.minorCycle:
                self.minorCycle = task.period
            period.append(task.period)
            #map.append(task.id)
        periodnp = np.array(period)
        periodindex = np.argsort(periodnp)
        self.sortedTasks = []
        self.remainingTime = []
        for ind in periodindex:
            currtask = tasks[ind]
            self.sortedTasks.append(currtask)
            self.remainingTime.append(currtask.wcet)
        self.executing = -1
        self.lastTime = 0
        self.absDeadline = [-1] * len(tasks)

    def isFeasible(tasks):
        n = len(tasks)
        lub = n * (pow(2, 1 / n) - 1)
        ui = 0
        for task in tasks:
            ui += task.wcet / task.period
        print("ui: " + str(ui))
        print("lub: " + str(lub))
        if ui > lub:
            return False
        return True

    def onTick(self, time, writer):
        delta = time - self.lastTime

        self.remainingTime[
            self.executing] -= delta  #decrease remaining execution time

        if self.remainingTime[
                self.executing] == 0:  #running task has finished execution
            print('time ' + str(time) + ' task ' +
                  str(self.sortedTasks[self.executing].id) +
                  ' has finished execution')
            writer.addSchedEvent(
                SchedEvent.SchedEvent(time,
                                      self.sortedTasks[self.executing].id,
                                      SchedEvent.EventType.finish.value))
            self.absDeadline[self.executing] = -1
            self.executing = -1  #mark no task running

        i = 0
        for task in self.sortedTasks:
            if time % task.period == 0:  #task activation
                print('time ' + str(time) + ' task ' + str(task.id) +
                      ' activates')
                writer.addSchedEvent(
                    SchedEvent.SchedEvent(
                        time, task.id, SchedEvent.EventType.activation.value))
                self.remainingTime[i] = task.wcet
                self.absDeadline[i] = time + task.deadline
            i += 1

        for i in range(0, len(self.absDeadline)):  #check if missed deadlines
            if time == self.absDeadline[i]:  #missed deadline
                print('time ' + str(time) + ' task ' +
                      str(self.sortedTasks[i].id) + ' missed deadline')
                writer.addSchedEvent(
                    SchedEvent.SchedEvent(
                        time, self.sortedTasks[i].id,
                        SchedEvent.EventType.deadlineMiss.value))

        if self.executing >= 0:
            if time % (self.minorCycle) == 0 and self.remainingTime[
                    self.executing] > 0:  #check if preemption needed
                for count in range(0, self.executing):
                    if self.remainingTime[count] > 0:  #preempt!
                        #signal preemption
                        print('time ' + str(time) + ' task ' +
                              str(self.sortedTasks[self.executing].id) +
                              ' has been preempted')
                        writer.addSchedEvent(
                            SchedEvent.SchedEvent(
                                time, self.sortedTasks[self.executing].id,
                                SchedEvent.EventType.preemption.value))
                        #allocate new task
                        self.executing = count
                        print('time ' + str(time) + ' task ' +
                              str(self.sortedTasks[count].id) + ' has started')
                        writer.addSchedEvent(
                            SchedEvent.SchedEvent(
                                time, self.sortedTasks[count].id,
                                SchedEvent.EventType.start.value))
        else:  #no task is running
            for count in range(
                    0, len(self.sortedTasks
                           )):  #allocate new task if at least one is activated
                if self.remainingTime[count] > 0:
                    self.executing = count
                    print('time ' + str(time) + ' task ' +
                          str(self.sortedTasks[count].id) + ' has started')
                    writer.addSchedEvent(
                        SchedEvent.SchedEvent(
                            time, self.sortedTasks[count].id,
                            SchedEvent.EventType.start.value))
                    break

        self.lastTime = time

    def execute(self, stop):
        writer = SchedIo.SchedEventWriter()
        for tick in range(0, stop):
            self.onTick(tick, writer)
        writer.terminateWrite()


schedulers = [RateMonotonic]
