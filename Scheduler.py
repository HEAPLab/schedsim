from abc import *
import SchedEvent
import SchedIO

class Scheduler:

    def __init__(self, output_file):
        self.name = 'GenericScheduler'
        self.tasks = []
        self.start = None
        self.end = None

        self.executing = None

        self.arrival_events = []
        self.finish_events = []
        self.deadline_events = []
        self.start_events = []

        self.output_file = SchedIO.SchedulerEventWriter(output_file)

        self.cores = []

    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def find_finish_events(self, time):
        pass

    def create_partitions(self):
        # create as many static partition as the core that we have
        # I can manage 3 different cases:

        # For 2 cores we make 2 partition: periodic and sporadic
        if len(self.cores) == 2:
            for task in self.tasks:
                if task.type == 'periodic':
                    task.core = self.cores[0].id
                else:
                    task.core = self.cores[1].id

        # For 3 cores: deadline partition
        elif len(self.cores) == 3:

            tasks = sorted(self.tasks.copy(), key=lambda x: x.deadline)
            list_length = len(tasks)
            part_size = list_length // 3
            tasks_list = [tasks[:part_size], tasks[part_size:2 * part_size], tasks[2 * part_size:]]

            for i in range(len(tasks_list)):
                for j in tasks_list[i]:
                    tasks_list[i][j].core = self.cores[i].id

        # For 4 cores: divide events in type/deadline like an hybrid of the 2 previous way
        else:
            tasks = sorted(self.tasks.copy(), key=lambda x: x.deadline)
            avg_deadline = 0
            for t in self.tasks:
                avg_deadline += t.deadline
            avg_deadline /= len(self.tasks)

            tasks_list = [tasks[:len(self.tasks)/2], tasks[len(self.tasks)/2:]]

            for i in tasks_list[0]:
                if tasks_list[0][i].type == 'periodic':
                    tasks_list[0][i].core = self.cores[0].id
                else:
                    tasks_list[0][i].core = self.cores[1].id

            for i in tasks_list[1]:
                if tasks_list[1][i].type == 'periodic':
                    tasks_list[1][i].core = self.cores[2].id
                else:
                    tasks_list[1][i].core = self.cores[3].id

    def get_all_arrivals(self):
        arrival_events = []
        for task in self.tasks:
            # Here you can add the code to choose between different cores:
            if len(self.cores) == 1:
                task.core = self.cores[0].id
            else:
                if self.name == 'PEDF':
                    self.create_partitions()
                elif self.name == 'GEDF':
                    a = 1

            # ------------------------------- #
            if task.type == 'periodic':
                i = self.start
                j = 1
                while i < self.end:
                    event = SchedEvent.ScheduleEvent(i, task, SchedEvent.EventType.activation.value)
                    event.job = j
                    arrival_events.append(event)
                    i += task.period
                    j += 1
            elif task.type == 'sporadic':
                task.init = task.activation
                event = SchedEvent.ScheduleEvent(task.activation, task, SchedEvent.EventType.activation.value)
                arrival_events.append(event)
        arrival_events.sort(key=lambda x: x.timestamp)
        return arrival_events

    def find_arrival_event(self, time):
        helper_list = []
        for event in self.arrival_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
                start_event = SchedEvent.ScheduleEvent(
                    event.timestamp, event.task, SchedEvent.EventType.start.value)
                start_event.job = event.job
                self.start_events.append(start_event)
            elif event.timestamp > time:
                helper_list.append(event)
        self.arrival_events = helper_list

    def find_deadline_events(self, time):
        helper_list = []
        for event in self.deadline_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
            elif event.timestamp > time:
                helper_list.append(event)
        self.deadline_events = helper_list


class NonPreemptive(Scheduler):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'GenericNonPreemptiveScheduler'

    def execute(self):
        pass

    def find_finish_events(self, time):
        helper_list = []
        for event in self.finish_events:
            if event.timestamp == time:
                self.output_file.add_scheduler_event(event)
                self.cores[int(event.processor)].executing = None
            elif event.timestamp > time:
                helper_list.append(event)
        self.finish_events = helper_list

    def find_start_events(self, time):
        helper_list = []
        for event in self.start_events:
            if event.timestamp == time and self.cores[int(event.processor)].executing is None:
                self.output_file.add_scheduler_event(event)
                self.cores[int(event.processor)].executing = event
                # Create finish event:
                finish_timestamp = event.timestamp + event.task.wcet
                finish_event = SchedEvent.ScheduleEvent(
                    finish_timestamp, event.task, SchedEvent.EventType.finish.value)
                finish_event.job = event.job
                self.finish_events.append(finish_event)
                # Create deadline event:
                if event.task.real_time:
                    deadline_timestamp = event.timestamp + event.task.deadline
                    deadline_event = SchedEvent.ScheduleEvent(
                        deadline_timestamp, event.task, SchedEvent.EventType.deadline.value)
                    deadline_event.job = event.job
                    self.deadline_events.append(deadline_event)
            elif event.timestamp == time and self.cores[int(event.processor)].executing:
                event.timestamp += (self.cores[int(event.processor)].executing.timestamp + self.cores[int(event.processor)].executing.task.wcet - event.timestamp)
            if event.timestamp > time:
                helper_list.append(event)
        self.start_events = helper_list


class Preemptive(Scheduler):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'GenericPreemptiveScheduler'

    def execute(self):
        pass

    def find_finish_events(self, time):
        for p in self.cores:
            if p.executing:
                if p.executing.executing_time == p.executing.task.wcet:
                    # Create finish event:
                    finish_event = SchedEvent.ScheduleEvent(
                        time, p.executing.task, SchedEvent.EventType.finish.value)
                    finish_event.job = p.executing.job
                    self.output_file.add_scheduler_event(finish_event)
                    # Delete from start_events:
                    self.start_events.remove(p.executing)
                    # Free execute:
                    p.executing = None

    def create_deadline_event(self, event):
        if event.task.real_time:
            deadline_timestamp = event.timestamp + event.task.deadline
            deadline_event = SchedEvent.ScheduleEvent(
                deadline_timestamp, event.task, SchedEvent.EventType.deadline.value)
            deadline_event.job = event.job
            self.deadline_events.append(deadline_event)
            event.task.first_time_executing = False


class FIFO(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'FIFO'

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.find_start_events(time)
            time += 1

        self.output_file.terminate_write()


class SJF(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'SJF'

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            # Sort by wcet:
            self.start_events.sort(key=lambda x: x.task.wcet)
            self.find_start_events(time)
            time += 1

        self.output_file.terminate_write()


class HRRN(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'HRRN'

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.calculate_responsive_ratio(time)
            # Sort by response ratio:
            self.start_events.sort(key=lambda x: x.response_ratio, reverse=True)
            self.find_start_events(time)
            time += 1

    def calculate_responsive_ratio(self, time):
        for event in self.start_events:
            if event.init <= time:
                w = time - event.init
                c = event.task.wcet
                event.response_ratio = (w + c)/c


class SRTF(Preemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'ShortestRemainingTimeFirst'

    def calculate_remaining_time(self):
        for event in self.start_events:
            event.remaining_time = event.task.wcet - event.executing_time

    def choose_executed(self, time):
        if len(self.start_events) > 0:
            self.start_events.sort(key=lambda x: x.remaining_time)
            # Non task is executed:
            for p in self.cores:
                if p.executing is None:
                    event = self.start_events[0]
                    event.timestamp = time
                    self.output_file.add_scheduler_event(event)
                    p.executing = event
                    # Create deadline event:
                    self.create_deadline_event(event)
                # Change of task:
                elif p.executing.remaining_time > self.start_events[0].remaining_time and \
                        p.executing != self.start_events[0]:
                    # Create finish event of the current task in execution:
                    finish_timestamp = time
                    finish_event = SchedEvent.ScheduleEvent(
                        finish_timestamp, p.executing.task, SchedEvent.EventType.finish.value)
                    finish_event.job = p.executing.job
                    self.output_file.add_scheduler_event(finish_event)
                    # Change task:
                    event = self.start_events[0]
                    event.timestamp = time
                    self.output_file.add_scheduler_event(event)
                    p.executing = event
                    # Create deadline event:
                    if event.task.first_time_executing:
                        self.create_deadline_event(event)

            '''print(f'EXECUTING {self.executing.task.id}:{self.executing.remaining_time}')
            print(f'BEST REM {self.start_events[0].task.id}:{self.start_events[0].remaining_time}')
            print(f'LEN STARTS {len(self.start_events)}')'''

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.calculate_remaining_time()
            self.choose_executed(time)
            for p in self.cores:
                if p.executing:
                    p.executing.executing_time += 1
            time += 1


class RoundRobin(Preemptive):

    def __init__(self, output_file, quantum):
        super().__init__(output_file)
        self.name = 'RoundRobin'
        self.quantum = int(quantum)
        self.quantum_counter = 0

    def choose_executed(self, time):
        if len(self.start_events) > 0:
            # Non task is executed:
            for p in self.cores:
                if p.executing is None:
                    event = self.start_events[0]
                    event.timestamp = time
                    self.output_file.add_scheduler_event(event)
                    p.executing = event
                    # Create deadline event:
                    self.create_deadline_event(event)
                    # Restart quantum counter
                    self.quantum_counter = 0
                # Change of task:
                elif self.quantum_counter == self.quantum:
                    # Create finish event of the current task in execution:
                    finish_timestamp = time
                    finish_event = SchedEvent.ScheduleEvent(
                        finish_timestamp, p.executing.task, SchedEvent.EventType.finish.value)
                    finish_event.job = p.executing.job
                    self.output_file.add_scheduler_event(finish_event)
                    # Change task:
                    # 1) Delete from start_events:
                    del self.start_events[0]
                    # 2) Add this event to the final:
                    self.start_events.append(p.executing)
                    # 3) New event:
                    event = self.start_events[0]
                    event.timestamp = time
                    self.output_file.add_scheduler_event(event)
                    p.executing = event
                    # Create deadline event:
                    if event.task.first_time_executing:
                        self.create_deadline_event(event)
                    # Restart counter
                    self.quantum_counter = 0

    def execute(self):
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.choose_executed(time)
            self.quantum_counter += 1
            for p in self.cores:
                if p.executing:
                    p.executing.executing_time += 1
            time += 1


class EDF(Preemptive):

    def __init__(self, output_file):
        super().__init__(output_file)

    def execute(self):
        a = 1


# Multiprocessor Scheduler

class PEDF(NonPreemptive):

    def __init__(self, output_file):
        super().__init__(output_file)
        self.name = 'PEDF'

    def execute(self):
        # temporarily fifo sched just to test, then we have to call EDF
        self.arrival_events = self.get_all_arrivals()

        time = self.start
        while time <= self.end:
            self.find_finish_events(time)
            self.find_deadline_events(time)
            self.find_arrival_event(time)
            self.find_start_events(time)
            time += 1

        self.output_file.terminate_write()






class GEDF(Preemptive):

    def __init__(self, output_file):
        super().__init__(output_file)

    def execute(self):
        c = 1


'''
XML be like:

<task real-time="true" type="periodic" id="1" period="10" deadline="50"  wcet="5" priority="1" />

Priority goes from 1 to 5 (1 high 5 low)

'''
