# This Python file uses the following encoding: utf-8
import xml.etree.ElementTree as ET
import Task


def importFile(filePath, adderFun):
    root_node = ET.parse(filePath).getroot()
    if root_node.tag == 'simulation':
        if root_node[0].tag == 'software':
            task_root = root_node[0][0]
            tasks = []
            for task_leaf in task_root:
                id = int(task_leaf.attrib['id'])
                wcet = int(task_leaf.attrib['wcet'])
                period = int(task_leaf.attrib['period'])
                deadline = int(task_leaf.attrib['deadline'])
                if id < 0 or wcet <= 0 or period <= 0 and (deadline <= 0 and
                                                           not deadline == -1):
                    raise Exception(
                        'non positive values are saved in the file')
                if wcet > period or deadline != -1 and deadline < wcet:
                    raise Exception('inconstintent values saved in the file')
                adderFun(Task.Task(id, wcet, period, deadline))


def exportFile(tasks, fileName):
    simulationNode = ET.Element('simulation')
    softwareNode = ET.SubElement(simulationNode, 'software')
    tasksNode = ET.SubElement(softwareNode, 'tasks')
    for task in tasks:
        attributes = {
            'id': str(task.id),
            'period': str(task.period),
            'deadline': str(task.deadline),
            'wcet': str(task.wcet)
        }
        task = ET.SubElement(tasksNode, 'periodictask', attrib=attributes)
    tree = ET.ElementTree(simulationNode)
    tree.write(fileName)


class SchedEventWriter:
    def __init__(self):
        #self._buffer=[]
        filename='out.txt'
        self.out = open(filename, 'w')

    def addSchedEvent(self, schedEvent):
        self.out.write(
            str(schedEvent.timestamp) + ',' + str(schedEvent.task) + ',' +
            str(schedEvent.job) + ',' + str(schedEvent.processor) + ',' +
            str(schedEvent.type) + ',' + str(schedEvent.extra) + '\n')
    #   self._buffer.append(schedEvent)

    #def writeToFile(self):

    def terminateWrite(self):
        self.out.close()
