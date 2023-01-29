import xml.etree.ElementTree as ET
import Task
import Scheduler
import Cpu
import  numpy as np


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
                    _dependencies = -1
                    _wcet = int(task_leaf.attrib['wcet'])
                    if task_leaf.attrib['type'] == 'periodic':
                        _period = int(task_leaf.attrib['period'])
                    if task_leaf.attrib['type'] == 'sporadic':
                        _activation = int(task_leaf.attrib['activation'])
                    if (task_leaf.attrib['realtime'] == 'true'):
                        _deadline = int(task_leaf.attrib['deadline'])
                    if not (task_leaf.attrib['dependencies'] == 0):
                        _dependencies = int(task_leaf.attrib['dependencies'])

                    if _id < 0 or _wcet <= 0 or _period <= 0 and (_deadline <= 0 and not _deadline == -1):
                        raise Exception(
                            'non positive values are saved in the file')
                    if (_wcet > _period != -1) or (_deadline != -1 and _deadline < _wcet):
                        raise Exception(
                            'inconsistent values saved in the file')

                    task = Task.Task(_real_time, _type, _id, _period, _activation, _deadline, _wcet, _dependencies)
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
        

        line = self.out.readline()
        vec = str(line).split(",")
        time_initial = int(vec[0])
        number_tasks=0
        number_sub_tasks=0
    

        while line:
            vec = str(line).split(",")
            if (int(vec[1])> number_tasks):
                number_tasks=int(vec[1])
            if (int(vec[2])> number_sub_tasks):
                number_sub_tasks=int(vec[2])    
            line = self.out.readline()
        time_final = int(vec[0])
        run_time = 0


        task_started = [0]*number_tasks
        task_finished = [0]*number_tasks
        task_Missed = np.zeros((number_tasks, number_sub_tasks))
        task_Activation = [0]*number_tasks
        task_Deadline = [0]*number_tasks
        time_start = np.zeros((number_tasks, number_sub_tasks))
        time_finish = np.zeros((number_tasks, number_sub_tasks))
        time_deadline = np.zeros((number_tasks, number_sub_tasks))
        time_arrival = np.zeros((number_tasks, number_sub_tasks))

        print("ola\n")

        self.out.seek(0)
        line = self.out.readline()
        vec = str(line).split(",")
        time_initial = int(vec[0])
        while line:
            vec = str(line).split(",")
            index = int(vec[1]) - 1
            index2 = int(vec[2])-1
            if(index2 == -1):
                index2 =0
            if vec[4] == 'S':
                time_start[index][index2] = int(vec[0])
                task_started[index] +=1
            elif vec[4] == 'F':
                time_finish[index][index2] = int(vec[0])
                task_finished[index] +=1
            elif vec[4] == 'M':
                task_Missed[index][index2] = 1
            elif vec[4] == 'A':
                time_arrival[index][index2] = int(vec[0])
                task_Activation[index] +=1
            elif vec[4] == 'D':
                time_deadline[index][index2] = int(vec[0])
                task_Deadline[index] +=1
            line = self.out.readline()

        #execution time
        print(run_time)
        print("ola\n")
        for j in range(0, number_tasks):
            for i in range(0, number_sub_tasks):
                if(time_finish[j][i] != 0):
                    run_time += (time_finish[j][i] - time_start[j][i])
                elif(time_start[j][i] != 0 and task_Missed[j][i] != 1):
                    print(time_final - time_start[j][i])
                    run_time += time_final - time_start[j][i]

        """"
        #execution time tasks
        slack_time = [None] * number_tasks
        max_exec = 0
        min_exec = time_final +1
        for i in range(0, number_tasks):
            for j in range(0, len(time_finish)):
                if(time_deadline[i][1] == time_finish[j][1]):
                    aux = (time_deadline[i][0] - time_finish[i][0])
                    slack_time = aux
                    if (aux > max_slac):
                        max_slac = aux
                    if (aux < min_slack):
                        min_slack = aux

            run_time += (time_finish[i][0] - time_start[i][0])


        #slack Time
        min_slack = time_final +1
        max_slac = 0
        for i in range(0, len(time_deadline)):
            for j in range(0, len(time_finish)):
                if(time_deadline[i][1] == time_finish[j][1]):
                    aux = (time_deadline[i][0] - time_finish[i][0])
                    slack_time += aux
                    if (aux > max_slac):
                        max_slac = aux
                    if (aux < min_slack):
                        min_slack = aux

        
        #Waiting Time
        min_wai = time_final +1
        max_wai = 0
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

        """
        self.out.write("Actual System Runtime utilization= %.2f \n" % (run_time/(time_final-time_initial)) )
        """
        self.out.write("Nr Activations= " + str(task_Activation)+'\n')
        self.out.write("Started Tasks= " + str(task_started)+'\n')
        self.out.write("Missed Deadline Tasks= " + str(task_Missed)+'\n')
        if(len(time_arrival)>0):
            self.out.write("Max/Avg/Min Run time = %.2f %.2f %.2f \n" % (max_exec, (run_time/len(time_arrival)), min_exec))
        if(len(time_deadline)>0):
            self.out.write("Max/Avg/Min Slack time = %.2f %.2f %.2f \n" % (max_slac, (slack_time/len(time_deadline)), min_slack))
        if(len(time_start)>0):
            self.out.write("Max/Avg/Min Waiting time= %.2f %.2f %.2f \n" % (max_wai, (wai_time/len(time_start)), min_wai))
        """        
        self.out.close()
