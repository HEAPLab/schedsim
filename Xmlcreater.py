import xml.etree.ElementTree as ET
import Task
import Taskgenerator
import sys
import random



tree = ET.parse("test.xml")
root = tree.getroot()

print(root[2][0][0].attrib)

if root.tag == 'simulation':
    if root[1].tag == 'software':
        taskgen = root[1][0]
        if taskgen.tag == 'taskgenerator':
            print(taskgen.attrib)
            algortihm = taskgen.attrib['algorithm']
            utilization = float(taskgen.attrib['utilization'])
            nr_tasks = int(taskgen.attrib['nr_tasks'])

            elem = ET.SubElement(root[1], 'tasks')

            # UUniFast algorithm
            sumU = utilization
            print(sumU)
            for i in range(1,nr_tasks):
                nextSumU = sumU * random.random()**(1/(nr_tasks-i))
                ET.SubElement(elem, 'task', realtime='true', type='sporadic', id =str(i), activation=str(sumU -nextSumU), wcet='50')
                add = sumU - nextSumU
                nextSumU = sumU
            ET.SubElement(elem, 'task', realtime='true', type='sporadic', id =str(i), activation=str(sumU), wcet ='50' )
            root[1].remove(taskgen)
    
           

tree.write('test_output.xml')
