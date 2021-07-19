<h1>SchedSim</h1>
<h3>By HeapLab</h3>
<p>This application is a real time schedulers simulator developed using Pythonand PyQt for the GUI.<br>Given  a  set  of  tasks,  which  can  be  defined  in  the  program  and  can  beimported/exported as XML, SchedSim provides as output a list of temporally ordered events, in CSV format, ready to be displayed in a temporal chart.</p>
<p>This tool can be useful for simulating new types of schedulers (for research purposes for example) and, subsequently, visualize the results starting from the ”event list” output file by means of an external application.</p>
<p>SchedSim provides a simple interface (abstract class) which can be implemented to allow user to include his/her own scheduling algorythm.  DeadlineMonotonic algorythm is built-in and provided as a working example.</p>
<p>For further information, design details and UML diagrams please look at the following document (/docs/SchedSim.pdf):</p>

<object data="../../raw/master/docs/SchedSim.pdf" type="application/pdf" width="700px" height="700px">
    <embed src="../../raw/master/docs/SchedSim.pdf">
        <p>This browser does not support PDFs. Please download the PDF to view it: <a href="../../raw/master/docs/SchedSim.pdf">Download PDF</a>.</p>
    </embed>
</object>
