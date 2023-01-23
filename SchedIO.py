import xml.etree.ElementTree as ET
import Task
import Scheduler
import Cpu


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
                    elif count_scheduler > 1:
                        raise Exception(
                            'more than one scheduler is defined in the file')
            if count_scheduler == 0:
                raise Exception(
                            'non scheduler is defined in the file')

        if root_node[1].tag == 'software':
            if scheduler:
                task_root = root_node[1].find('tasks')
                count_task = 0
                for task_leaf in task_root:
                    _real_time = False
                    if (task_leaf.attrib['realtime'] == 'true') :
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
                    if (task_leaf.attrib['realtime'] == 'true'):
                        _deadline = int(task_leaf.attrib['deadline'])

                    if _id < 0 or _wcet <= 0 or _period <= 0 and (_deadline <= 0 and not _deadline == -1):
                        raise Exception(
                            'non positive values are saved in the file')
                    if (_wcet > _period != -1) or (_deadline != -1 and _deadline < _wcet):
                        raise Exception(
                            'inconsistent values saved in the file')

                    task = Task.Task(_real_time, _type, _id, _period, _activation, _deadline, _wcet)
                    scheduler.tasks.append(task)
                    count_task += 1
                if count_task == 0:
                    raise Exception(
                        'non task recognized in the file')
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


import csv





# This class was based on SchedSim v1:
# https://github.com/HEAPLab/schedsim/blob/master/SchedIo.py
class SchedulerEventWriter:

    def __init__(self, output_file):
        self.out = open(output_file, 'w+')

    def add_scheduler_event(self, scheduler_event):
        self.out.write(
            str(scheduler_event.timestamp) + ',' + str(scheduler_event.task.id) + ',' +
            str(scheduler_event.job) + ',' + str(scheduler_event.processor) + ',' +
            str(scheduler_event.type) + ',' + str(scheduler_event.extra) +'\n')
            

    def terminate_write(self):
        self.out.seek(0)
        task_started = 0
        task_finished = 0
        task_Missed = 0
        task_Activation = 0
        task_Deadline = 0
        time_final = 0
        time_initial = 0
        time_start = []
        time_finish = []
        time_deadline = []
        time_arrival =[]
        aux_list = []
        

        line = self.out.readline()
        vec = str(line).split(",")
        time_initial = int(vec[0])
        slack_time = 0

        while line:
            vec = str(line).split(",")
            if vec[4] == 'S':
                time_start.append([int(vec[0]), str(vec[1]+','+vec[2]) ])
                task_started +=1
            elif vec[4] == 'F':
                time_finish.append([int(vec[0]), str(vec[1]+','+vec[2]) ])
                task_finished +=1
            elif vec[4] == 'M':
                task_Missed +=1
            elif vec[4] == 'A':
                time_arrival.append([int(vec[0]), str(vec[1]+','+vec[2]) ])
                task_Activation +=1
            elif vec[4] == 'D':
                time_deadline.append([int(vec[0]), str(vec[1]+','+vec[2]) ])
                task_Deadline +=1

            line = self.out.readline()

        time_final = int(vec[0])
        run_time = 0

        #execution time - in these one they have the same corresponding location, because for one start we need one finish, less in the last one
        max_exec = 0
        min_exec = time_final +1
        for i in range(0, len(time_finish)):
            aux = (time_finish[i][0] - time_start[i][0])
            run_time += aux
            if (aux > max_exec):
                max_exec = aux
            if (aux < min_exec):
                min_exec = aux


        run_time += time_final - time_start[len(time_start)-1][0]


        #slack Time
        min_slack = time_final +1
        max_slac = 0
        for i in range(0, len(time_deadline)):
            for j in range(0, len(time_finish)):
                if(time_deadline[i][1] == time_finish[j][1]):
                    aux = (time_deadline[i][0] - time_finish[i][0])
                    slack_time = aux
                    if (aux > max_slac):
                        max_slac = aux
                    if (aux < min_slack):
                        min_slack = aux

        
        #Waiting Time
        min_wai =0
        max_wai = time_final +1
        wai_time = 0
        for i in range(0, len(time_start)):
            for j in range(0, len(time_arrival)):
                if(time_start[i][1] == time_arrival[j][1]):
                    aux = (time_start[i][0] - time_arrival[j][0])
                    wai_time += aux
                    if (aux > max_wai):
                        max_wai = aux
                    if (aux < min_wai):
                        min_wai = aux


        self.out.write("Actual System Runtime utilization= %.2f \n" % (run_time/(time_final-time_initial)) )

        self.out.write("Nr Activations= " + str(task_Activation)+'\n')
        self.out.write("Started Tasks= " + str(task_started)+'\n')
        self.out.write("Missed Deadline Tasks= " + str(task_Missed)+'\n')
        self.out.write("Max/Avg/Min Run time = %.2f %.2f %.2f \n" % (max_exec, (run_time/len(time_arrival)), min_exec))
        self.out.write("Max/Avg/Min Slack time = %.2f %.2f %.2f \n" % (max_slac, (slack_time/len(time_deadline)), min_slack))
        self.out.write("Max/Avg/Min Waiting time= %.2f %.2f %.2f \n" % (max_wai, (wai_time/len(time_deadline)), min_wai))
        
        self.out.close()
