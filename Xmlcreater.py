import xml.etree.ElementTree as ET
import random
import sys


def UUniFast(n, u):
    vectu =[]
    sumU = u
    for i in range(0,n-1):
        nextSumU = sumU * random.random()**(1/(n-(i+1)))
        vectu.append(sumU - nextSumU)  
        sumU=nextSumU

    vectu.append(sumU)
    return vectu


if len(sys.argv)==3:
    input = sys.argv[1]
    output = sys.argv[2]
else:
    raise Exception('Insufficient arguments. The name of the input and output files are required')

tree = ET.parse(input)
root = tree.getroot()



if root.tag == 'simulation':
    if root[0].tag =='time':
        time_start = int(root[0].attrib['start'])
        time_end = int(root[0].attrib['end'])
        total_time = time_end-time_start
    if root[1].tag == 'software':
        taskgen = root[1][0]
        scheduler = root[1][1]
        if taskgen.tag == 'taskgenerator':
            algortihm = taskgen.attrib['algorithm']
            utilization = float(taskgen.attrib['utilization'])
            nr_tasks = int(taskgen.attrib['nr_tasks'])

            schedulerType = scheduler.attrib['algorithm']

            root[1].remove(scheduler)

            elem = ET.SubElement(root[1], 'tasks')
            ET.SubElement(root[1], 'scheduler', algorithm = schedulerType)

            # UUniFast algorithm
            vec=[]
            vec = UUniFast(nr_tasks,utilization)
            for j in range (0, nr_tasks):
                ET.SubElement(elem, 'task', realtime='false', type='sporadic', id =str(j+1), activation='0', wcet = str(int(vec[j]*total_time+time_start)), dependencies = '0')
            root[1].remove(taskgen)
            
ET.indent(tree, space="\t", level=0)
tree.write(output, encoding="utf-8")    

