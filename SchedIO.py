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
                        _dependencies = (task_leaf.attrib['dependencies'])

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
            

    def terminate_write(self, time_final, time_initial):
        self.out.seek(0)
        line = self.out.readline()
        vec = str(line).split(",")
        number_tasks=0
        number_sub_tasks=0
    

        while line:
            vec = str(line).split(",")
            if (int(vec[1])> number_tasks):
                number_tasks=int(vec[1])
            if (int(vec[2])> number_sub_tasks):
                number_sub_tasks=int(vec[2])    
            line = self.out.readline()
        run_time = 0

        if(number_sub_tasks==0):
            number_sub_tasks=1
        task_started = [0]*number_tasks
        task_finished = [0]*number_tasks
        task_Missed = np.zeros((number_tasks, number_sub_tasks))
        task_Activation = [0]*number_tasks
        task_Deadline = [0]*number_tasks
        time_start = np.zeros((number_tasks, number_sub_tasks))
        time_finish = np.zeros((number_tasks, number_sub_tasks))
        time_deadline = np.zeros((number_tasks, number_sub_tasks))
        time_arrival = np.zeros((number_tasks, number_sub_tasks))


        self.out.seek(0)
        line = self.out.readline()
        vec = str(line).split(",")
        while line:
            vec = str(line).split(",")
            index = int(vec[1]) - 1
            index2 = int(vec[2]) - 1
            if index2 == -1:
                index2=0
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
        for j in range(0, number_tasks):
            for i in range(0, number_sub_tasks):
                if(time_finish[j][i] != 0):
                    run_time += (time_finish[j][i] - time_start[j][i])
                elif(time_start[j][i] != 0 and task_Missed[j][i] != 1):
                    run_time += time_final - time_start[j][i]

        print("Actual System Runtime utilization= %.2f \n" % (run_time/(time_final-time_initial)) )

        for j in range(0, number_tasks):

            
            

            print("Nr Activations Task %d = %d\n" % (j+1,task_Activation[j]))
            print("Deadline Misses Task %d = %d\n" % (j+1, np.count_nonzero(task_Missed[j])))


            exec_time_task = 0
            max_exec = 0
            min_exec = time_final +1
            for i in range(0, number_sub_tasks):
                if(time_finish[j][i]!=0):
                    aux = (time_finish[j][i] - time_start[j][i])
                    exec_time_task += aux
                    if (aux > max_exec):
                        max_exec = aux
                    if (aux < min_exec):
                        min_exec = aux
                elif(time_start[j][i] != 0 and task_Missed[j][i] != 1):
                    aux = (time_final - time_start[j][i])
                    exec_time_task += aux
                    if (aux > max_exec):
                        max_exec = aux
                    if (aux < min_exec):
                        min_exec = aux

            

            if(task_started[j]>0):
                avg_runtime = (exec_time_task/task_started[j])
                print("Max/Avg/Min Run time Task % d = %.2f %.2f %.2f \n" % (j+1, max_exec, avg_runtime, min_exec))


            
            #slack Time
            slack_time = 0
            min_slack = time_final +1
            max_slac = 0
            for i in range(0, number_sub_tasks):
                if(time_deadline[j][i] != 0):
                    aux = (time_deadline[j][i] - time_finish[j][i])
                    slack_time += aux
                    if (aux > max_slac):
                        max_slac = aux
                    if (aux < min_slack):
                        min_slack = aux

            if(task_Deadline[j]>0):
                avg_slac = (slack_time/task_Deadline[j])
                print("Max/Avg/Min Slack time Task %d = %.2f %.2f %.2f \n" % (j+1,max_slac, avg_slac, min_slack))

            
            #Waiting Time
            min_wai = time_final +1
            max_wai = 0
            wai_time = 0
            for i in range(0, number_sub_tasks):
                if(time_start[j][i] != 0 or time_finish[j][i] !=0):
                    aux = (time_start[j][i] - time_arrival[j][i])
                    wai_time += aux
                    if (aux > max_wai):
                        max_wai = aux
                    if (aux < min_wai):
                        min_wai = aux

            
            if(task_started[j]>0):
                avg_waiting = (wai_time/task_started[j])
                print("Max/Avg/Min Waiting time Task %d= %.2f %.2f %.2f \n" % (j+1,max_wai, avg_waiting, min_wai))
                    
        self.out.close()
