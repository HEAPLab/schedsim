import xml.etree.ElementTree as ET
import Task
import Scheduler
import Cpu
from Noises import *


# The idea of this function was based on SchedSim v1:
# https://github.com/HEAPLab/schedsim/blob/master/SchedIo.py
def import_file(file_path, output_file):
    scheduler = None
    root_node = ET.parse(file_path).getroot()
    if root_node.tag == 'simulation':
        if root_node[1].tag == 'software':
            count_scheduler = 0
            for scheduler in root_node[1]:
                if scheduler.tag == 'scheduler':
                    count_scheduler += 1
                    if count_scheduler == 1:
                        _scheduler = scheduler
                        if _scheduler.attrib['algorithm'] == 'RR':
                            if 'quantum' in _scheduler.attrib:
                                quantum = _scheduler.attrib['quantum']
                                scheduler = Scheduler.RoundRobin(output_file, quantum)
                            else:
                                raise Exception(
                                    'non "quantum" attribute are defined in the file')
                        if _scheduler.attrib['algorithm'] == 'FIFO':
                            scheduler = Scheduler.FIFO(output_file)
                        if _scheduler.attrib['algorithm'] == 'SJF':
                            scheduler = Scheduler.SJF(output_file)
                        if _scheduler.attrib['algorithm'] == 'HRRN':
                            scheduler = Scheduler.HRRN(output_file)
                        if _scheduler.attrib['algorithm'] == 'SRTF':
                            scheduler = Scheduler.SRTF(output_file)

                        if _scheduler.attrib['algorithm'] == 'EDF':
                            scheduler = Scheduler.EDF(output_file)
                        # Multiprocessor scheduler
                        if _scheduler.attrib['algorithm'] == 'PEDF':
                            scheduler = Scheduler.PEDF(output_file)
                        if _scheduler.attrib['algorithm'] == 'PFP':
                            scheduler = Scheduler.PFP(output_file)

                    elif count_scheduler > 1:
                        raise Exception(
                            'more than one scheduler is defined in the file')
            if count_scheduler == 0:
                raise Exception(
                            'non scheduler is defined in the file')

        if root_node[1].tag == 'software':
            if scheduler:
                task_root = root_node[1][0]
                count_task = 0
                for task_leaf in task_root:
                    _real_time = False
                    if task_leaf.attrib['real-time'] == 'true':
                        _real_time = True
                    _type = task_leaf.attrib['type']
                    _id = int(task_leaf.attrib['id'])
                    _period = -1
                    _activation = -1
                    _deadline = -1
                    _wcet = int(task_leaf.attrib['wcet'])
                    if task_leaf.attrib['type'] == 'periodic':
                        _period = int(task_leaf.attrib['period'])
                    if task_leaf.attrib['type'] == 'sporadic':
                        _activation = int(task_leaf.attrib['activation'])
                    if task_leaf.attrib['real-time'] == 'true':
                        _deadline = int(task_leaf.attrib['deadline'])

                    if _id < 0 or _wcet <= 0 or _period <= 0 and (_deadline <= 0 and not _deadline == -1):
                        raise Exception(
                            'non positive values are saved in the file')
                    if (_wcet > _period != -1) or (_deadline != -1 and _deadline < _wcet):
                        raise Exception(
                            'inconsistent values saved in the file')
                    _noise = None

                    task = Task.Task(_real_time, _type, _id, _period, _activation, _deadline, _wcet)
                    scheduler.tasks.append(task)
                    count_task += 1
                if count_task == 0:
                    raise Exception(
                        'no tasks recognized in the file')
                noises_root = root_node[1][1]
                for noise_leaf in noises_root:
                    #Default to -1
                    assigned_task = -1

                    #This for each assigns the Noise to the correct task
                    for task in scheduler.tasks:
                        if (task.id == int(noise_leaf.attrib['task-id'])):
                            assigned_task = task.id
                            if(noise_leaf.attrib['type']=="gauss"):
                                noise_mean = int(noise_leaf.attrib['mean'])
                                noise_std = int(noise_leaf.attrib['std'])
                                task.noises.append(GaussianNoise(task.id, noise_mean, noise_std))
                            elif(noise_leaf.attrib['type']=="uniform"):
                                noise_low = int(noise_leaf.attrib['low_end'])
                                noise_high = int(noise_leaf.attrib['high_end'])
                                if(noise_high<noise_low):
                                    raise Exception(
                                'Uniform ends are not valid')
                                task.noises.append(UniformNoise(task.id, noise_low, noise_high))



                            else:
                                raise Exception(
                                'Noise type not recognized')
                    if assigned_task==-1:
                        raise Exception(
                            'A noise is not being assigned to a task')

            else:
                raise Exception(
                    'non scheduler recognized in the file')

        if root_node[0].tag == 'time':
            time = root_node[0].attrib
            scheduler.start = int(time['start'])
            scheduler.end = int(time['end'])

        if root_node[2].tag == 'hardware':
            core_root = root_node[2][0]
            count_cores = 0
            for core_leaf in core_root:
                _id = core_leaf.attrib['id']
                core = Cpu.Core(_id)
                if core_leaf.attrib['speed']:
                    core.speed = core_leaf.attrib['speed']
                scheduler.cores.append(core)
                count_cores += 1

            if count_cores == 0:
                raise Exception(
                    'non cores recognized in the file')

    return scheduler


# This class was based on SchedSim v1:
# https://github.com/HEAPLab/schedsim/blob/master/SchedIo.py
class SchedulerEventWriter:
    def __init__(self, output_file):
        self.out = open(output_file, 'w')

    def add_scheduler_event(self, scheduler_event):
        self.out.write(
            str(scheduler_event.timestamp) + ',' + str(scheduler_event.task.id) + ',' +
            str(scheduler_event.job) + ',' + str(scheduler_event.processor) + ',' +
            str(scheduler_event.type) + ',' + str(scheduler_event.extra) + ',' + '\n')
            # + str(scheduler_event.task.priority)

    def terminate_write(self):
        self.out.close()
